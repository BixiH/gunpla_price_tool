"""
78动漫网站爬虫
专门用于爬取 https://acg.78dm.net 的高达数据
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from models import db, Gunpla
from app import app
import json
from sqlalchemy import or_

class Scraper78DM:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.base_url = 'https://acg.78dm.net'
    
    def parse_price(self, price_text):
        """解析价格文本"""
        if not price_text:
            return None
        
        # 提取数字，例如："2500→2800日元" -> 2500
        price_text = price_text.replace(',', '').replace('，', '')
        match = re.search(r'(\d+)', price_text)
        if match:
            return float(match.group(1))
        return None
    
    def extract_model_number(self, name):
        """从名称中提取机体编号"""
        # 常见的编号格式：RX-78-2, MS-06S, GNT-0000等
        patterns = [
            r'([A-Z]{1,3}-\d{2,4}[A-Z]?)',  # RX-78-2, MS-06S
            r'([A-Z]{2,4}\d{1,3})',  # RG02, HG123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                return match.group(1)
        return None
    
    def detect_subcategory(self, link_element, soup):
        """
        检测模型所属的子分类
        
        参数:
            link_element: 链接元素
            soup: BeautifulSoup对象
        
        返回:
            子分类名称
        """
        # 78动漫的子分类通常以标题或div分隔
        # 查找链接所在的父容器，向上查找包含分类标题的元素
        
        current = link_element.parent
        subcategory = None
        
        # 向上查找，寻找分类标题
        for _ in range(10):  # 最多向上查找10层
            if current is None:
                break
            
            # 查找包含分类关键词的文本
            text = current.get_text() if hasattr(current, 'get_text') else str(current)
            
            # 常见的子分类关键词
            if '普通版' in text and '共' in text:
                subcategory = '普通版'
                break
            elif '网络限定版' in text and '共' in text:
                subcategory = '网络限定版'
                break
            elif '其他限定版' in text and '共' in text:
                subcategory = '其他限定版'
                break
            elif 'EVANGELION系列' in text or 'EVA' in text:
                subcategory = 'EVANGELION系列'
                break
            elif '勇者王系列' in text or '勇者王' in text:
                subcategory = '勇者王系列'
                break
            elif '参考出品' in text or '开发中' in text:
                subcategory = '参考出品/开发中'
                break
            
            # 继续向上查找
            if hasattr(current, 'parent'):
                current = current.parent
            else:
                break
        
        # 如果没找到，尝试在整个页面中查找链接附近的分类信息
        if not subcategory:
            # 查找链接前后的文本，看是否有分类信息
            link_text = link_element.get_text(strip=True)
            page_text = soup.get_text()
            
            # 查找链接在页面中的位置
            link_index = page_text.find(link_text)
            if link_index > 0:
                # 查找链接前500字符内的分类信息
                context = page_text[max(0, link_index-500):link_index]
                if '普通版' in context and '共' in context:
                    subcategory = '普通版'
                elif '网络限定版' in context and '共' in context:
                    subcategory = '网络限定版'
                elif '其他限定版' in context and '共' in context:
                    subcategory = '其他限定版'
                elif 'EVANGELION系列' in context:
                    subcategory = 'EVANGELION系列'
                elif '勇者王系列' in context:
                    subcategory = '勇者王系列'
                elif '参考出品' in context:
                    subcategory = '参考出品/开发中'
        
        return subcategory or '普通版'  # 默认返回普通版
    
    def scrape_series_page(self, url, grade='RG'):
        """
        爬取系列页面（如RG系列页面），自动识别子分类
        
        参数:
            url: 系列页面URL，例如：https://acg.78dm.net/ct/341672.html
            grade: 级别，如 'RG', 'MG', 'HG' 等
        """
        print(f"正在爬取: {url}")
        print(f"级别: {grade}")
        
        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            gunpla_list = []
            
            # 查找所有链接，包含高达名称的
            links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))
            
            # 统计子分类
            subcategory_count = {}
            
            for link in links:
                name = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 过滤掉无效链接和导航链接
                if not name or len(name) < 2:
                    continue
                
                # 跳过一些明显的非模型链接
                if any(skip in name for skip in ['更多', '显示', '隐藏', '加载', '级别', '分类', '共']):
                    continue
                
                # 构建完整URL
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # 检测子分类
                subcategory = self.detect_subcategory(link, soup)
                subcategory_count[subcategory] = subcategory_count.get(subcategory, 0) + 1
                
                # 提取基本信息
                data = {
                    'name_cn': name,
                    'grade': grade,
                    'url': full_url,
                    'subcategory': subcategory,
                }
                
                # 尝试从名称中提取编号
                ms_number = self.extract_model_number(name)
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
            
            # 打印子分类统计
            print(f"\n子分类统计：")
            for subcat, count in sorted(subcategory_count.items()):
                print(f"  {subcat}: {count} 个")
            
            print(f"\n找到 {len(unique_list)} 个模型")
            return unique_list
            
        except Exception as e:
            print(f"爬取失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_item_detail(self, url):
        """
        爬取单个模型的详细信息页面，提取价格信息
        
        参数:
            url: 单品页面URL
        
        返回:
            包含价格信息的字典
        """
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {}
            
            # 方法1：查找表格中的价格信息
            # 78动漫通常在表格中显示价格
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        
                        # 查找价格相关字段
                        if '价格' in label or '定价' in label or '日元' in label:
                            price = self.parse_price(value)
                            if price:
                                data['price_jp_msrp'] = price
                                break
                        elif '发售' in label and '价格' in value:
                            # 有时价格在发售信息中
                            price = self.parse_price(value)
                            if price:
                                data['price_jp_msrp'] = price
            
            # 方法2：在页面文本中搜索价格模式
            if 'price_jp_msrp' not in data:
                page_text = soup.get_text()
                price_patterns = [
                    r'(\d+)\s*→\s*(\d+)\s*日元',  # 2500→2800日元
                    r'定价[：:]\s*(\d+)',  # 定价：2500
                    r'价格[：:]\s*(\d+)',  # 价格：2500
                    r'(\d+)\s*日元',  # 2500日元
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        # 如果有两个数字，取第一个（通常是定价）
                        price = float(match.group(1))
                        data['price_jp_msrp'] = price
                        break
            
            # 查找其他信息
            page_text = soup.get_text()
            if '万代' in page_text or 'Bandai' in page_text:
                data['series'] = '万代'
            
            return data
            
        except Exception as e:
            print(f"爬取详情失败 {url}: {e}")
            return {}
    
    def convert_price(self, jpy_price, jpy_to_usd=0.0067, jpy_to_cny=0.05):
        """
        将日元价格转换为美元和人民币价格
        
        参数:
            jpy_price: 日元价格
            jpy_to_usd: 日元对美元汇率（默认：1日元 = 0.0067美元，约150日元=1美元）
            jpy_to_cny: 日元对人民币汇率（默认：1日元 = 0.05人民币，约20日元=1人民币）
        
        返回:
            包含转换后价格的字典
        """
        if not jpy_price:
            return {}
        
        return {
            'price_us_msrp': round(jpy_price * jpy_to_usd, 2),
            'price_cn_msrp': round(jpy_price * jpy_to_cny, 2),
        }
    
    def save_to_database(self, gunpla_list, grade=None):
        """保存到数据库"""
        with app.app_context():
            saved_count = 0
            skipped_count = 0
            updated_count = 0
            
            for data in gunpla_list:
                try:
                    # 如果指定了级别，使用指定的级别
                    if grade:
                        data['grade'] = grade
                    
                    name = data.get('name_cn', '').strip()
                    if not name:
                        continue
                    
                    grade_value = data.get('grade', '其他')
                    
                    # 检查是否已存在
                    existing = Gunpla.query.filter_by(
                        name_cn=name,
                        grade=grade_value
                    ).first()
                    
                    if existing:
                        # 如果存在，更新价格信息和子分类
                        updated = False
                        if data.get('price_jp_msrp') and not existing.price_jp_msrp:
                            existing.price_jp_msrp = data.get('price_jp_msrp')
                            updated = True
                        if data.get('price_us_msrp') and not existing.price_us_msrp:
                            existing.price_us_msrp = data.get('price_us_msrp')
                            updated = True
                        if data.get('price_cn_msrp') and not existing.price_cn_msrp:
                            existing.price_cn_msrp = data.get('price_cn_msrp')
                            updated = True
                        # 更新子分类（如果原来没有）
                        if data.get('subcategory') and not existing.subcategory:
                            existing.subcategory = data.get('subcategory')
                            updated = True
                        
                        if updated:
                            db.session.commit()
                            updated_count += 1
                            print(f"更新: {name}")
                        else:
                            skipped_count += 1
                        continue
                    
                    # 创建新的高达记录
                    gunpla = Gunpla(
                        name_cn=name,
                        name_jp=data.get('name_jp'),
                        name_en=data.get('name_en'),
                        grade=grade_value,
                        ms_number=data.get('ms_number'),
                        series=data.get('series', 'RG系列拼装模型'),
                        subcategory=data.get('subcategory'),
                        price_jp_msrp=data.get('price_jp_msrp'),
                        price_jp_market=data.get('price_jp_market'),
                        price_us_msrp=data.get('price_us_msrp'),
                        price_us_market=data.get('price_us_market'),
                        price_cn_msrp=data.get('price_cn_msrp'),
                        price_cn_market=data.get('price_cn_market'),
                    )
                    
                    db.session.add(gunpla)
                    saved_count += 1
                    
                    # 每10条提交一次，避免内存占用过大
                    if saved_count % 10 == 0:
                        db.session.commit()
                    
                except Exception as e:
                    print(f"保存数据失败: {data.get('name_cn')} - {e}")
                    db.session.rollback()
                    continue
            
            db.session.commit()
            print(f"\n保存完成！")
            print(f"新增: {saved_count} 条")
            print(f"更新: {updated_count} 条")
            print(f"跳过（已存在）: {skipped_count} 条")
            return saved_count


def scrape_rg_series(include_price=True, delay=1.5):
    """
    爬取RG系列，包括价格信息
    
    参数:
        include_price: 是否爬取价格信息（默认True）
        delay: 每个请求之间的延迟（秒），默认1.5秒
    """
    scraper = Scraper78DM()
    
    # RG系列页面
    url = 'https://acg.78dm.net/ct/341672.html'
    
    print("=" * 60)
    print("开始爬取RG系列")
    print("=" * 60)
    
    # 爬取列表
    gunpla_list = scraper.scrape_series_page(url, grade='RG')
    
    if gunpla_list:
        print(f"\n成功爬取 {len(gunpla_list)} 个模型")
        
        # 爬取详细信息（价格等）
        if include_price:
            print(f"\n开始爬取价格信息...")
            print(f"预计需要 {len(gunpla_list) * delay / 60:.1f} 分钟")
            print("正在爬取，请耐心等待...\n")
            
            for i, item in enumerate(gunpla_list, 1):
                if item.get('url'):
                    print(f"[{i}/{len(gunpla_list)}] 爬取: {item['name_cn']}")
                    detail = scraper.scrape_item_detail(item['url'])
                    
                    # 更新价格信息
                    if detail.get('price_jp_msrp'):
                        item['price_jp_msrp'] = detail['price_jp_msrp']
                        
                        # 换算为美元和人民币定价
                        converted = scraper.convert_price(detail['price_jp_msrp'])
                        item.update(converted)
                        
                        print(f"  价格: ¥{item['price_jp_msrp']:.0f} (JPY) → ${item.get('price_us_msrp', 0):.2f} (USD) / ¥{item.get('price_cn_msrp', 0):.2f} (CNY)")
                    else:
                        print(f"  未找到价格信息")
                    
                    # 延迟，避免请求过快
                    if i < len(gunpla_list):
                        time.sleep(delay)
        
        # 保存到数据库
        print(f"\n保存数据到数据库...")
        scraper.save_to_database(gunpla_list, grade='RG')
    else:
        print("未能爬取到数据，请检查网站结构或网络连接")


def scrape_by_grade(grade, url):
    """
    按级别爬取
    
    参数:
        grade: 级别，如 'RG', 'MG', 'HG' 等
        url: 该级别的系列页面URL
    """
    scraper = Scraper78DM()
    
    print("=" * 60)
    print(f"开始爬取{grade}系列")
    print("=" * 60)
    
    gunpla_list = scraper.scrape_series_page(url, grade=grade)
    
    if gunpla_list:
        print(f"\n成功爬取 {len(gunpla_list)} 个模型")
        scraper.save_to_database(gunpla_list, grade=grade)
    else:
        print("未能爬取到数据")


def update_existing_prices(grade='RG', delay=1.5):
    """
    更新已有模型的价格信息（只更新价格为空的模型）
    
    参数:
        grade: 级别
        delay: 每个请求之间的延迟（秒）
    """
    scraper = Scraper78DM()
    
    with app.app_context():
        # 获取所有该级别且没有价格的模型
        gunpla_list = Gunpla.query.filter_by(grade=grade).filter(
            db.or_(
                Gunpla.price_jp_msrp.is_(None),
                Gunpla.price_jp_msrp == 0
            )
        ).all()
        
        if not gunpla_list:
            print(f"所有{grade}系列模型都已包含价格信息")
            return
        
        print(f"找到 {len(gunpla_list)} 个需要更新价格的模型")
        print(f"开始更新价格信息...\n")
        
        updated_count = 0
        for i, gunpla in enumerate(gunpla_list, 1):
            # 尝试从78动漫搜索找到对应的URL
            # 这里简化处理，需要手动提供URL或改进搜索逻辑
            print(f"[{i}/{len(gunpla_list)}] {gunpla.name_cn} - 需要手动提供URL或改进搜索")
            # TODO: 实现自动搜索功能
        
        print(f"\n更新完成！")


if __name__ == '__main__':
    print("78动漫爬虫 - 带价格爬取和汇率换算")
    print("=" * 60)
    print("\n使用方法：")
    print("1. 爬取RG系列（包含价格）：scrape_rg_series()")
    print("2. 爬取其他级别：scrape_by_grade('MG', 'https://acg.78dm.net/ct/XXXXX.html')")
    print("\n汇率设置：")
    print("- 日元 → 美元：1 JPY = 0.0067 USD (约150 JPY = 1 USD)")
    print("- 日元 → 人民币：1 JPY = 0.05 CNY (约20 JPY = 1 CNY)")
    print("\n开始爬取RG系列（包含价格）...\n")
    
    # 爬取RG系列（包含价格）
    scrape_rg_series(include_price=True, delay=1.5)
    
    # 如果需要爬取其他级别，取消下面的注释并修改URL
    # scrape_by_grade('MG', 'https://acg.78dm.net/ct/XXXXX.html')
    # scrape_by_grade('HG', 'https://acg.78dm.net/ct/XXXXX.html')
