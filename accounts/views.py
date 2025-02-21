from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 自动登录
            login(request, user)
            return redirect('home')  # 注册成功后跳转主页
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': '用户名或密码错误'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')