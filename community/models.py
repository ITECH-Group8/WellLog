from django.db import models
from django.conf import settings
from django.urls import reverse
import base64
from django.utils.html import mark_safe

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    # Store image as binary data
    image = models.BinaryField(blank=True, null=True)
    image_type = models.CharField(max_length=20, blank=True, null=True)  # Store MIME type (e.g. image/jpeg)
    # Add thumbnail field for list page display
    thumbnail = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])
    
    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
    
    @property
    def image_url(self):
        # Return original image base64 encoding for detail page
        if self.image and self.image_type:
            return f"data:{self.image_type};base64,{base64.b64encode(self.image).decode('utf-8')}"
        return None
    
    @property
    def thumbnail_url(self):
        # Return thumbnail base64 encoding for list page
        if self.thumbnail and self.image_type:
            return f"data:{self.image_type};base64,{base64.b64encode(self.thumbnail).decode('utf-8')}"
        elif self.image and self.image_type:
            # Fall back to original image if no thumbnail
            return self.image_url
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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only like a post once
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'