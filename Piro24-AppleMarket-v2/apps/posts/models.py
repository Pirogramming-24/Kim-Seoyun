from django.db import models
from django.utils import timezone
from apps.users.models import User

class Post(models.Model):
    title = models.CharField('제목', max_length=20)
    content = models.TextField('내용')
    region = models.CharField('지역', max_length=20)
    user = models.ForeignKey(User, verbose_name='작성자', on_delete=models.CASCADE)
    price = models.IntegerField('가격', default=1000)
    
    photo = models.ImageField('이미지', blank=True, upload_to='posts/%Y%m%d')
    nutrition_photo = models.ImageField('영양 성분 이미지', blank=True, upload_to='posts/%Y%m%d')

    kcal = models.FloatField('칼로리', default=0, null=True, blank=True)
    carbohydrate = models.FloatField('탄수화물(g)', default=0, null=True, blank=True)
    protein = models.FloatField('단백질(g)', default=0, null=True, blank=True)
    fat = models.FloatField('지방(g)', default=0, null=True, blank=True)

    sort_hashtag = models.CharField('상품 종류 해시 태그', max_length=50, blank=True)

    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True) 

    def __str__(self):
        return self.title