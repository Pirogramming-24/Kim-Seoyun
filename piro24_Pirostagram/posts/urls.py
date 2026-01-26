from django.urls import path
from . import views 

app_name = 'posts'

urlpatterns = [
    # 게시글 관련
    path('', views.feed_view, name='feed'),
    path('create/', views.post_create_view, name='post_create'),
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    path('<int:pk>/update/', views.post_update_view, name='post_update'),
    path('<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    
    # 좋아요 및 댓글 (비동기/기능성)
    path('<int:post_id>/like/', views.like_toggle, name='like_toggle'),
    path('<int:post_id>/comment/', views.comment_create, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('comment/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    
    # 스토리 관련
    path('story/<int:pk>/', views.story_detail, name='story_detail'),
    path('story/create/', views.story_create, name='story_create')
]