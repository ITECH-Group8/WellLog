from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment

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
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'community/post_detail.html', {'post': post, 'comments': comments})

@login_required
def create_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(post=post, user=request.user, content=content)
        return redirect('post_detail', post_id=post_id)
    return redirect('community_list')