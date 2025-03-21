from django.db import models
from django.conf import settings
from django.urls import reverse
import base64
import os
from pathlib import Path
from django.utils.functional import cached_property
from django.utils import timezone

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
    title = models.CharField('Title', max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name='Author')
    content = models.TextField('Content')
    # Local storage file fields
    image = models.ImageField('Image', upload_to='community/images/', null=True, blank=True)
    thumbnail = models.ImageField('Thumbnail', upload_to='community/thumbnails/', null=True, blank=True)
    # Object storage URL fields
    image_url_field = models.URLField('Image URL', max_length=500, null=True, blank=True)
    thumbnail_url_field = models.URLField('Thumbnail URL', max_length=500, null=True, blank=True)
    created_at = models.DateTimeField('Created at', default=timezone.now)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    likes_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True, verbose_name='Likes')
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('community:post_detail', args=[str(self.id)])
    
    def like_count(self):
        return self.likes_users.count()
    
    @property
    def image_url(self):
        """Return image URL, prioritizing OSS URL accessed through proxy"""
        if self.image_url_field:
            # Extract filename from OSS URL
            filename = os.path.basename(self.image_url_field)
            # Return proxy URL
            return reverse('proxy_image', kwargs={'image_type': 'images', 'filename': filename})
        # If using local storage, return direct URL
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    
    @property
    def thumbnail_url(self):
        """Return thumbnail URL, prioritizing OSS URL accessed through proxy"""
        if self.thumbnail_url_field:
            # Extract filename from OSS URL
            filename = os.path.basename(self.thumbnail_url_field)
            # Return proxy URL
            return reverse('proxy_image', kwargs={'image_type': 'thumbnails', 'filename': filename})
        elif self.image_url_field:
            # If no thumbnail but have original image, use original image proxy URL
            filename = os.path.basename(self.image_url_field)
            return reverse('proxy_image', kwargs={'image_type': 'images', 'filename': filename})
        # Fall back to local storage
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