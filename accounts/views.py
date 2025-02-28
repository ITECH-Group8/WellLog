from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout

# 用户注册
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 注册后自动登录
            return redirect("home")  # 登录后跳转主页
    else:
        form = UserCreationForm()
    return render(request, "account/register.html", {"form": form})

# 用户登录
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # 登录成功后跳转
        else:
            return render(request, "account/login.html", {"error": "Invalid username or password"})
    return render(request, "account/login.html")

# 用户登出
def logout_view(request):
    logout(request)
    return redirect("login")
