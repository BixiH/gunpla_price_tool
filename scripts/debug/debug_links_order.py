"""
调试链接顺序 - 查看子分类标题和模型链接的顺序
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
print("前50个链接的详细信息：")
print("=" * 60)

current_subcategory = '普通版'
subcategory_count = 0
model_count = 0

for i, link in enumerate(links[:50], 1):
    name = link.get_text(strip=True)
    href = link.get('href', '')
    
    # 检查是否是子分类标题
    if '共' in name and '款' in name:
        if '普通版' in name:
            current_subcategory = '普通版'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        elif '网络限定版' in name:
            current_subcategory = '网络限定版'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        elif '其他限定版' in name:
            current_subcategory = '其他限定版'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        elif 'EVANGELION系列' in name or ('EVA' in name and '系列' in name):
            current_subcategory = 'EVANGELION系列'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        elif '勇者王系列' in name:
            current_subcategory = '勇者王系列'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        elif '参考出品' in name or '开发中' in name:
            current_subcategory = '参考出品/开发中'
            print(f"{i}. [子分类标题] {current_subcategory} - {name[:50]}")
        subcategory_count += 1
    elif name and len(name) > 2 and not any(k in name for k in ['更多', '显示', '隐藏', '加载', '级别分类详情']):
        model_count += 1
        print(f"{i}. [模型] {current_subcategory} - {name[:40]}")
        if model_count >= 10:
            print("...")
            break

print(f"\n子分类标题数量: {subcategory_count}")
print(f"模型数量（前50个中）: {model_count}")
