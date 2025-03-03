from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db import connection
from django.core.exceptions import PermissionDenied
import requests
import os
import oss2
from .storage import AliyunOSSStorage
from django.conf import settings

from .models import Post, Comment, Like
from .forms import PostForm, CommentForm

# Initialize OSS storage
oss_storage = AliyunOSSStorage()

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Post.objects.create(author=request.user, title=title, content=content)
        return redirect('community_list')
    return render(request, 'community/create_post.html')

def list_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/list_posts.html', {'posts': posts})

def post_detail(request, post_id):
    try:
        # Safely get post details
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        
        # Check if current user has already liked
        user_liked = False
        if request.user.is_authenticated:
            user_liked = Like.objects.filter(post=post, user=request.user).exists()
        
        # Comment form
        comment_form = CommentForm()
        
        context = {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'user_liked': user_liked,
        }
        return render(request, 'community/post_detail.html', context)
    except Exception as e:
        # Log error and return error page
        print(f"Error in post_detail view: {e}")
        return render(request, 'community/post_detail.html', {'error': str(e)})

@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(post=post, user=request.user, content=content)
        return redirect('post_detail', post_id=post_id)
    return redirect('community_list')

@login_required
def community_list(request):
    return render(request, 'community_list.html')

@login_required
def post_list(request):
    try:
        # Get all posts
        posts = Post.objects.all().order_by('-created_at')
        
        # Add count attributes for each post and check if user has liked
        for post in posts:
            post.comment_count = post.comments.count()
            # Check if current user has liked this post
            if request.user.is_authenticated:
                post.user_liked = post.likes_users.filter(id=request.user.id).exists()
            else:
                post.user_liked = False
            print(f"Post {post.id}: User like status={post.user_liked}, Like count={post.like_count()}")
        
        context = {'posts': posts}
        return render(request, 'community/post_list.html', context)
    except Exception as e:
        # Log error and return empty list
        print(f"Error in post_list view: {e}")
        return render(request, 'community/post_list.html', {'posts': [], 'error': str(e)})

@login_required
def post_create(request):
    try:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                # Create post - the save method in PostForm already handles image uploads
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                messages.success(request, 'Post published successfully!')
                return redirect('post_detail', post_id=post.id)
            else:
                # Print form errors for debugging
                print(f"Form validation errors: {form.errors}")
        else:
            form = PostForm()
        
        return render(request, 'community/post_form.html', {'form': form})
    except Exception as e:
        print(f"Error in post_create view: {e}")
        messages.error(request, f'Error creating post: {e}')
        return redirect('post_list')

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Ensure only the author can edit the post
    if post.author != request.user:
        messages.error(request, 'You do not have permission to edit this post!')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post has been updated!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
        # For the edit page, no need to display the current value of the image upload field as it's binary data
    
    return render(request, 'community/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Ensure only the author can delete the post
    if post.author != request.user:
        messages.error(request, 'You do not have permission to delete this post!')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted!')
        return redirect('post_list')
    
    return render(request, 'community/post_confirm_delete.html', {'post': post})

@login_required
@require_POST
def comment_create(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            # Check table structure
            with connection.cursor() as cursor:
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='community_comment';")
                columns = [col[0] for col in cursor.fetchall()]
                
                if 'author_id' not in columns or 'post_id' not in columns:
                    messages.error(request, 'Comment function is temporarily unavailable, please try again later.')
                    return redirect('post_detail', post_id=post_id)
            
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment published!')
        
        return redirect('post_detail', post_id=post.id)
    except Exception as e:
        print(f"Error in comment_create view: {e}")
        messages.error(request, f'Error posting comment: {e}')
        return redirect('post_list')

@login_required
@require_POST
def like_toggle(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        
        # Check if user has already liked
        if post.likes_users.filter(id=request.user.id).exists():
            # If already liked, unlike
            post.likes_users.remove(request.user)
            liked = False
        else:
            # If not liked, add like
            post.likes_users.add(request.user)
            liked = True
        
        # Get updated like count
        like_count = post.like_count()
        print(f"Like operation completed: Post ID={post_id}, User={request.user.username}, Like status={liked}, Like count={like_count}")
        
        # Return updated like count
        return JsonResponse({
            'liked': liked,
            'like_count': like_count
        })
    except Exception as e:
        print(f"Error in like_toggle view: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def proxy_image(request, image_type, filename):
    """
    Proxy view: Get image from OSS and return to browser
    Image type can be 'images' or 'thumbnails'
    """
    try:
        # Build image path in OSS
        if image_type not in ['images', 'thumbnails']:
            raise Http404("Invalid image type")
            
        # Build image path in OSS
        oss_path = f"community/{image_type}/{filename}"
        
        # Security check, ensure only community images can be accessed
        if '..' in oss_path or not oss_path.startswith('community/'):
            raise PermissionDenied("Access to this path is forbidden")
        
        response = HttpResponse()
        
        # Get cache control parameters
        cache_timeout = int(request.GET.get('cache', 86400))  # Default 24 hours
        
        # Try to get image from OSS
        try:
            # If OSS storage is valid, use OSS
            if oss_storage.valid:
                # Get authentication info
                auth = oss2.Auth(oss_storage.access_key_id, oss_storage.access_key_secret)
                bucket = oss2.Bucket(auth, oss_storage.endpoint, oss_storage.bucket_name)
                
                # Read object from OSS
                oss_object = bucket.get_object(oss_path)
                
                # Set content type
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    content_type = 'image/png'
                elif filename.lower().endswith('.gif'):
                    content_type = 'image/gif'
                else:
                    content_type = 'application/octet-stream'
                    
                # Set response headers
                response['Content-Type'] = content_type
                response['Content-Length'] = oss_object.content_length
                response['Cache-Control'] = f'max-age={cache_timeout}'
                
                # Write response body
                response.write(oss_object.read())
                return response
        except Exception as e:
            print(f"Failed to get image from OSS: {e}")
            
        # If OSS retrieval fails, try to get from local media directory
        local_path = os.path.join(settings.MEDIA_ROOT, f"community/{image_type}/{filename}")
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                # Set content type
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif filename.lower().endswith('.png'):
                    content_type = 'image/png'
                elif filename.lower().endswith('.gif'):
                    content_type = 'image/gif'
                else:
                    content_type = 'application/octet-stream'
                
                # Set response headers
                response['Content-Type'] = content_type
                response['Cache-Control'] = f'max-age={cache_timeout}'
                
                # Write response body
                response.write(f.read())
                return response
        
        # If all fails, return 404
        raise Http404("Image does not exist")
    except Exception as e:
        print(f"Image proxy error: {e}")
        raise Http404("Error retrieving image")