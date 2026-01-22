from django.urls import path
from . import views

app_name = 'gpt'

urlpatterns = [
    path('', views.index, name='index'),
    path('image/', views.image_view, name='image'),
    path("translate/", views.translate_view, name="translate"),
    path('summarize/', views.summarize_view, name='summarize'),
    path('image/', views.image_view),
]

