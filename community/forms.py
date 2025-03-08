from django import forms
from .models import Post, Comment
from django.core.files.base import ContentFile
from PIL import Image
import io
import uuid
import os
from .storage import AliyunOSSStorage

# Create OSS storage instance
oss_storage = AliyunOSSStorage()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter content', 'rows': 5}),
        }
        labels = {
            'title': 'Title',
            'content': 'Content',
            'image': 'Image',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        image = self.cleaned_data.get('image')
        
        if image:
            # Open image for processing
            img = Image.open(image)
            
            # Convert RGBA to RGB to avoid saving issues
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Adjust large image size
            max_width = 1200
            if img.width > max_width:
                width_percent = max_width / float(img.width)
                height = int(float(img.height) * width_percent)
                img = img.resize((max_width, height), Image.LANCZOS)
            
            # Generate unique filename
            image_id = uuid.uuid4().hex
            original_name = os.path.splitext(image.name)[0]
            file_extension = '.jpg'
            
            # Save large image to IO buffer
            large_io = io.BytesIO()
            img.save(large_io, format='JPEG', quality=80)
            large_io.seek(0)
            
            # Try uploading to Aliyun OSS
            image_path = f"community/images/{image_id}_{original_name}{file_extension}"
            oss_url = oss_storage.upload_image(large_io, image_path)
            
            if oss_url:
                # If upload to OSS succeeded, save URL and clear local field
                instance.image_url_field = oss_url
                instance.image = None  # Clear local field
                print(f"Image uploaded to OSS: {oss_url}")
            else:
                # Fall back to local storage
                instance.image.save(f"{original_name}{file_extension}", ContentFile(large_io.getvalue()), save=False)
                instance.image_url_field = None  # Clear OSS field
            
            # Create thumbnail
            thumb_width = 300
            width_percent = thumb_width / float(img.width)
            height = int(float(img.height) * width_percent)
            thumb_img = img.resize((thumb_width, height), Image.LANCZOS)
            
            # Save thumbnail to IO buffer
            thumb_io = io.BytesIO()
            thumb_img.save(thumb_io, format='JPEG', quality=70)
            thumb_io.seek(0)
            
            # Try uploading thumbnail to Aliyun OSS
            thumb_path = f"community/thumbnails/thumb_{image_id}_{original_name}{file_extension}"
            thumb_oss_url = oss_storage.upload_image(thumb_io, thumb_path)
            
            if thumb_oss_url:
                # If upload to OSS succeeded, save URL and clear local field
                instance.thumbnail_url_field = thumb_oss_url
                instance.thumbnail = None  # Clear local field
                print(f"Thumbnail uploaded to OSS: {thumb_oss_url}")
            else:
                # Fall back to local storage
                instance.thumbnail.save(f"thumb_{original_name}{file_extension}", ContentFile(thumb_io.getvalue()), save=False)
                instance.thumbnail_url_field = None  # Clear OSS field
        
        if commit:
            instance.save()
        
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your comment...', 'rows': 3}),
        }
        labels = {
            'content': '',
        } 