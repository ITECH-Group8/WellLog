from django import forms
from .models import Post, Comment
from django.core.files.base import ContentFile
from PIL import Image
import io
import uuid
import os
from .storage import AliyunOSSStorage

# 创建OSS存储实例
oss_storage = AliyunOSSStorage()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入标题'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入内容', 'rows': 5}),
        }
        labels = {
            'title': '标题',
            'content': '内容',
            'image': '图片',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        image = self.cleaned_data.get('image')
        
        if image:
            # 打开图片进行处理
            img = Image.open(image)
            
            # 将RGBA转换为RGB以避免保存问题
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 调整大图尺寸
            max_width = 1200
            if img.width > max_width:
                width_percent = max_width / float(img.width)
                height = int(float(img.height) * width_percent)
                img = img.resize((max_width, height), Image.LANCZOS)
            
            # 生成唯一的文件名
            image_id = uuid.uuid4().hex
            original_name = os.path.splitext(image.name)[0]
            file_extension = '.jpg'
            
            # 保存大图到IO缓冲区
            large_io = io.BytesIO()
            img.save(large_io, format='JPEG', quality=80)
            large_io.seek(0)
            
            # 尝试上传到阿里云OSS
            image_path = f"community/images/{image_id}_{original_name}{file_extension}"
            oss_url = oss_storage.upload_image(large_io, image_path)
            
            if oss_url:
                # 如果上传到OSS成功，保存URL并清空本地字段
                instance.image_url_field = oss_url
                instance.image = None  # 清空本地字段
                print(f"图片已上传到OSS: {oss_url}")
            else:
                # 回退到本地存储
                instance.image.save(f"{original_name}{file_extension}", ContentFile(large_io.getvalue()), save=False)
                instance.image_url_field = None  # 清空OSS字段
            
            # 创建缩略图
            thumb_width = 300
            width_percent = thumb_width / float(img.width)
            height = int(float(img.height) * width_percent)
            thumb_img = img.resize((thumb_width, height), Image.LANCZOS)
            
            # 保存缩略图到IO缓冲区
            thumb_io = io.BytesIO()
            thumb_img.save(thumb_io, format='JPEG', quality=70)
            thumb_io.seek(0)
            
            # 尝试上传缩略图到阿里云OSS
            thumb_path = f"community/thumbnails/thumb_{image_id}_{original_name}{file_extension}"
            thumb_oss_url = oss_storage.upload_image(thumb_io, thumb_path)
            
            if thumb_oss_url:
                # 如果上传到OSS成功，保存URL并清空本地字段
                instance.thumbnail_url_field = thumb_oss_url
                instance.thumbnail = None  # 清空本地字段
                print(f"缩略图已上传到OSS: {thumb_oss_url}")
            else:
                # 回退到本地存储
                instance.thumbnail.save(f"thumb_{original_name}{file_extension}", ContentFile(thumb_io.getvalue()), save=False)
                instance.thumbnail_url_field = None  # 清空OSS字段
        
        if commit:
            instance.save()
        
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '写下你的评论...', 'rows': 3}),
        }
        labels = {
            'content': '',
        } 