"""
最终RG爬虫 - 正确识别子分类
先找到所有子分类标题的位置，然后根据链接位置判断子分类
"""
import requests
from bs4 import BeautifulSoup
import re
from models import db, Gunpla
from app import app
import sys
import importlib.util

# 导入基础爬虫类
spec = importlib.util.spec_from_file_location("scraper78dm", "78dm_scraper.py")
scraper78dm_module = importlib.util.module_from_spec(spec)
sys.modules["scraper78dm"] = scraper78dm_module
spec.loader.exec_module(scraper78dm_module)
Scraper78DM = scraper78dm_module.Scraper78DM

def scrape_rg_final():
    """
    最终版本：正确识别子分类
    """
    scraper = Scraper78DM()
    
    # RG系列URL
    rg_url = 'https://acg.78dm.net/ct/341672.html'
    
    print("=" * 60)
    print("完善RG数据库 - 最终版本（正确识别子分类）")
    print("=" * 60)
    print(f"URL: {rg_url}\n")
    
    try:
        response = scraper.session.get(rg_url, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        gunpla_list = []
        
        # 方法：按顺序遍历所有元素，遇到子分类标题时切换，遇到模型链接时记录
        # 获取页面中所有元素（按顺序）
        all_elements = soup.find_all(True)  # 获取所有标签
        
        current_subcategory = '普通版'
        
        # 查找所有模型链接和子分类标题
        links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))
        
        print(f"找到 {len(links)} 个链接，正在处理...")
        
        # 获取页面文本，用于查找子分类标题的位置
        page_text = soup.get_text()
        
        # 找到所有子分类标题的位置
        subcategory_markers = []
        patterns = [
            (r'普通版共\d+款', '普通版'),
            (r'网络限定版共\d+款', '网络限定版'),
            (r'其他限定版共\d+款', '其他限定版'),
            (r'EVANGELION系列共\d+款', 'EVANGELION系列'),
            (r'勇者王系列共\d+款', '勇者王系列'),
            (r'参考出品/开发中商品共\d+款', '参考出品/开发中'),
        ]
        
        for pattern, subcat in patterns:
            for match in re.finditer(pattern, page_text):
                subcategory_markers.append((match.start(), subcat))
        
        # 按位置排序
        subcategory_markers.sort()
        print(f"\n找到 {len(subcategory_markers)} 个子分类标记：")
        for pos, subcat in subcategory_markers:
            print(f"  位置 {pos}: {subcat}")
        
        # 处理每个链接
        for link in links:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            
            # 过滤无效链接
            if not name or len(name) < 2:
                continue
            
            # 跳过导航链接
            skip_keywords = ['更多', '显示', '隐藏', '加载', '级别分类详情']
            if any(keyword in name for keyword in skip_keywords):
                continue
            
            # 找到链接在页面中的位置
            link_pos = page_text.find(name)
            
            # 确定链接属于哪个子分类（找到最近的子分类标记之前的位置）
            link_subcategory = '普通版'  # 默认
            for pos, subcat in subcategory_markers:
                if link_pos > pos:
                    link_subcategory = subcat
                else:
                    break
            
            # 构建完整URL
            if href.startswith('/'):
                full_url = scraper.base_url + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # 提取基本信息
            data = {
                'name_cn': name,
                'grade': 'RG',
                'url': full_url,
                'subcategory': link_subcategory,
            }
            
            # 尝试从名称中提取编号
            ms_number = scraper.extract_model_number(name)
            if ms_number:
                data['ms_number'] = ms_number
            
            gunpla_list.append(data)
        
        # 去重（基于名称）
        seen = set()
        unique_list = []
        for item in gunpla_list:
            name_key = item['name_cn']
            if name_key not in seen:
                seen.add(name_key)
                unique_list.append(item)
        
        # 统计子分类
        subcategory_count = {}
        for item in unique_list:
            subcat = item.get('subcategory', '未知')
            subcategory_count[subcat] = subcategory_count.get(subcat, 0) + 1
        
        print(f"\n找到 {len(unique_list)} 个模型\n")
        print("子分类统计：")
        for subcat, count in sorted(subcategory_count.items()):
            print(f"  {subcat}: {count} 个")
        
        # 保存到数据库
        print(f"\n保存数据到数据库...")
        with app.app_context():
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            
            for data in unique_list:
                try:
                    name = data.get('name_cn', '').strip()
                    if not name:
                        continue
                    
                    # 检查是否已存在
                    existing = Gunpla.query.filter_by(
                        name_cn=name,
                        grade='RG'
                    ).first()
                    
                    if existing:
                        # 强制更新子分类和编号
                        updated = False
                        if data.get('subcategory'):
                            existing.subcategory = data.get('subcategory')
                            updated = True
                        if data.get('ms_number') and not existing.ms_number:
                            existing.ms_number = data.get('ms_number')
                            updated = True
                        
                        if updated:
                            db.session.commit()
                            updated_count += 1
                        else:
                            skipped_count += 1
                        continue
                    
                    # 创建新记录
                    gunpla = Gunpla(
                        name_cn=name,
                        grade='RG',
                        ms_number=data.get('ms_number'),
                        subcategory=data.get('subcategory'),
                        series='RG系列拼装模型',
                    )
                    
                    db.session.add(gunpla)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存失败: {name} - {e}")
                    db.session.rollback()
                    continue
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("保存完成！")
            print(f"新增: {saved_count} 条")
            print(f"更新: {updated_count} 条")
            print(f"跳过（已存在）: {skipped_count} 条")
            print("=" * 60)
            print("\n说明：")
            print("- 价格信息暂时不爬取（价格爬取逻辑需要改进）")
            print("- 可以在网页应用中手动补充价格")
            
    except Exception as e:
        print(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    scrape_rg_final()
