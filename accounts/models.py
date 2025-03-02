from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.utils.safestring import mark_safe
import os

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username if self.username else self.email
    
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            # 如果用户名为空，使用邮箱前缀作为默认用户名
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

def get_avatar_upload_path(instance, filename):
    # 生成头像上传路径: avatars/user_<id>/<filename>
    return os.path.join('avatars', f'user_{instance.user.id}', filename)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=get_avatar_upload_path, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            # 基于用户名首字母生成默认头像
            return self.get_default_avatar()
    
    def get_default_avatar(self):
        colors = [
            '#007bff', '#6610f2', '#6f42c1', '#e83e8c', '#dc3545',
            '#fd7e14', '#28a745', '#20c997', '#17a2b8', '#343a40'
        ]
        bg_colors = [
            '#f8f9fa', '#e9ecef', '#dee2e6', '#cff4fc', '#d1e7dd',
            '#fff3cd', '#f8d7da', '#e8d4f8', '#d6d8db', '#eaf5fb'
        ]
        
        # 基于用户名确定颜色索引
        username = self.user.username if self.user.username else 'User'
        color_index = sum(ord(c) for c in username) % len(colors)
        bg_index = (color_index + 3) % len(bg_colors)  # 添加偏移以避免颜色太接近
        
        # 获取用户名首字母（大写）
        letter = username[0].upper() if username else 'U'
        
        # 返回静态SVG文件路径，或使用data URI
        svg_code = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
            <rect width="200" height="200" fill="{bg_colors[bg_index]}" />
            <text x="100" y="125" font-size="100" text-anchor="middle" fill="{colors[color_index]}">{letter}</text>
        </svg>
        """
        # 使用数据URI
        import base64
        svg_base64 = base64.b64encode(svg_code.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"

# 信号接收器，用于在创建用户时自动创建关联的Profile
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()