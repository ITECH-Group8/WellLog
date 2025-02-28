from django.urls import path
from .views import login_view, register_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),  # 登录页面
    path("register/", register_view, name="register"),  # 注册页面
    path("logout/", logout_view, name="logout"),  # 退出登录
]
