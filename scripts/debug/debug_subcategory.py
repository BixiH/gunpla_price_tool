"""
调试子分类识别 - 查看网页结构
"""
import requests
from bs4 import BeautifulSoup
import re

rg_url = 'https://acg.78dm.net/ct/341672.html'

response = requests.get(rg_url, timeout=15)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有链接
links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))

print(f"找到 {len(links)} 个链接\n")
print("前30个链接的内容：")
print("=" * 60)

for i, link in enumerate(links[:30], 1):
    name = link.get_text(strip=True)
    href = link.get('href', '')
    
    # 查看包含"共"的链接
    if '共' in name:
        print(f"{i}. [{name}] - {href}")
        # 查看父元素
        parent = link.parent
        if parent:
            print(f"   父元素: {parent.name} - {parent.get_text(strip=True)[:100]}")

print("\n" + "=" * 60)
print("查找子分类标题...")
print("=" * 60)

# 查找包含"共X款"的元素
subcategory_titles = []
for elem in soup.find_all(string=re.compile(r'.*共\d+款')):
    text = str(elem).strip()
    if '共' in text and '款' in text:
        parent = elem.parent if hasattr(elem, 'parent') else None
        if parent:
            parent_text = parent.get_text(strip=True)
            print(f"找到: {text[:50]}")
            print(f"  父元素: {parent.name} - {parent_text[:100]}")
