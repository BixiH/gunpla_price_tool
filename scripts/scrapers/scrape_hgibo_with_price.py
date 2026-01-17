"""
HGIBO（铁血）系列价格爬虫
爬取HGIBO系列的所有模型和价格信息
"""
import sys
import os
import time
import re
import importlib.util

# 动态导入78dm_scraper模块（因为模块名以数字开头）
spec = importlib.util.spec_from_file_location("scraper_78dm", "78dm_scraper.py")
scraper_module = importlib.util.module_from_spec(spec)
sys.modules["scraper_78dm"] = scraper_module
spec.loader.exec_module(scraper_module)

from scraper_78dm import Scraper78DM
from bs4 import BeautifulSoup
from app import app
from models import db, Gunpla

def scrape_price_improved(url):
    """
    改进的价格爬取函数
    尝试多种方法提取价格
    """
    scraper = Scraper78DM()
    price_data = {}
    
    try:
        response = scraper.session.get(url, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 方法1：查找表格中的价格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    # 查找包含"定价"、"价格"、"日元"的行
                    if '定价' in text or '价格' in text or '日元' in text:
                        # 查找同一行或下一行的数字
                        for next_cell in cells[i+1:]:
                            price_text = next_cell.get_text(strip=True)
                            match = re.search(r'(\d+)', price_text.replace(',', ''))
                            if match:
                                price = float(match.group(1))
                                if 100 <= price <= 50000:  # HGIBO价格范围
                                    if not price_data.get('price_jp_msrp'):
                                        price_data['price_jp_msrp'] = price
                                        break
        
        # 方法2：在页面文本中搜索价格模式
        page_text = soup.get_text()
        price_patterns = [
            r'定价[：:]\s*[¥￥]?\s*(\d+)',
            r'价格[：:]\s*[¥￥]?\s*(\d+)',
            r'[¥￥]\s*(\d+)\s*日元',
            r'(\d+)\s*日元',
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, page_text)
            for match in matches:
                price = float(match.group(1))
                if 100 <= price <= 50000:  # HGIBO价格范围
                    if not price_data.get('price_jp_msrp'):
                        price_data['price_jp_msrp'] = price
                        break
            if price_data.get('price_jp_msrp'):
                break
        
        # 方法3：查找包含"价格"的div或span
        price_elements = soup.find_all(['div', 'span', 'p'], string=re.compile(r'.*\d+.*日元'))
        for elem in price_elements:
            text = elem.get_text(strip=True)
            match = re.search(r'(\d+)', text.replace(',', ''))
            if match:
                price = float(match.group(1))
                if 100 <= price <= 50000:  # HGIBO价格范围
                    if not price_data.get('price_jp_msrp'):
                        price_data['price_jp_msrp'] = price
                        break
        
        return price_data
        
    except Exception as e:
        print(f"    价格爬取失败: {e}")
        return {}

def scrape_hgibo_with_price(include_price=True):
    """
    完善HGIBO数据库，包含价格信息
    只爬取HG 1/144部分，TV 1/100部分属于FM系列
    """
    scraper = Scraper78DM()
    
    # HGIBO系列URL
    hgibo_url = 'https://acg.78dm.net/ct/92653.html'
    
    print("=" * 60)
    print("完善HGIBO数据库 - 包含价格信息")
    print("=" * 60)
    print(f"URL: {hgibo_url}\n")
    print("注意：只爬取HG 1/144部分，TV 1/100部分属于FM系列\n")
    
    try:
        response = scraper.session.get(hgibo_url, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        gunpla_list = []
        
        # 查找所有模型链接
        links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))
        
        print(f"找到 {len(links)} 个链接，正在处理...")
        
        # 获取页面文本，用于查找子分类
        page_text = soup.get_text()
        
        # 找到所有子分类标题的位置（只关注HG 1/144部分）
        subcategory_markers = []
        patterns = [
            (r'HG 1/144 普通版共\d+款', '普通版'),
            (r'HG 1/144 网络限定版共\d+款', '网络限定版'),
            (r'HG 1/144 其他限定版共\d+款', '其他限定版'),
        ]
        
        for pattern, subcat in patterns:
            for match in re.finditer(pattern, page_text):
                subcategory_markers.append((match.start(), subcat))
        
        subcategory_markers.sort()
        
        # 非HGIBO级别的关键词（这些是其他级别，不是HGIBO产品）
        non_hgibo_grades = ['RG', 'PG', 'MG', 'RE/100', 'HGUC', 'HGGTO', 'HGBF', 'HGBD', 'HGBF/BD', 'SDCS', '30MM', 'FM',
                           'MB', 'MR魂', 'FIX', 'R魂', 'GU', 'FW食玩', 'G-FRAME', 'MSE',
                           '万代机甲', '万代人形', '超合金魂', 'BEASTBOX', 'MEGABOX',
                           '骨装机兵', '骨装机兵 FA', 'FA', 'FAG', '女神装置', 'MODEROID', '千值练', '海洋堂',
                           'threezero', 'threezero美系', 'Hot Toys', '麦克法兰', 'Sideshow', 'NECA', 'MEDICOM',
                           'MEDICOM奇迹可动', 'Mezco', '田宫', '小号手', '威龙', 'MENG', '爱德美', '长谷川',
                           '青岛社', '威骏', '红星']
        
        # 其他品类关键词（这些是其他产品类别，不是HGIBO产品）
        other_categories = [
            # 变形金刚及其子系列
            '变形金刚', 'SS系列', '大黄蜂美版', '变5美版', '日经', 'MP日版', 'G系列', 
            '王国', '地出', 'TFP美版', 'G1', '铁机巧', 'DLX',
            # 特摄周边及其子系列
            '特摄周边', 'S.H.Figuarts', 'DX假面骑士', 'S.I.C', 'RAH', 'X-PLUS', 
            'S.H.M', '假面骑士大集结', '掌动SHODO',
            # 潮流玩具及其子系列
            '潮流玩具', '52TOYS', 'POP MART', '末匠', '19八3', '奇谭俱乐部', 
            '撕裂熊', 'tokidoki', '豆芽水产',
            # 其他品类
            '科幻机甲', '美系周边', '军模民用'
        ]
        
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
            
            # 跳过TV 1/100部分（这些属于FM系列）
            if 'TV 1/100' in name or 'CHARA STAND PLATE' in name:
                continue
            
            # 过滤非HGIBO产品（这些是其他级别，不是HGIBO系列的产品）
            name_stripped = name.strip()
            if name_stripped in non_hgibo_grades:
                continue
            
            # 检查是否是其他级别的导航链接（包含"共X款"的级别名称）
            if any(grade in name and ('共' in name or '款' in name) for grade in non_hgibo_grades):
                continue
            
            # 过滤其他品类
            if name_stripped in other_categories:
                continue
            
            # 检查是否是其他品类的导航链接
            if any(category in name and ('共' in name or '款' in name) for category in other_categories):
                continue
            
            # 确定子分类（只处理HG 1/144部分）
            link_pos = page_text.find(name)
            link_subcategory = '普通版'  # 默认
            for pos, subcat in subcategory_markers:
                if link_pos > pos:
                    link_subcategory = subcat
                else:
                    break
            
            # 构建完整URL
            if href.startswith('/'):
                # 确保href不以//开头，避免URL拼接错误
                if href.startswith('//'):
                    full_url = 'https:' + href
                else:
                    full_url = 'https://acg.78dm.net' + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # 提取基本信息
            data = {
                'name_cn': name,
                'grade': 'HGIBO',
                'url': full_url,
                'subcategory': link_subcategory,
            }
            
            # 提取编号
            ms_number = scraper.extract_model_number(name)
            if ms_number:
                data['ms_number'] = ms_number
            
            gunpla_list.append(data)
        
        # 去重
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
        
        print(f"\n找到 {len(unique_list)} 个HGIBO模型")
        print("\n子分类统计：")
        for subcat, count in sorted(subcategory_count.items()):
            print(f"  {subcat}: {count} 个")
        
        # 爬取价格信息
        if include_price:
            print(f"\n开始爬取价格信息...")
            print(f"预计需要 {len(unique_list) * 1.5 / 60:.1f} 分钟\n")
            
            price_found = 0
            price_failed = 0
            
            for i, item in enumerate(unique_list, 1):
                if item.get('url'):
                    print(f"[{i}/{len(unique_list)}] {item['name_cn']}")
                    
                    # 爬取价格
                    price_data = scrape_price_improved(item['url'])
                    
                    if price_data.get('price_jp_msrp'):
                        item['price_jp_msrp'] = price_data['price_jp_msrp']
                        
                        # 换算为美元和人民币定价
                        converted = scraper.convert_price(price_data['price_jp_msrp'])
                        item.update(converted)
                        
                        print(f"  价格: ¥{item['price_jp_msrp']:.0f} (JPY) → ${item.get('price_us_msrp', 0):.2f} (USD) / ¥{item.get('price_cn_msrp', 0):.2f} (CNY)")
                        price_found += 1
                    else:
                        print(f"  未找到价格信息（但仍会录入）")
                        price_failed += 1
                    
                    # 延迟
                    if i < len(unique_list):
                        time.sleep(1.5)
            
            print(f"\n价格爬取统计：")
            print(f"  找到价格: {price_found} 个")
            print(f"  未找到价格: {price_failed} 个")
            print(f"  最终将录入: {len(unique_list)} 个模型")
        
        # 保存到数据库
        print(f"\n保存数据到数据库...")
        with app.app_context():
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            
            for data in unique_list:
                try:
                    name = data['name_cn']
                    
                    # 检查是否已存在
                    existing = Gunpla.query.filter_by(
                        name_cn=name,
                        grade='HGIBO'
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        if data.get('ms_number'):
                            existing.ms_number = data['ms_number']
                        if data.get('subcategory'):
                            existing.subcategory = data['subcategory']
                        if data.get('url'):
                            # 可以更新URL，但通常不需要
                            pass
                        
                        # 更新价格（如果提供了新价格）
                        if data.get('price_jp_msrp'):
                            existing.price_jp_msrp = data['price_jp_msrp']
                        if data.get('price_us_msrp'):
                            existing.price_us_msrp = data['price_us_msrp']
                        if data.get('price_cn_msrp'):
                            existing.price_cn_msrp = data['price_cn_msrp']
                        
                        db.session.commit()
                        updated_count += 1
                    else:
                        # 创建新记录
                        gunpla = Gunpla(
                            name_cn=name,
                            grade='HGIBO',
                            ms_number=data.get('ms_number'),
                            subcategory=data.get('subcategory'),
                            series='高达铁血的奥尔芬斯拼装模型',
                            price_jp_msrp=data.get('price_jp_msrp'),
                            price_us_msrp=data.get('price_us_msrp'),
                            price_cn_msrp=data.get('price_cn_msrp'),
                        )
                        
                        db.session.add(gunpla)
                        saved_count += 1
                        
                except Exception as e:
                    print(f"  保存失败 {data.get('name_cn', '未知')}: {e}")
                    skipped_count += 1
                    db.session.rollback()
            
            db.session.commit()
            
            print(f"\n保存完成！")
            print(f"  新增: {saved_count} 条")
            print(f"  更新: {updated_count} 条")
            if skipped_count > 0:
                print(f"  跳过: {skipped_count} 条")
        
    except Exception as e:
        print(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("开始爬取HGIBO系列数据...")
    scrape_hgibo_with_price(include_price=True)
    print("\n完成！")
