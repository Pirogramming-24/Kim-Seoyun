# login/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('gpt:index')
        else:
            return render(request, 'login/login.html', {
                'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
            })

    return render(request, 'login/login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'login/signup.html', {
                'error': '비밀번호가 일치하지 않습니다.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'login/signup.html', {
                'error': '이미 존재하는 아이디입니다.'
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect('gpt:index')

    return render(request, 'login/signup.html')



def logout_view(request):
    logout(request)
    return redirect('login:login')