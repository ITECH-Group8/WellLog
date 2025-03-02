import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WellLog.settings')
django.setup()

from django.db import connection

def reset_community_tables():
    """删除并重建社区应用的表"""
    with connection.cursor() as cursor:
        # 确保所有社区表都被删除
        cursor.execute("""
        DROP TABLE IF EXISTS 
            community_post, 
            community_comment, 
            community_like
        CASCADE;
        """)
        
        print("已删除社区相关表")
        
        # 删除迁移记录
        cursor.execute("""
        DELETE FROM django_migrations WHERE app = 'community';
        """)
        
        print("已删除社区迁移记录")

if __name__ == "__main__":
    print("开始重置社区表...")
    reset_community_tables()
    print("社区表重置完成。请按以下步骤继续:")
    print("1. 删除community/migrations中除__init__.py外的所有文件")
    print("2. 运行 python manage.py makemigrations community")
    print("3. 运行 python manage.py migrate community") 