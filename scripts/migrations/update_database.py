"""
更新数据库，添加subcategory字段
"""
from app import app, db
from models import Gunpla
from sqlalchemy import text

def update_database():
    """添加subcategory字段到数据库"""
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('gunpla')]
            
            if 'subcategory' in columns:
                print("subcategory字段已存在，无需更新")
                return
            
            # 添加字段
            print("正在添加subcategory字段...")
            db.session.execute(text('ALTER TABLE gunpla ADD COLUMN subcategory VARCHAR(100)'))
            db.session.commit()
            print("[成功] subcategory字段添加成功！")
            
        except Exception as e:
            print(f"更新数据库失败: {e}")
            # 如果ALTER TABLE失败，尝试重新创建表
            print("\n尝试重新创建表结构...")
            try:
                db.drop_all()
                db.create_all()
                print("[成功] 表结构重新创建成功！")
                print("[警告] 注意：所有数据已清空，需要重新爬取")
            except Exception as e2:
                print(f"重新创建表失败: {e2}")
                db.session.rollback()

if __name__ == '__main__':
    print("=" * 60)
    print("更新数据库结构 - 添加subcategory字段")
    print("=" * 60)
    print()
    update_database()
    print()
    print("=" * 60)
    print("更新完成！")
    print("=" * 60)
    print("\n下一步：运行爬虫重新爬取数据（包含子分类）")
    print("命令：py 78dm_scraper.py")
