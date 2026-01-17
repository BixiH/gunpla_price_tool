"""
数据库迁移脚本：为wishlist和collection表添加user_id列
"""
from app import app
from models import db
import sqlite3

def add_user_id_columns():
    """
    为wishlist和collection表添加user_id列
    """
    with app.app_context():
        # 获取数据库路径
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        print("=" * 60)
        print("数据库迁移：添加user_id列")
        print("=" * 60)
        print(f"数据库路径: {db_path}\n")
        
        try:
            # 直接使用SQLite连接来执行ALTER TABLE
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查wishlist表是否有user_id列
            cursor.execute("PRAGMA table_info(wishlist)")
            wishlist_columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in wishlist_columns:
                print("为wishlist表添加user_id列...")
                cursor.execute("ALTER TABLE wishlist ADD COLUMN user_id INTEGER")
                # 为现有数据设置user_id为NULL（公共数据）
                cursor.execute("UPDATE wishlist SET user_id = NULL WHERE user_id IS NULL")
                print("  [OK] wishlist表已添加user_id列")
            else:
                print("  [OK] wishlist表已有user_id列，跳过")
            
            # 检查collection表是否有user_id列
            cursor.execute("PRAGMA table_info(collection)")
            collection_columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in collection_columns:
                print("为collection表添加user_id列...")
                cursor.execute("ALTER TABLE collection ADD COLUMN user_id INTEGER")
                # 为现有数据设置user_id为NULL（公共数据）
                cursor.execute("UPDATE collection SET user_id = NULL WHERE user_id IS NULL")
                print("  [OK] collection表已添加user_id列")
            else:
                print("  [OK] collection表已有user_id列，跳过")
            
            conn.commit()
            conn.close()
            
            print("\n迁移完成！")
            
        except Exception as e:
            print(f"\n迁移失败: {e}")
            import traceback
            traceback.print_exc()
            if 'conn' in locals():
                conn.rollback()
                conn.close()

if __name__ == '__main__':
    print("开始数据库迁移...")
    add_user_id_columns()
    print("\n完成！")
