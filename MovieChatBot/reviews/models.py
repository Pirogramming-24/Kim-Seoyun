from django.db import models

class Review(models.Model):
    title = models.CharField(max_length=200)  # 영화 제목
    director = models.CharField(max_length=200)  # 감독
    actor = models.CharField(max_length=200)  # 주연
    genre = models.CharField(max_length=100)  # 장르
    rating = models.DecimalField(max_digits=2, decimal_places=1)  # 별점 (0.0~5.0)
    runtime = models.IntegerField()  # 상영 시간
    release_year = models.IntegerField()  # 개봉 년도
    content = models.TextField()  # 리뷰 내용
    
    source = models.CharField(
        max_length=20, 
        choices=[('tmdb', 'TMDB'), ('manual', '직접 추가')],
        default='manual'
    )
    poster_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']