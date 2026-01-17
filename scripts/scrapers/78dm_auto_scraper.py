"""
78动漫自动爬虫 - 从主页开始，自动查找并爬取所有级别
"""
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import importlib.util
from models import db, Gunpla
from app import app

# 导入78dm_scraper模块（因为模块名以数字开头，需要使用特殊方法）
spec = importlib.util.spec_from_file_location("scraper78dm", "78dm_scraper.py")
scraper78dm_module = importlib.util.module_from_spec(spec)
sys.modules["scraper78dm"] = scraper78dm_module
spec.loader.exec_module(scraper78dm_module)
Scraper78DM = scraper78dm_module.Scraper78DM

class AutoScraper78DM(Scraper78DM):
    """自动爬虫类，继承自基础爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.78dm.net'
        self.acg_url = 'https://acg.78dm.net'  # 资料库使用acg子域名
    
    def find_grade_links(self):
        """
        从主页找到资料库，然后找到所有级别的链接
        
        返回:
            级别和URL的字典，例如：{'RG': 'https://acg.78dm.net/ct/341672.html', ...}
        """
        print("=" * 60)
        print("正在查找所有级别的链接...")
        print("=" * 60)
        
        grade_links = {}
        
        try:
            # 方法1：直接访问资料库页面
            # 78动漫的资料库通常在 acg.78dm.net
            database_url = 'https://acg.78dm.net'
            
            print(f"访问资料库: {database_url}")
            response = self.session.get(database_url, timeout=15)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找高达相关的级别链接
            # 常见的级别：PG, MG, RE/100, RG, HGUC, HGGTO, HGBF/BD, SDCS等
            
            # 方法1：查找包含级别名称的链接
            grade_names = {
                'PG': ['PG', 'pg'],
                'MG': ['MG', 'mg'],
                'RE/100': ['RE/100', 'RE100', 're/100'],
                'RG': ['RG', 'rg'],
                'HGUC': ['HGUC', 'hguc'],
                'HG': ['HG', 'hg'],
                'HGGTO': ['HGGTO', 'hggto'],
                'HGBF': ['HGBF', 'hgbf'],
                'SDCS': ['SDCS', 'sdcs'],
                'SD': ['SD', 'sd'],
                'EG': ['EG', 'eg'],
            }
            
            # 查找所有链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 检查是否是级别链接
                for grade, keywords in grade_names.items():
                    # 检查链接文本或href中是否包含级别关键词
                    if any(keyword in text or keyword in href for keyword in keywords):
                        # 构建完整URL
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = self.acg_url + href
                        elif href.startswith('ct/'):
                            full_url = self.acg_url + '/' + href
                        else:
                            continue
                        
                        # 检查URL是否是资料库页面（包含/ct/）
                        if '/ct/' in full_url and grade not in grade_links:
                            grade_links[grade] = full_url
                            print(f"找到 {grade} 级别: {full_url}")
            
            # 方法2：如果方法1没找到，使用已知的URL
            # 根据已知的RG URL格式
            if not grade_links:
                print("\n使用已知的URL格式...")
                # 已知RG的URL
                known_grades = {
                    'RG': '341672',
                    # 可以添加其他已知的ID
                }
                
                for grade, ct_id in known_grades.items():
                    url = f'https://acg.78dm.net/ct/{ct_id}.html'
                    grade_links[grade] = url
                    print(f"使用已知URL {grade}: {url}")
            else:
                # 如果找到了，但RG不在其中，使用已知的RG URL
                if 'RG' not in grade_links:
                    grade_links['RG'] = 'https://acg.78dm.net/ct/341672.html'
                    print(f"添加已知RG URL: {grade_links['RG']}")
            
            return grade_links
            
        except Exception as e:
            print(f"查找级别链接失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def scrape_all_grades(self, grades_to_scrape=None, include_price=True, delay=1.5):
        """
        爬取所有级别
        
        参数:
            grades_to_scrape: 要爬取的级别列表，如果为None则爬取所有找到的级别
            include_price: 是否爬取价格信息
            delay: 每个请求之间的延迟（秒）
        """
        print("\n" + "=" * 60)
        print("78动漫自动爬虫 - 爬取所有级别")
        print("=" * 60)
        
        # 查找所有级别的链接
        grade_links = self.find_grade_links()
        
        if not grade_links:
            print("\n未找到任何级别的链接！")
            print("请检查网络连接或网站结构是否发生变化")
            return
        
        print(f"\n找到 {len(grade_links)} 个级别:")
        for grade, url in grade_links.items():
            print(f"  {grade}: {url}")
        
        # 如果指定了要爬取的级别，只爬取这些级别
        if grades_to_scrape:
            grade_links = {k: v for k, v in grade_links.items() if k in grades_to_scrape}
            print(f"\n将爬取以下级别: {', '.join(grade_links.keys())}")
        
        # 逐个爬取每个级别
        total_saved = 0
        for i, (grade, url) in enumerate(grade_links.items(), 1):
            print("\n" + "=" * 60)
            print(f"[{i}/{len(grade_links)}] 开始爬取 {grade} 级别")
            print("=" * 60)
            
            try:
                # 爬取该级别
                gunpla_list = self.scrape_series_page(url, grade=grade)
                
                if gunpla_list:
                    print(f"\n成功爬取 {len(gunpla_list)} 个{grade}模型")
                    
                    # 爬取价格信息
                    if include_price:
                        print(f"\n开始爬取价格信息...")
                        print(f"预计需要 {len(gunpla_list) * delay / 60:.1f} 分钟")
                        
                        for j, item in enumerate(gunpla_list, 1):
                            if item.get('url'):
                                print(f"[{j}/{len(gunpla_list)}] {item['name_cn']}")
                                detail = self.scrape_item_detail(item['url'])
                                
                                if detail.get('price_jp_msrp'):
                                    item['price_jp_msrp'] = detail['price_jp_msrp']
                                    converted = self.convert_price(detail['price_jp_msrp'])
                                    item.update(converted)
                                    print(f"  价格: ¥{item['price_jp_msrp']:.0f} (JPY) → ${item.get('price_us_msrp', 0):.2f} (USD) / ¥{item.get('price_cn_msrp', 0):.2f} (CNY)")
                                
                                if j < len(gunpla_list):
                                    time.sleep(delay)
                    
                    # 保存到数据库
                    print(f"\n保存{grade}数据到数据库...")
                    saved = self.save_to_database(gunpla_list, grade=grade)
                    total_saved += saved
                    
                    # 级别之间延迟
                    if i < len(grade_links):
                        print(f"\n等待 {delay * 2} 秒后继续下一个级别...")
                        time.sleep(delay * 2)
                else:
                    print(f"未能爬取到{grade}数据")
                    
            except Exception as e:
                print(f"爬取{grade}级别失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("\n" + "=" * 60)
        print("所有级别爬取完成！")
        print(f"总共新增/更新: {total_saved} 条数据")
        print("=" * 60)


def scrape_specific_grades(grades, include_price=True):
    """
    爬取指定的级别（使用已知URL）
    
    参数:
        grades: 级别列表，如 ['RG', 'MG', 'HG']
        include_price: 是否爬取价格
    """
    scraper = AutoScraper78DM()
    
    # 使用已知的URL映射（避免自动查找的复杂性）
    known_urls = {
        'RG': 'https://acg.78dm.net/ct/341672.html',
        # 可以添加其他已知的URL
        # 'MG': 'https://acg.78dm.net/ct/XXXXX.html',
        # 'HG': 'https://acg.78dm.net/ct/XXXXX.html',
    }
    
    # 只爬取有已知URL的级别
    grades_to_scrape = [g for g in grades if g in known_urls]
    if not grades_to_scrape:
        print(f"未找到以下级别的已知URL: {grades}")
        print("可用的级别:", list(known_urls.keys()))
        return
    
    # 构建级别和URL的映射
    grade_urls = {grade: known_urls[grade] for grade in grades_to_scrape}
    
    print("=" * 60)
    print("使用已知URL爬取指定的级别")
    print("=" * 60)
    print(f"将爬取: {', '.join(grades_to_scrape)}")
    
    # 逐个爬取
    total_saved = 0
    for i, (grade, url) in enumerate(grade_urls.items(), 1):
        print("\n" + "=" * 60)
        print(f"[{i}/{len(grade_urls)}] 开始爬取 {grade} 级别")
        print(f"URL: {url}")
        print("=" * 60)
        
        try:
            gunpla_list = scraper.scrape_series_page(url, grade=grade)
            
            if gunpla_list:
                print(f"\n成功爬取 {len(gunpla_list)} 个{grade}模型")
                
                if include_price:
                    print(f"\n开始爬取价格信息...")
                    print(f"预计需要 {len(gunpla_list) * 1.5 / 60:.1f} 分钟")
                    
                    for j, item in enumerate(gunpla_list, 1):
                        if item.get('url'):
                            print(f"[{j}/{len(gunpla_list)}] {item['name_cn']}")
                            detail = scraper.scrape_item_detail(item['url'])
                            
                            if detail.get('price_jp_msrp'):
                                item['price_jp_msrp'] = detail['price_jp_msrp']
                                converted = scraper.convert_price(detail['price_jp_msrp'])
                                item.update(converted)
                                print(f"  价格: ¥{item['price_jp_msrp']:.0f} (JPY) → ${item.get('price_us_msrp', 0):.2f} (USD) / ¥{item.get('price_cn_msrp', 0):.2f} (CNY)")
                            
                            if j < len(gunpla_list):
                                time.sleep(1.5)
                
                print(f"\n保存{grade}数据到数据库...")
                saved = scraper.save_to_database(gunpla_list, grade=grade)
                total_saved += saved
                
                if i < len(grade_urls):
                    time.sleep(3)
            else:
                print(f"未能爬取到{grade}数据")
                
        except Exception as e:
            print(f"爬取{grade}级别失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 60)
    print("爬取完成！")
    print(f"总共新增/更新: {total_saved} 条数据")
    print("=" * 60)


if __name__ == '__main__':
    print("78动漫自动爬虫")
    print("从主页开始，自动查找并爬取所有级别")
    print("\n" + "=" * 60)
    
    scraper = AutoScraper78DM()
    
    # 方法1：爬取指定的级别（推荐）
    print("\n使用方法1：爬取指定的级别")
    print("当前配置：爬取 RG 级别")
    print("\n如需爬取其他级别，修改下面的列表：")
    print("例如：scrape_specific_grades(['RG', 'MG', 'HG'], include_price=True)")
    print("\n开始爬取...\n")
    
    # 爬取RG级别（可以修改为其他级别）
    scrape_specific_grades(['RG'], include_price=True)
    
    # 如果需要爬取更多级别，取消下面的注释并修改：
    # scrape_specific_grades(['RG', 'MG', 'HG'], include_price=True)
    
    # 方法2：爬取所有找到的级别（不推荐，数据量太大）
    # scraper.scrape_all_grades(include_price=True, delay=1.5)
