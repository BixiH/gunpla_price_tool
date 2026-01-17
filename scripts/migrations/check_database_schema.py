"""
检查数据库架构，确保所有表都存在
"""
from app import app
from models import db, User, Wishlist, Collection

def check_database_schema():
    """检查数据库架构"""
    with app.app_context():
        print("=" * 60)
        print("检查数据库架构")
        print("=" * 60)
        
        # 检查users表是否存在
        try:
            user_count = User.query.count()
            print(f"[OK] users表存在，当前有 {user_count} 个用户")
        except Exception as e:
            print(f"[错误] users表不存在或有问题: {e}")
            print("正在创建users表...")
            db.create_all()
            print("[OK] users表已创建")
        
        # 检查wishlist表的列
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            wishlist_columns = [col['name'] for col in inspector.get_columns('wishlist')]
            print(f"\nwishlist表的列: {wishlist_columns}")
            if 'user_id' in wishlist_columns:
                print("[OK] wishlist表有user_id列")
            else:
                print("[错误] wishlist表缺少user_id列")
        except Exception as e:
            print(f"[错误] 无法检查wishlist表: {e}")
        
        # 检查collection表的列
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            collection_columns = [col['name'] for col in inspector.get_columns('collection')]
            print(f"\ncollection表的列: {collection_columns}")
            if 'user_id' in collection_columns:
                print("[OK] collection表有user_id列")
            else:
                print("[错误] collection表缺少user_id列")
        except Exception as e:
            print(f"[错误] 无法检查collection表: {e}")
        
        print("\n检查完成！")

if __name__ == '__main__':
    check_database_schema()
