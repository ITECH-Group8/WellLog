from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db import connection

from .models import Post, Comment, Like
from .forms import PostForm, CommentForm

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Post.objects.create(user=request.user, title=title, content=content)
        return redirect('community_list')
    return render(request, 'community/create_post.html')

def list_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/list_posts.html', {'posts': posts})

def post_detail(request, post_id):
    try:
        # 尝试安全地获取帖子详情
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        
        # 检查当前用户是否已经点赞
        user_liked = False
        if request.user.is_authenticated:
            user_liked = Like.objects.filter(post=post, user=request.user).exists()
        
        # 评论表单
        comment_form = CommentForm()
        
        context = {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'user_liked': user_liked,
        }
        return render(request, 'community/post_detail.html', context)
    except Exception as e:
        # 记录错误并返回错误页面
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

def post_list(request):
    try:
        # 获取所有帖子
        posts = Post.objects.all().order_by('-created_at')
        
        # 为每个帖子添加计数属性
        for post in posts:
            post.like_count = post.total_likes()
            post.comment_count = post.total_comments()
        
        context = {'posts': posts}
        return render(request, 'community/post_list.html', context)
    except Exception as e:
        # 记录错误并返回空列表
        print(f"Error in post_list view: {e}")
        return render(request, 'community/post_list.html', {'posts': [], 'error': str(e)})

@login_required
def post_create(request):
    try:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                # 创建帖子 - PostForm中的save方法已处理图片上传
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                messages.success(request, '帖子发布成功！')
                return redirect('post_detail', post_id=post.id)
        else:
            form = PostForm()
        
        return render(request, 'community/post_form.html', {'form': form})
    except Exception as e:
        print(f"Error in post_create view: {e}")
        messages.error(request, f'创建帖子时发生错误: {e}')
        return redirect('post_list')

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # 确保只有作者可以编辑帖子
    if post.author != request.user:
        messages.error(request, '您没有权限编辑此帖子！')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '帖子已更新！')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
        # 对于编辑页面不需要显示图片上传字段的当前值，因为它是二进制数据
    
    return render(request, 'community/post_form.html', {'form': form, 'post': post})

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # 确保只有作者可以删除帖子
    if post.author != request.user:
        messages.error(request, '您没有权限删除此帖子！')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '帖子已删除！')
        return redirect('post_list')
    
    return render(request, 'community/post_confirm_delete.html', {'post': post})

@login_required
@require_POST
def comment_create(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            # 检查表结构
            with connection.cursor() as cursor:
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='community_comment';")
                columns = [col[0] for col in cursor.fetchall()]
                
                if 'author_id' not in columns or 'post_id' not in columns:
                    messages.error(request, '评论功能暂时不可用，请稍后再试。')
                    return redirect('post_detail', post_id=post_id)
            
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '评论已发布！')
        
        return redirect('post_detail', post_id=post.id)
    except Exception as e:
        print(f"Error in comment_create view: {e}")
        messages.error(request, f'发表评论时发生错误: {e}')
        return redirect('post_list')

@login_required
@require_POST
def like_toggle(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        
        # 检查表结构
        with connection.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='community_like';")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'user_id' not in columns or 'post_id' not in columns:
                return JsonResponse({'error': '点赞功能暂时不可用，请稍后再试。'}, status=400)
        
        # 检查用户是否已点赞
        like = Like.objects.filter(post=post, user=request.user).first()
        
        if like:
            # 如果已点赞，取消点赞
            like.delete()
            liked = False
        else:
            # 如果未点赞，添加点赞
            Like.objects.create(post=post, user=request.user)
            liked = True
        
        # 返回更新后的点赞数
        return JsonResponse({
            'liked': liked,
            'like_count': post.total_likes()
        })
    except Exception as e:
        print(f"Error in like_toggle view: {e}")
        return JsonResponse({'error': str(e)}, status=500)