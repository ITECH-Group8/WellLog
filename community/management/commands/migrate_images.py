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
    help = 'Migrate binary image data from database to Alibaba Cloud OSS storage'

    def add_arguments(self, parser):
        # Add optional arguments to specify post ID to process
        parser.add_argument('--post_id', type=int, help='Specify the post ID to process')
        parser.add_argument('--force', action='store_true', help='Force reprocessing of posts with existing images')
        
    def handle(self, *args, **options):
        self.stdout.write("Starting migration of image data to Alibaba Cloud OSS...")
        
        # Get parameters
        post_id = options.get('post_id')
        force = options.get('force', False)
        
        # Get current storage backend
        from django.core.files.storage import default_storage
        storage_class = default_storage.__class__.__name__
        self.stdout.write(f"Current storage backend: {storage_class}")
        
        # Get all posts or specific post
        if post_id:
            posts = Post.objects.filter(id=post_id)
        else:
            posts = Post.objects.all()
        
        # Counters
        migrated = 0
        skipped = 0
        errors = 0
        
        for post in posts:
            try:
                self.stdout.write(f"Processing post: {post.id} - {post.title}")
                
                # Skip if image exists and not forcing reprocessing
                if not force and post.image and hasattr(post.image, 'url') and post.image.name:
                    try:
                        # Test if URL is valid
                        url = post.image.url
                        self.stdout.write(f"Post {post.id} already has accessible image, skipping...")
                        skipped += 1
                        continue
                    except:
                        self.stdout.write(f"Post {post.id} image URL is invalid, will reprocess")
                
                # Directly query binary data from database
                with connection.cursor() as cursor:
                    # Check if community_post table has old binary image field
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name='community_post' AND column_name='image';
                    """)
                    column_info = cursor.fetchone()
                    has_binary_image = column_info and column_info[1] == 'bytea'
                    
                    if has_binary_image:
                        # Get binary image data
                        cursor.execute(f"""
                            SELECT image, thumbnail 
                            FROM community_post 
                            WHERE id = %s;
                        """, [post.id])
                        row = cursor.fetchone()
                        
                        if row and row[0]:  # If image data exists
                            # Process main image
                            image_data = row[0]
                            if image_data:
                                # Convert binary data to file and save
                                image_name = f"community/images/post_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                post.image.save(image_name, ContentFile(image_data), save=False)
                                self.stdout.write(f"Saved main image: {image_name}")
                            
                            # Process thumbnail
                            thumbnail_data = row[1]
                            if thumbnail_data:
                                # Convert binary data to file and save
                                thumb_name = f"community/thumbnails/thumb_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                post.thumbnail.save(thumb_name, ContentFile(thumbnail_data), save=False)
                                self.stdout.write(f"Saved thumbnail: {thumb_name}")
                            
                            # If only main image exists without thumbnail, create thumbnail
                            elif image_data:
                                try:
                                    # Create image from binary data
                                    img = Image.open(io.BytesIO(image_data))
                                    # Resize to 300px width
                                    width, height = img.size
                                    new_width = 300
                                    new_height = int(height * (new_width / width))
                                    img = img.resize((new_width, new_height), Image.LANCZOS)
                                    # Save as JPEG
                                    thumb_io = io.BytesIO()
                                    img.save(thumb_io, format='JPEG', quality=70)
                                    thumb_io.seek(0)
                                    # Save thumbnail
                                    thumb_name = f"community/thumbnails/thumb_{post.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                                    post.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                                    self.stdout.write(f"Created new thumbnail: {thumb_name}")
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f"Error creating thumbnail: {e}"))
                            
                            # Save post
                            post.save()
                            migrated += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"Post {post.id} has no binary image data"))
                            skipped += 1
                    else:
                        # Check if image has already been migrated from local storage to OSS
                        if post.image and post.image.name and post.image.name.startswith('media/'):
                            try:
                                # Read local file
                                old_path = post.image.path
                                if os.path.exists(old_path):
                                    with open(old_path, 'rb') as f:
                                        image_data = f.read()
                                        
                                        # Create new filename without media/ prefix
                                        new_name = post.image.name.replace('media/', '', 1)
                                        
                                        # Save to OSS
                                        post.image.save(new_name, ContentFile(image_data), save=False)
                                        self.stdout.write(f"Migrated image from local storage: {new_name}")
                                        
                                        # If thumbnail exists, migrate it too
                                        if post.thumbnail and post.thumbnail.name and post.thumbnail.name.startswith('media/'):
                                            old_thumb_path = post.thumbnail.path
                                            if os.path.exists(old_thumb_path):
                                                with open(old_thumb_path, 'rb') as f_thumb:
                                                    thumb_data = f_thumb.read()
                                                    new_thumb_name = post.thumbnail.name.replace('media/', '', 1)
                                                    post.thumbnail.save(new_thumb_name, ContentFile(thumb_data), save=False)
                                                    self.stdout.write(f"Migrated thumbnail from local storage: {new_thumb_name}")
                                        
                                        post.save()
                                        migrated += 1
                                else:
                                    self.stdout.write(self.style.WARNING(f"Post {post.id} local image file does not exist"))
                                    skipped += 1
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"Error migrating from local storage: {e}"))
                                errors += 1
                        else:
                            self.stdout.write(self.style.WARNING(f"Post {post.id} has no image data to migrate"))
                            skipped += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing post {post.id}: {e}"))
                errors += 1
        
        self.stdout.write(self.style.SUCCESS(f"Image migration complete! Migrated: {migrated}, Skipped: {skipped}, Errors: {errors}"))
        
        # Check if storage backend is Alibaba Cloud OSS
        if hasattr(settings, 'ALIYUN_BUCKET_NAME') and hasattr(settings, 'ALIYUN_ENDPOINT'):
            self.stdout.write(self.style.SUCCESS(f"Using Alibaba Cloud OSS storage. Please check your OSS console to confirm files were uploaded correctly."))
            self.stdout.write(f"OSS bucket: {settings.ALIYUN_BUCKET_NAME}")
            self.stdout.write(f"OSS endpoint: {settings.ALIYUN_ENDPOINT}") 