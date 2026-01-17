"""
专门用于爬取RG系列 - 只爬取列表信息，不爬取价格
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

def scrape_rg_list_only():
    """
    只爬取RG系列的列表信息（名称、子分类等），不爬取价格
    """
    scraper = Scraper78DM()
    
    # RG系列URL
    rg_url = 'https://acg.78dm.net/ct/341672.html'
    
    print("=" * 60)
    print("爬取RG系列列表信息（不包含价格）")
    print("=" * 60)
    print(f"URL: {rg_url}\n")
    
    # 爬取列表
    gunpla_list = scraper.scrape_series_page(rg_url, grade='RG')
    
    if gunpla_list:
        print(f"\n成功爬取 {len(gunpla_list)} 个模型")
        print(f"\n子分类统计：")
        
        # 统计子分类
        subcategory_count = {}
        for item in gunpla_list:
            subcat = item.get('subcategory', '未知')
            subcategory_count[subcat] = subcategory_count.get(subcat, 0) + 1
        
        for subcat, count in sorted(subcategory_count.items()):
            print(f"  {subcat}: {count} 个")
        
        # 保存到数据库（不包含价格）
        print(f"\n保存数据到数据库...")
        scraper.save_to_database(gunpla_list, grade='RG')
        
        print("\n" + "=" * 60)
        print("完成！")
        print("=" * 60)
        print("\n提示：")
        print("- 价格信息可以后续手动补充")
        print("- 或者单独运行价格爬取脚本（需要改进价格提取逻辑）")
    else:
        print("未能爬取到数据")


if __name__ == '__main__':
    scrape_rg_list_only()
