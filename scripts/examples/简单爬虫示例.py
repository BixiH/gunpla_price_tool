"""
简单爬虫示例 - 根据实际网站结构调整
这个文件展示了如何根据不同的网站结构来爬取数据
"""
import requests
from bs4 import BeautifulSoup
from models import db, Gunpla
from app import app
import re

def parse_price(text):
    """从文本中提取价格数字"""
    if not text:
        return None
    match = re.search(r'(\d+)', text.replace(',', ''))
    return float(match.group(1)) if match else None

def scrape_simple_table(url, grade):
    """
    示例1：如果数据在简单的HTML表格中
    
    表格结构示例：
    <table>
      <tr>
        <td>名称</td>
        <td>级别</td>
        <td>价格</td>
      </tr>
      ...
    </table>
    """
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    gunpla_list = []
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')[1:]  # 跳过表头
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                data = {
                    'name_cn': cells[0].get_text(strip=True),
                    'grade': cells[1].get_text(strip=True) or grade,
                    'price_jp_msrp': parse_price(cells[2].get_text(strip=True)),
                }
                if data['name_cn']:
                    gunpla_list.append(data)
    
    return gunpla_list

def scrape_div_items(url, grade):
    """
    示例2：如果数据在div元素中
    
    HTML结构示例：
    <div class="gunpla-item">
      <h3>RX-78-2 高达</h3>
      <span class="price">4500日元</span>
      <span class="grade">MG</span>
    </div>
    """
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    gunpla_list = []
    items = soup.find_all('div', class_='gunpla-item')  # 根据实际class调整
    
    for item in items:
        name_elem = item.find('h3') or item.find('a')
        price_elem = item.find('span', class_='price')
        grade_elem = item.find('span', class_='grade')
        
        if name_elem:
            data = {
                'name_cn': name_elem.get_text(strip=True),
                'grade': grade_elem.get_text(strip=True) if grade_elem else grade,
                'price_jp_msrp': parse_price(price_elem.get_text(strip=True)) if price_elem else None,
            }
            if data['name_cn']:
                gunpla_list.append(data)
    
    return gunpla_list

def save_to_db(gunpla_list):
    """保存到数据库"""
    with app.app_context():
        saved = 0
        for data in gunpla_list:
            # 检查是否已存在
            existing = Gunpla.query.filter_by(
                name_cn=data['name_cn'],
                grade=data.get('grade', '其他')
            ).first()
            
            if existing:
                continue
            
            gunpla = Gunpla(
                name_cn=data['name_cn'],
                grade=data.get('grade', '其他'),
                price_jp_msrp=data.get('price_jp_msrp'),
            )
            db.session.add(gunpla)
            saved += 1
        
        db.session.commit()
        print(f"保存了 {saved} 条新数据")

# 使用示例
if __name__ == '__main__':
    print("这是一个示例文件，请根据实际网站结构调整")
    print("\n使用方法：")
    print("1. 查看目标网站的HTML结构")
    print("2. 选择适合的解析函数（表格或div）")
    print("3. 修改函数中的选择器（class、标签等）")
    print("4. 运行爬虫")
    
    # 示例：爬取RG级别
    # url = 'https://example.com/rg-list'
    # data = scrape_simple_table(url, 'RG')
    # save_to_db(data)
