from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
from django.utils import timezone

from .services.ocr_service import run_ocr, parse_nutrition_info

# 1. 메인 리스트 뷰
def main(request):
    posts = Post.objects.all()
    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'posts/list.html', context=context)

# 2. 게시글 생성 뷰
def create(request):
    if request.method == 'GET':
        form = PostForm()
        return render(request, 'posts/create.html', {'form': form})
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # 유저 정보가 필수로 들어가야 하므로 commit=False 사용
            post = form.save(commit=False)
            post.user = request.user 
            post.save()
            return redirect('posts:main')
        return render(request, 'posts/create.html', {'form': form})

# 3. 상세 보기 뷰
def detail(request, pk):
    post = Post.objects.get(id=pk)
    return render(request, 'posts/detail.html', {'post': post})

# 4. 수정 뷰
def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        return render(request, 'posts/update.html', {'form': form, 'post': post})
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', pk=pk)

# 5. 삭제 뷰
def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('posts:main')

from django.views.decorators.csrf import csrf_exempt 

@csrf_exempt
def ocr_api(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        
        # 1. 텍스트 추출 (ocr_service.py)
        ocr_results = run_ocr(image) 
        
        # 2. 결과 파싱 (rules.py 혹은 ocr_service.py)
        parsed_data = parse_nutrition_info(ocr_results)

        return JsonResponse({
            "status": "success",
            "data": parsed_data, # { 'kcal': 150, 'carbohydrate': 20, ... }
        })

    return JsonResponse({"status": "fail", "message": "잘못된 요청입니다."}, status=400)