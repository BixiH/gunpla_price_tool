"""
将HG级别拆分为HGUC、HGGTO、HGBF/BD三个独立级别
这个脚本需要根据实际数据情况进行调整
"""
from app import app
from models import db, Gunpla

def migrate_hg_to_subcategories():
    """
    将HG级别的数据迁移到HGUC、HGGTO、HGBF/BD
    注意：这个函数需要根据实际数据情况进行调整
    """
    with app.app_context():
        # 查找所有HG级别的模型
        hg_models = Gunpla.query.filter_by(grade='HG').all()
        
        print(f"找到 {len(hg_models)} 个HG级别的模型")
        print("\n开始迁移...")
        
        migrated_count = 0
        skipped_count = 0
        
        for model in hg_models:
            name = model.name_cn
            series = model.series or ''
            
            # 根据名称和系列判断应该属于哪个子分类
            # 这里需要根据实际数据调整判断逻辑
            new_grade = None
            
            # 判断逻辑（需要根据实际数据调整）
            # 注意：这个判断逻辑可能需要根据实际数据情况进行调整
            name_upper = name.upper()
            series_upper = (series or '').upper()
            
            # HGBF/BD: Build Fighters / Build Divers 系列
            if ('BF' in name_upper or 'BD' in name_upper or 
                'BUILD' in name_upper or 'BUILD' in series_upper or 
                '创制' in name or '创战' in name or '创形' in name):
                new_grade = 'HGBF/BD'
            # HGGTO: Gundam The Origin 系列
            elif ('GTO' in name_upper or 'GTO' in series_upper or 
                  '重力战线' in name or '重力战线' in series or
                  'THE ORIGIN' in name_upper or 'THE ORIGIN' in series_upper):
                new_grade = 'HGGTO'
            # HGUC: Universal Century 系列（默认）
            else:
                # 默认归类为HGUC（如果无法判断）
                new_grade = 'HGUC'
            
            if new_grade:
                model.grade = new_grade
                migrated_count += 1
                print(f"  {name} -> {new_grade}")
            else:
                skipped_count += 1
                print(f"  跳过（无法判断）: {name}")
        
        db.session.commit()
        
        print(f"\n迁移完成！")
        print(f"  已迁移: {migrated_count} 条")
        print(f"  跳过: {skipped_count} 条")
        
        # 显示统计
        print("\n迁移后的统计：")
        for grade in ['HGUC', 'HGGTO', 'HGBF/BD']:
            count = Gunpla.query.filter_by(grade=grade).count()
            print(f"  {grade}: {count} 个")

if __name__ == '__main__':
    print("=" * 60)
    print("HG级别拆分迁移脚本")
    print("=" * 60)
    print("\n警告：此操作会修改数据库中的HG级别数据")
    print("请确保已备份数据库！")
    print("\n按Ctrl+C取消，或等待5秒后继续...")
    
    import time
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n已取消")
        exit(0)
    
    migrate_hg_to_subcategories()
    print("\n完成！")
