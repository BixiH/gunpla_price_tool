"""
高达数据爬虫脚本
用于从网站爬取高达数据并导入到数据库
"""
import requests
from bs4 import BeautifulSoup
import time
from models import db, Gunpla
from app import app
import re

class GunplaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def parse_price(self, price_text):
        """
        解析价格文本，提取数字
        例如："2500→2800日元" -> 2500
        """
        if not price_text:
            return None
        
        # 提取第一个数字
        match = re.search(r'(\d+)', price_text.replace(',', ''))
        if match:
            return float(match.group(1))
        return None
    
    def parse_grade_from_text(self, text):
        """
        从文本中提取级别信息
        例如："RG系列拼装模型" -> "RG"
        """
        if not text:
            return None
        
        # 常见的级别
        grades = ['PG', 'MG', 'RG', 'HG', 'EG', 'SD', 'RE', 'FM']
        for grade in grades:
            if grade in text.upper():
                return grade
        
        # 如果没有匹配，返回"其他"
        return "其他"
    
    def scrape_gunpla_from_url(self, url):
        """
        从指定URL爬取高达数据
        
        参数:
            url: 要爬取的网页URL
        
        返回:
            高达数据字典列表
        """
        print(f"正在爬取: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'  # 设置编码
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 这里需要根据实际网站结构来解析
            # 以下是示例代码，需要根据实际网站调整
            
            gunpla_list = []
            
            # 示例：假设数据在表格中
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # 根据实际表格结构调整
                        data = self.parse_table_row(cells)
                        if data:
                            gunpla_list.append(data)
            
            # 如果表格方式不行，尝试其他方式
            if not gunpla_list:
                # 尝试查找特定的div或class
                items = soup.find_all('div', class_='gunpla-item')  # 根据实际class调整
                for item in items:
                    data = self.parse_item_div(item)
                    if data:
                        gunpla_list.append(data)
            
            print(f"成功爬取 {len(gunpla_list)} 条数据")
            return gunpla_list
            
        except Exception as e:
            print(f"爬取失败: {e}")
            return []
    
    def parse_table_row(self, cells):
        """
        解析表格行数据
        需要根据实际网站结构调整
        """
        try:
            # 示例解析逻辑（需要根据实际网站调整）
            data = {}
            
            # 假设表格结构：
            # 列0: 名称, 列1: 级别, 列2: 价格, 列3: 编号等
            
            if len(cells) > 0:
                name_text = cells[0].get_text(strip=True)
                if name_text:
                    data['name_cn'] = name_text
            
            if len(cells) > 1:
                grade_text = cells[1].get_text(strip=True)
                data['grade'] = self.parse_grade_from_text(grade_text) or "其他"
            
            if len(cells) > 2:
                price_text = cells[2].get_text(strip=True)
                data['price_jp_msrp'] = self.parse_price(price_text)
            
            # 可以根据实际表格结构调整更多字段
            
            return data if data.get('name_cn') else None
            
        except Exception as e:
            print(f"解析行数据失败: {e}")
            return None
    
    def parse_item_div(self, item):
        """
        解析div元素中的数据
        需要根据实际网站结构调整
        """
        try:
            data = {}
            
            # 查找名称
            name_elem = item.find('h3') or item.find('a') or item.find('span', class_='name')
            if name_elem:
                data['name_cn'] = name_elem.get_text(strip=True)
            
            # 查找价格
            price_elem = item.find('span', class_='price') or item.find('div', class_='price')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                data['price_jp_msrp'] = self.parse_price(price_text)
            
            # 查找级别
            grade_elem = item.find('span', class_='grade') or item.find('div', class_='grade')
            if grade_elem:
                grade_text = grade_elem.get_text(strip=True)
                data['grade'] = self.parse_grade_from_text(grade_text) or "其他"
            
            return data if data.get('name_cn') else None
            
        except Exception as e:
            print(f"解析div数据失败: {e}")
            return None
    
    def save_to_database(self, gunpla_data_list, grade=None):
        """
        将爬取的数据保存到数据库
        
        参数:
            gunpla_data_list: 高达数据字典列表
            grade: 如果指定，会为所有数据设置这个级别
        """
        with app.app_context():
            saved_count = 0
            skipped_count = 0
            
            for data in gunpla_data_list:
                try:
                    # 如果指定了级别，使用指定的级别
                    if grade:
                        data['grade'] = grade
                    
                    # 检查是否已存在（根据名称和级别）
                    existing = Gunpla.query.filter_by(
                        name_cn=data.get('name_cn'),
                        grade=data.get('grade', '其他')
                    ).first()
                    
                    if existing:
                        print(f"已存在，跳过: {data.get('name_cn')}")
                        skipped_count += 1
                        continue
                    
                    # 创建新的高达记录
                    gunpla = Gunpla(
                        name_cn=data.get('name_cn', ''),
                        name_jp=data.get('name_jp'),
                        name_en=data.get('name_en'),
                        grade=data.get('grade', '其他'),
                        ms_number=data.get('ms_number'),
                        series=data.get('series'),
                        price_jp_msrp=data.get('price_jp_msrp'),
                        price_jp_market=data.get('price_jp_market'),
                        price_us_msrp=data.get('price_us_msrp'),
                        price_us_market=data.get('price_us_market'),
                        price_cn_msrp=data.get('price_cn_msrp'),
                        price_cn_market=data.get('price_cn_market'),
                    )
                    
                    db.session.add(gunpla)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存数据失败: {data.get('name_cn')} - {e}")
                    db.session.rollback()
                    continue
            
            db.session.commit()
            print(f"\n保存完成！")
            print(f"新增: {saved_count} 条")
            print(f"跳过（已存在）: {skipped_count} 条")
            return saved_count


def scrape_by_grade(grade, urls):
    """
    按级别爬取数据
    
    参数:
        grade: 级别（如 'RG', 'MG', 'HG'）
        urls: 该级别对应的URL列表
    """
    scraper = GunplaScraper()
    
    all_data = []
    for url in urls:
        data = scraper.scrape_gunpla_from_url(url)
        all_data.extend(data)
        time.sleep(1)  # 延迟1秒，避免请求过快
    
    # 保存到数据库
    if all_data:
        scraper.save_to_database(all_data, grade=grade)
    else:
        print("没有爬取到数据")


if __name__ == '__main__':
    print("=" * 60)
    print("高达数据爬虫")
    print("=" * 60)
    print("\n请根据实际网站结构调整 scraper.py 中的解析函数")
    print("然后修改下面的URL和级别信息\n")
    
    # 示例：按级别爬取
    # 请根据实际网站修改URL
    
    # 示例1：爬取RG级别
    # scrape_by_grade('RG', [
    #     'https://example.com/rg-list',
    #     'https://example.com/rg-list?page=2',
    # ])
    
    # 示例2：爬取MG级别
    # scrape_by_grade('MG', [
    #     'https://example.com/mg-list',
    # ])
    
    print("请在 scraper.py 中配置实际的URL后运行")

