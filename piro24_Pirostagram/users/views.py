from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm  
from posts.models import Follow, Post 

User = get_user_model()

# 회원가입
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 폼 검증이 끝나면 유저 저장 및 로그인
            user = form.save()
            login(request, user)
            return redirect('users:profile', username=user.username)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# 로그인
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('posts:feed') 
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# 로그아웃
@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

# 프로필 보기
@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all().order_by('-created_at')
    
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    followers_count = user.followers.count() 
    following_count = user.following.count()
    
    return render(request, 'users/profile.html', {
        'user_profile': user,
        'posts': user_posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

# 팔로우 / 언팔로우 토글
@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        follow_relation, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if not created:
            follow_relation.delete()
    return redirect('users:profile', username=username)

# 유저 검색
@login_required
def search_view(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)
    else:
        users = User.objects.none()
    return render(request, 'users/search.html', {'users': users, 'query': query})