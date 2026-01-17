"""
更新已有模型的价格信息
只更新价格为空的模型
"""
from 78dm_scraper import Scraper78DM
from models import db, Gunpla
from app import app
import time

def update_missing_prices(grade='RG', delay=1.5):
    """
    更新缺少价格信息的模型
    
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
        print(f"开始更新价格信息...")
        print(f"预计需要 {len(gunpla_list) * delay / 60:.1f} 分钟\n")
        
        updated_count = 0
        failed_count = 0
        
        for i, gunpla in enumerate(gunpla_list, 1):
            # 尝试构建78动漫的URL
            # 78动漫的URL格式通常是：https://acg.78dm.net/ct/数字.html
            # 由于我们没有存储原始URL，需要搜索或手动提供
            
            # 方法1：尝试在78动漫搜索
            search_url = f"https://acg.78dm.net/search?q={gunpla.name_cn}"
            print(f"[{i}/{len(gunpla_list)}] {gunpla.name_cn}")
            
            # 这里简化处理：提示用户需要手动查找URL
            # 或者可以改进为自动搜索功能
            print(f"  提示：需要手动查找 {gunpla.name_cn} 的78动漫URL")
            print(f"  或者等待自动搜索功能实现")
            
            # TODO: 实现自动搜索功能
            # 暂时跳过，等待改进
            failed_count += 1
            continue
        
        print(f"\n更新完成！")
        print(f"成功更新: {updated_count} 个")
        print(f"需要手动处理: {failed_count} 个")

if __name__ == '__main__':
    print("=" * 60)
    print("更新模型价格信息")
    print("=" * 60)
    print("\n注意：由于需要访问每个模型的详情页面，")
    print("建议直接运行 78dm_scraper.py 重新爬取（会更新已有数据）\n")
    
    # 更新RG系列
    update_missing_prices(grade='RG', delay=1.5)
