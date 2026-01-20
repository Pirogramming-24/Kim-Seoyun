from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Review
import json
import requests
from django.core.paginator import Paginator
from django.db.models import Q

# ---  TMDB  ---
def parse_tmdb_movie_data(movie_data):
    genres = movie_data.get('genres', [])
    genre_str = ', '.join([g.get('name') for g in genres[:2]]) if genres else '기타'
    
    credits = movie_data.get('credits', {})
    crew = credits.get('crew', [])
    directors = [c.get('name') for c in crew if c.get('job') == 'Director']
    cast = credits.get('cast', [])
    actors = [c.get('name') for c in cast[:3]]

    release_date = movie_data.get('release_date', '')
    release_year = int(release_date[:4]) if release_date else 0
    rating = round(float(movie_data.get('vote_average', 0)) / 2, 1)

    return {
        'tmdb_id': movie_data.get('id'),
        'title': movie_data.get('title', '제목 없음'),
        'director': directors[0] if directors else '미상',
        'actor': ', '.join(actors) if actors else '미상',
        'genre': genre_str,
        'rating': rating,
        'runtime': movie_data.get('runtime', 0) or 0,
        'release_year': release_year,
        'content': movie_data.get('overview', ''),
        'poster_url': f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else "",
        'source': 'tmdb'
    }

# --- 리뷰  ---
def review_list(request):
    sort_param = request.GET.get('sort', 'latest')
    filter_param = request.GET.get('filter', 'all')
    search_query = request.GET.get('q', '') 
    

    reviews_list = Review.objects.all()


    if search_query:

        reviews_list = reviews_list.filter(
            Q(title__icontains=search_query) | 
            Q(director__icontains=search_query) |
            Q(actor__icontains=search_query)
        )

    if filter_param == 'tmdb':
        reviews_list = reviews_list.filter(source='tmdb')
    elif filter_param == 'manual':
        reviews_list = reviews_list.filter(source='manual')
    
 
    if sort_param == 'title':
        order_by = 'title'
    elif sort_param == 'rating':
        order_by = '-rating'
    elif sort_param == 'year':
        order_by = '-release_year'
    else:
        order_by = '-id'
    
    reviews_list = reviews_list.order_by(order_by)

    page = request.GET.get('page', '1')
    paginator = Paginator(reviews_list, 8)
    reviews = paginator.get_page(page)

    context = {
        'reviews': reviews,
        'current_sort': sort_param,
        'current_filter': filter_param,
        'search_query': search_query,
        'tmdb_count': Review.objects.filter(source='tmdb').count(),
        'manual_count': Review.objects.filter(source='manual').count(),
    }
    return render(request, 'reviews/review_list.html', context)

# --- 2. 리뷰 상세 ---
def review_detail(request, pk):
    review = get_object_or_404(Review, id=pk)
    return render(request, "reviews/review_detail.html", {"review": review})

# --- 3. 리뷰 작성/수정/삭제 ---
def review_create(request):
    if request.method == "POST":
        Review.objects.create(
            title=request.POST["title"],
            director=request.POST["director"],
            actor=request.POST["actor"],
            genre=request.POST["genre"],
            rating=request.POST["rating"],
            runtime=request.POST.get("runtime") or 0,
            release_year=request.POST.get("release_year") or 0,
            content=request.POST["content"],
            source='manual'
        )
        return redirect("reviews:review_list")
    return render(request, "reviews/review_create.html")

def review_update(request, pk):
    review = get_object_or_404(Review, id=pk)
    if request.method == "POST":
        review.title = request.POST["title"]
        review.director = request.POST["director"]
        review.actor = request.POST["actor"]
        review.genre = request.POST["genre"]
        review.rating = request.POST["rating"]
        review.runtime = request.POST.get("runtime") or 0
        review.release_year = request.POST.get("release_year") or 0
        review.content = request.POST["content"]
        review.save()
        return redirect("reviews:review_detail", pk=pk)
    return render(request, "reviews/review_update.html", {"review": review})

def review_delete(request, pk):
    if request.method == "POST":
        review = get_object_or_404(Review, id=pk)
        review.delete()
    return redirect("reviews:review_list")

# --- TMDB ---
def fetch_tmdb_movie_detail(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {'api_key': settings.TMDB_API_KEY, 'language': 'ko-KR', 'append_to_response': 'credits'}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except:
        return None

def auto_fill_tmdb_movies(count=40):
    current_count = Review.objects.filter(source='tmdb').count()
    needed = count - current_count
    if needed <= 0: return

    imported = 0
    page = 1
    while imported < needed and page <= 5:
        url = "https://api.themoviedb.org/3/movie/popular"
        params = {'api_key': settings.TMDB_API_KEY, 'language': 'ko-KR', 'page': page}
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code != 200: break
            movies = resp.json().get('results', [])
            for movie in movies:
                if imported >= needed: break
                if not Review.objects.filter(tmdb_id=movie['id']).exists():
                    raw_detail = fetch_tmdb_movie_detail(movie['id'])
                    if raw_detail:
                        movie_data = parse_tmdb_movie_data(raw_detail)
                        Review.objects.create(**movie_data)
                        imported += 1
            page += 1
        except:
            break

# --- 챗봇 ---
def search_reviews_by_keyword(question):
    reviews = Review.objects.all()
    keywords = question.lower().split()
    matched_reviews = []
    for review in reviews:
        score = 0
        text = f"{review.title} {review.content} {review.genre}".lower()
        for kw in keywords:
            if kw in text: score += 1
        if score > 0:
            matched_reviews.append({'review': review, 'score': score})
    matched_reviews.sort(key=lambda x: x['score'], reverse=True)
    return [item['review'] for item in matched_reviews[:5]]

def review_chatbot(request):
    return render(request, 'reviews/chatbot.html')

@csrf_exempt
def chatbot_ask(request):
    if request.method != "POST": return HttpResponseBadRequest("POST only")
    try:
        body = json.loads(request.body.decode("utf-8"))
        question = body.get("question", "").strip()
    except:
        question = request.POST.get("question", "").strip()

    related_reviews = search_reviews_by_keyword(question) or list(Review.objects.all()[:5])
    context_text = "\n".join([f"제목: {r.title}, 리뷰: {r.content}" for r in related_reviews])
    
    headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "solar-mini",
        "messages": [
            {"role": "system", "content": "너는 영화 추천 전문가야. 제공된 정보 내에서 답변해줘."},
            {"role": "user", "content": f"질문: {question}\n참고 정보:\n{context_text}"}
        ]
    }
    try:
        response = requests.post("https://api.upstage.ai/v1/solar/chat/completions", headers=headers, json=data)
        ans = response.json()['choices'][0]['message']['content']
    except:
        ans = "상담이 원활하지 않습니다."

    return JsonResponse({"answer": ans, "sources": [{"title": r.title} for r in related_reviews[:3]]})