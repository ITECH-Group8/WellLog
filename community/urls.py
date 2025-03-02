from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='community_list'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('posts/<int:post_id>/like/', views.like_toggle, name='like_toggle'),
] 