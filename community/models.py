from django.db import models
from django.conf import settings
from django.urls import reverse
import base64
import os
from pathlib import Path
from django.utils.functional import cached_property
from django.utils import timezone
# 修复导入错误
# from users.models import User

def post_image_path(instance, filename):
    """Define the upload path for post images"""
    # Get the file extension
    ext = Path(filename).suffix
    # Create a unique filename based on post id and title
    return f'community/images/{instance.id}_{instance.title.replace(" ", "_")[:30]}{ext}'

def post_thumbnail_path(instance, filename):
    """Define the upload path for post thumbnails"""
    # Get the file extension
    ext = Path(filename).suffix
    # Create a unique filename based on post id and title
    return f'community/thumbnails/{instance.id}_{instance.title.replace(" ", "_")[:30]}{ext}'

class Post(models.Model):
    title = models.CharField('标题', max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name='作者')
    content = models.TextField('内容')
    # 本地存储文件字段
    image = models.ImageField('图片', upload_to='community/images/', null=True, blank=True)
    thumbnail = models.ImageField('缩略图', upload_to='community/thumbnails/', null=True, blank=True)
    # 对象存储URL字段
    image_url_field = models.URLField('图片URL', max_length=500, null=True, blank=True)
    thumbnail_url_field = models.URLField('缩略图URL', max_length=500, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    likes_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True, verbose_name='点赞')
    
    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('community:post_detail', args=[str(self.id)])
    
    def like_count(self):
        return self.likes_users.count()
    
    @property
    def image_url(self):
        """返回图片URL，优先使用OSS URL通过代理访问"""
        if self.image_url_field:
            # 从OSS URL提取文件名
            filename = os.path.basename(self.image_url_field)
            # 返回代理URL
            return reverse('proxy_image', kwargs={'image_type': 'images', 'filename': filename})
        # 如果使用本地存储，还是返回直接URL
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    
    @property
    def thumbnail_url(self):
        """返回缩略图URL，优先使用OSS URL通过代理访问"""
        if self.thumbnail_url_field:
            # 从OSS URL提取文件名
            filename = os.path.basename(self.thumbnail_url_field)
            # 返回代理URL
            return reverse('proxy_image', kwargs={'image_type': 'thumbnails', 'filename': filename})
        elif self.image_url_field:
            # 如果没有缩略图但有原图，使用原图的代理URL
            filename = os.path.basename(self.image_url_field)
            return reverse('proxy_image', kwargs={'image_type': 'images', 'filename': filename})
        # 回退到本地存储
        elif self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only like a post once
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'