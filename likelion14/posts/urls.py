from django.urls import path
from posts.views import *

urlpatterns = [
    #path('', hello_world, name = 'hello_world'),
    #path('page', index, name='my-page'),
    #path('<int:id>', get_post_detail),

    #config/urls.py 에서 http://~~/post/ 이후에 이렇게 치면 연결됨
    path('', post_list, name = "post_list"), # Post 생성, 전체조회
    path('<int:post_id>/', post_detail, name = "post_detail"), # Post 단일조회, 수정, 삭제
    path('<int:post_id>/comments/', comment_list, name = "comment_list"), # Post의 댓글 조회
]