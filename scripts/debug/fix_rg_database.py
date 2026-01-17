"""
修复RG数据库 - 重新爬取RG系列列表，确保数据完整
"""
import requests
from bs4 import BeautifulSoup
import time
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

def scrape_rg_complete():
    """
    完整爬取RG系列 - 改进版本
    只爬取列表信息，不爬取价格（价格爬取有问题，后续改进）
    """
    scraper = Scraper78DM()
    
    # RG系列URL
    rg_url = 'https://acg.78dm.net/ct/341672.html'
    
    print("=" * 60)
    print("完善RG数据库 - 重新爬取列表信息")
    print("=" * 60)
    print(f"URL: {rg_url}\n")
    
    try:
        response = scraper.session.get(rg_url, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        gunpla_list = []
        
        # 查找所有模型链接
        links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))
        
        # 用于跟踪当前子分类
        current_subcategory = '普通版'  # 默认
        subcategory_sections = []  # 存储子分类标题位置
        
        # 先找到所有子分类标题的位置
        page_text = soup.get_text()
        all_text_elements = soup.find_all(['h3', 'h4', 'div', 'p', 'span'], string=re.compile(r'.*共\d+款'))
        
        # 获取所有包含子分类信息的元素
        for elem in soup.find_all(string=re.compile(r'(普通版|网络限定版|其他限定版|EVANGELION系列|勇者王系列|参考出品).*共\d+款')):
            parent = elem.parent if hasattr(elem, 'parent') else None
            if parent:
                subcategory_sections.append((parent, elem))
        
        print(f"找到 {len(subcategory_sections)} 个子分类标题")
        
        # 查找所有模型链接
        for link in links:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            
            # 过滤无效链接
            if not name or len(name) < 2:
                continue
            
            # 跳过明显的非模型链接
            skip_keywords = ['更多', '显示', '隐藏', '加载', '级别', '分类', '共', '款']
            if any(keyword in name for keyword in skip_keywords):
                # 检查是否是子分类标题
                if '普通版' in name and '共' in name:
                    current_subcategory = '普通版'
                    continue
                elif '网络限定版' in name and '共' in name:
                    current_subcategory = '网络限定版'
                    continue
                elif '其他限定版' in name and '共' in name:
                    current_subcategory = '其他限定版'
                    continue
                elif 'EVANGELION系列' in name or ('EVA' in name and '共' in name):
                    current_subcategory = 'EVANGELION系列'
                    continue
                elif '勇者王系列' in name and '共' in name:
                    current_subcategory = '勇者王系列'
                    continue
                elif '参考出品' in name or '开发中' in name:
                    current_subcategory = '参考出品/开发中'
                    continue
                else:
                    continue
            
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
                'subcategory': current_subcategory,
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
        
        print(f"找到 {len(unique_list)} 个模型\n")
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
                        # 更新子分类（如果原来没有）
                        if data.get('subcategory') and not existing.subcategory:
                            existing.subcategory = data.get('subcategory')
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
            
    except Exception as e:
        print(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    scrape_rg_complete()
