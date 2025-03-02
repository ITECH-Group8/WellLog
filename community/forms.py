from django import forms
from .models import Post, Comment
import imghdr
from PIL import Image
from io import BytesIO

class PostForm(forms.ModelForm):
    # Add a temporary ImageField for form processing
    image_upload = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}), label='Image')
    
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your fitness journey and experiences...', 'rows': 5}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Process image upload
        image_upload = self.cleaned_data.get('image_upload')
        if image_upload:
            # Compress image
            img = Image.open(image_upload)
            
            # Calculate appropriate scale ratio, keeping large images no wider than 1200px
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert image to RGB mode (avoid RGBA mode issues)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Save compressed image in JPEG format (80% quality)
            output = BytesIO()
            img.save(output, format='JPEG', quality=80, optimize=True)
            output.seek(0)
            
            # Read compressed image binary data
            instance.image = output.getvalue()
            instance.image_type = 'image/jpeg'
            
            # Create thumbnail - resize to 300px width for list display
            thumbnail_size = (300, int(300 * img.height / img.width))
            thumbnail = img.resize(thumbnail_size, Image.LANCZOS)
            thumbnail_output = BytesIO()
            thumbnail.save(thumbnail_output, format='JPEG', quality=70, optimize=True)
            thumbnail_output.seek(0)
            instance.thumbnail = thumbnail_output.getvalue()
        
        if commit:
            instance.save()
        
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your comment here...', 'rows': 3}),
        }
        labels = {
            'content': '',
        } 