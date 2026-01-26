from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import Post, Comment, Like, Story, StoryImage

# ---------------- Feed (게시글 + 스토리 목록)
@login_required
def feed_view(request):
    # 내가 팔로우하는 유저들 ID 목록
    following_users = request.user.following.values_list('following', flat=True)
    
    # 1. 게시글 가져오기 (팔로우한 사람 + 내 글)
    posts = Post.objects.filter(
        Q(user__in=following_users) | Q(user=request.user)
    ).annotate(
        likes_count=Count('likes', distinct=True),
        is_liked=Exists(
            Like.objects.filter(user=request.user, post=OuterRef('pk'))
        )
    ).select_related('user').order_by('-created_at')

    # 2. 최근 24시간 이내의 스토리 가져오기
    time_threshold = timezone.now() - timedelta(hours=24)
    stories = Story.objects.filter(
        Q(user__in=following_users) | Q(user=request.user),
        created_at__gte=time_threshold
    ).select_related('user').prefetch_related('images').distinct().order_by('-created_at')

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'stories': stories
    })

# ---------------- Post CRUD
@login_required
def post_create_view(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if image:
            Post.objects.create(user=request.user, content=content, image=image)
            return redirect('posts:feed')
    return render(request, 'posts/post_form.html')

@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 상세페이지용 좋아요 수/유무 (annotate 대신 직접 계산)
    post.likes_count = post.likes.count()
    post.is_liked = post.likes.filter(user=request.user).exists()
    comments = post.comments.all().order_by('created_at')
    return render(request, 'posts/post_detail.html', {'post': post, 'comments': comments})

@login_required
def post_update_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 작성자가 아니면 권한 없음 처리 (보안)
    if post.user != request.user:
        return redirect('posts:feed')

    if request.method == 'POST':
        post.content = request.POST.get('content')
        if request.FILES.get('image'):
            post.image = request.FILES.get('image')
        post.save()
        return redirect('posts:post_detail', pk=post.pk)
    
    return render(request, 'posts/post_form.html', {'post': post})
@login_required
def post_delete_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user == request.user:
        post.delete()
    return redirect('posts:feed')

# ---------------- Story
@login_required
def story_create(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image:
            Story.objects.create(user=request.user, image=image)
            return redirect('posts:feed')
    return render(request, 'posts/story_form.html')

# 스토리 상세 보기
def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    return render(request, 'posts/story_detail.html', {'story': story})

# ---------------- Like & Comment (AJAX/Post)
@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    # 좋아요 토글 로직
    like_qs = post.likes.filter(user=user)
    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(user=user, post=post)
    
    # JsonResponse 대신 눌렀던 페이지로 다시 돌아가기
    return redirect(request.META.get('HTTP_REFERER', 'posts:feed'))

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('posts:feed')

@login_required
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
            return redirect('posts:feed') # 또는 상세페이지로 이동
            
    return render(request, 'posts/comment_form.html', {'comment': comment})

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    comment.delete()
    return redirect('posts:feed')