from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.main, name='main'),
    path('create/', views.create, name='create'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('update/<int:pk>/', views.update, name='update'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    
    path('ocr/', views.ocr_api, name='ocr'), 
]