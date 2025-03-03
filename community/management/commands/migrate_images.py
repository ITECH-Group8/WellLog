import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from community.models import Post
import io
import psycopg
from django.db import connection
import base64
from PIL import Image
import datetime


class Command(BaseCommand):
    help = '将数据库中的二进制图片数据迁移到阿里云OSS对象存储'

    def add_arguments(self, parser):
        # 添加可选参数，指定要处理的帖子ID
        parser.add_argument('--post_id', type=int, help='指定要处理的帖子ID')
        parser.add_argument('--force', action='store_true', help='强制重新处理已有图片的帖子')
        
    def handle(self, *args, **options):
        self.stdout.write("开始迁移图片数据到阿里云OSS...")
        
        # 获取参数
        post_id = options.get('post_id')
        force = options.get('force', False)
        
        # 获取当前存储后端
        from django.core.files.storage import default_storage
        storage_class = default_storage.__class__.__name__
        self.stdout.write(f"当前存储后端: {storage_class}")
        
        # 获取所有帖子或指定帖子
        if post_id:
            posts = Post.objects.filter(id=post_id)
        else:
            posts = Post.objects.all()
        
        # 计数器
        migrated = 0
        skipped = 0
        errors = 0
        
        for post in posts:
            try:
                self.stdout.write(f"处理帖子: {post.id} - {post.title}")
                
                # 如果已有图片且不强制重新处理，则跳过
                if not force and post.image and hasattr(post.image, 'url') and post.image.name:
                    try:
                        # 测试URL是否有效
                        url = post.image.url
                        self.stdout.write(f"帖子 {post.id} 已有可访问的图片，跳过...")
                        skipped += 1
                        continue
                    except:
                        self.stdout.write(f"帖子 {post.id} 的图片URL无效，将重新处理")
                
                # 直接从数据库查询二进制数据
                with connection.cursor() as cursor:
                    # 检查community_post表是否存在旧的二进制image字段
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name='community_post' AND column_name='image';
                    """)
                    column_info = cursor.fetchone()
                    has_binary_image = column_info and column_info[1] == 'bytea'
                    
                    if has_binary_image:
                        # 获取二进制图片数据
                        cursor.execute(f"""
                            SELECT image, thumbnail 
                            FROM community_post 
                            WHERE id = %s;
                        """, [post.id])
                        row = cursor.fetchone()
                        
                        if row and row[0]:  # 如果有图片数据
                            # 处理主图
                            image_data = row[0]
                            if image_data:
                                # 将二进制数据转换为文件并保存
                                image_name = f"community/images/post_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                post.image.save(image_name, ContentFile(image_data), save=False)
                                self.stdout.write(f"已保存主图: {image_name}")
                            
                            # 处理缩略图
                            thumbnail_data = row[1]
                            if thumbnail_data:
                                # 将二进制数据转换为文件并保存
                                thumb_name = f"community/thumbnails/thumb_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                post.thumbnail.save(thumb_name, ContentFile(thumbnail_data), save=False)
                                self.stdout.write(f"已保存缩略图: {thumb_name}")
                            
                            # 如果只有主图没有缩略图，则创建缩略图
                            elif image_data:
                                try:
                                    # 从二进制数据创建图像
                                    img = Image.open(io.BytesIO(image_data))
                                    # 调整大小为300宽度
                                    width, height = img.size
                                    new_width = 300
                                    new_height = int(height * (new_width / width))
                                    img = img.resize((new_width, new_height), Image.LANCZOS)
                                    # 保存为JPEG
                                    thumb_io = io.BytesIO()
                                    img.save(thumb_io, format='JPEG', quality=70)
                                    thumb_io.seek(0)
                                    # 保存缩略图
                                    thumb_name = f"community/thumbnails/thumb_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                    post.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                                    self.stdout.write(f"已创建新缩略图: {thumb_name}")
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f"创建缩略图时出错: {e}"))
                            
                            # 保存帖子
                            post.save()
                            migrated += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"帖子 {post.id} 没有二进制图片数据"))
                            skipped += 1
                    else:
                        # 检查图片是否已经从本地存储迁移到OSS
                        if post.image and post.image.name and post.image.name.startswith('media/'):
                            try:
                                # 读取本地文件
                                old_path = post.image.path
                                if os.path.exists(old_path):
                                    with open(old_path, 'rb') as f:
                                        image_data = f.read()
                                        
                                        # 创建新文件名，不包含media/前缀
                                        new_name = post.image.name.replace('media/', '', 1)
                                        
                                        # 保存到OSS
                                        post.image.save(new_name, ContentFile(image_data), save=False)
                                        self.stdout.write(f"从本地存储迁移图片: {new_name}")
                                        
                                        # 如果有缩略图，也迁移
                                        if post.thumbnail and post.thumbnail.name and post.thumbnail.name.startswith('media/'):
                                            old_thumb_path = post.thumbnail.path
                                            if os.path.exists(old_thumb_path):
                                                with open(old_thumb_path, 'rb') as f_thumb:
                                                    thumb_data = f_thumb.read()
                                                    new_thumb_name = post.thumbnail.name.replace('media/', '', 1)
                                                    post.thumbnail.save(new_thumb_name, ContentFile(thumb_data), save=False)
                                                    self.stdout.write(f"从本地存储迁移缩略图: {new_thumb_name}")
                                        
                                        post.save()
                                        migrated += 1
                                else:
                                    self.stdout.write(self.style.WARNING(f"帖子 {post.id} 的本地图片文件不存在"))
                                    skipped += 1
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"从本地存储迁移时出错: {e}"))
                                errors += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"帖子 {post.id} 没有需要迁移的图片数据"))
                            skipped += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"处理帖子 {post.id} 时出错: {e}"))
                errors += 1
        
        self.stdout.write(self.style.SUCCESS(f"图片迁移完成! 已迁移: {migrated}, 已跳过: {skipped}, 错误: {errors}"))
        
        # 检查存储后端是否为阿里云OSS
        if hasattr(settings, 'ALIYUN_BUCKET_NAME') and hasattr(settings, 'ALIYUN_ENDPOINT'):
            self.stdout.write(self.style.SUCCESS(f"使用阿里云OSS存储。请检查您的OSS控制台，确认文件是否正确上传。"))
            self.stdout.write(f"OSS存储桶: {settings.ALIYUN_BUCKET_NAME}")
            self.stdout.write(f"OSS端点: {settings.ALIYUN_ENDPOINT}") 