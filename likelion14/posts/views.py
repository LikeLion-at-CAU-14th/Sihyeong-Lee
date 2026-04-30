from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from .models import *
import json

# Create your views here.

def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello likelion-14th!"
        })
    
def index(request):
    return render(request, 'index.html')

# 게시글 단일조회(GET), 수정(PATCH), 삭제(DELETE) 로직
@require_http_methods(["GET","PATCH","DELETE"])
def post_detail(request, post_id): #127.0.0.1:8000/post/(request method)/post_id/

    if request.method == "GET": #GET 요청일 때
        post = get_object_or_404(Post, pk=post_id) #Post 테이블에서 pk=입력한 post_id인 튜플
        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "writer" : post.writer.username,
            "created_at" : post.created_at,
            "updated_at" : post.updated_at,
        }
        return JsonResponse({
            "status" : 200,
            'message' : '게시글 단일 조회 성공',
            "data": post_detail_json})
    
    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8')) #HTTP 요청의 본문을 utf-8을 통해 문자열로 변환

        post_update = get_object_or_404(Post, pk=post_id) #Post 테이블에서 pk=입력한 post_id인 튜플

        if 'title' in body:
            post_update.title = body['title']
        if 'content' in body:
            post_update.content = body['content']
        if 'status' in body:
            post_update.status = body['status']
        
        post_update.save()

        post_update_json = {
            "id" : post_update.id,
            "title" : post_update.title,
            "content" : post_update.content,
            "status" : post_update.status,
            "writer" : post_update.writer.username
        }

        return JsonResponse({
            'status': 200,
            'message' : '게시글 수정 성공',
            'data' : post_update_json
        })
    
    if request.method == "DELETE":
        post_delete = get_object_or_404(Post, pk=post_id)
        post_delete.delete()

        return JsonResponse({ #없어도 되지만 삭제됐다는 걸 보여주기위해
            'status' : 200,
            'message' : '게시글 삭제 성공',
            'data' : None
        })

# 게시글을 Post(Create), Get(Read) 하는 뷰 로직
@require_http_methods(["POST", "GET"])   #함수 데코레이터, 특정 http method 만 허용합니다
def post_list(request):

    if request.method == "POST":

        # request.body의 byte -> 문자열 -> python 딕셔너리
        body = json.loads(request.body.decode('utf-8'))

        # 프론트에게서 user id를 넘겨받는다고 가정.
				# 외래키 필드의 경우, 객체 자체를 전달해줘야하기 때문에
        # id를 기반으로 user 객체를 조회해서 가져옵니다 !
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)

        # 새로운 데이터를 DB에 생성
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            writer = user
        )

        # Json 형태 반환 데이터 생성
        new_post_json = {
            "id" : new_post.id,
            "title" : new_post.title,
            "content" : new_post.content,
            "status" : new_post.status,
            "writer" : new_post.writer.username
        }

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 생성 성공',
            'data' : new_post_json
        })

# 게시글 전체 Get(Read)
    if request.method == "GET":
        category_id = request.GET.get('category_id') #request.Get.get() : GET 요청의 쿼리스트링에서 category_id 값을 가져옵니다. (없으면 None 반환)
                                                     #()안의 'category_id'는 프론트에서 쿼리스트링으로 넘겨주는 key값입니다. 예시) http://~~/post/?category_id=1 -> category_id = 1

        if category_id:
            category = get_object_or_404(Category, pk=category_id)
            post_all = Post.objects.filter(category=category).order_by('-created_at')
            message = '카테고리별 게시글 목록 조회 성공'
        else:
            post_all = Post.objects.all()
            message = '게시글 목록 조회 성공'

        # 각 데이터를 Json 형식으로 변환하여 리스트에 저장 (여러개의 게시글 내용을 담을 거라 리스트를 이용합니다)
        post_all_json = []

        for post in post_all:
            post_json = {
                "id" : post.id,
                "title" : post.title,
                "content" : post.content,
                "status" : post.status,
                "writer" : post.writer.username,
                "created_at" : post.created_at
            }
            post_all_json.append(post_json)

        return JsonResponse({
            'status' : 200,
            'message' : message,
            'data' : post_all_json
        })
    

# 특정 게시글의 댓글을 Get(Read) 하는 뷰 로직
@require_http_methods(["GET"])   #함수 데코레이터, 특정 http method 만 허용합니다
def comment_list(request, post_id):

# 댓글 전체 조회
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id) # post_id 에 해당하는 Post 데이터 가져오기
        comment_all = Comment.objects.filter(post=post) #Comment 테이블에서 post속성이 입력한 post_id인 객체들 가져옴

        # 각 데이터를 Json 형식으로 변환하여 리스트에 저장 (여러개의 게시글 내용을 담을 거라 리스트를 이용합니다)
        comment_all_json = []

        for comment in comment_all:
            comment_json = {
                "post_id" : post.id,
                "comment_id" : comment.id,
                "content" : comment.content
            }
            comment_all_json.append(comment_json)

        return JsonResponse({
            'status' : 200,
            'message' : '댓글 목록 조회 성공',
            'data' : comment_all_json
        })

from .serializers import PostSerializer, CommentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class PostList(APIView):
    def post(self, request, format=None): #create #drf에서 콘텐츠 협상을 위해 사용
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(): #클라이언트가 보낸 데이터가 유효한지 검사
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None): #read 전체 조회
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True) #many=True: 모든 게시글을 한번에 가져옴
        return Response(serializer.data)
    
class PostDetail(APIView):
    def get(self, request, post_id): #read 단일 조회(post_id)
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, post_id): #update 전체 업데이트, patch는 일부분 업데이트
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response(
            {
                "message": "게시글이 성공적으로 삭제되었습니다.",
                "post_id": post_id
            },
            status=status.HTTP_200_OK
        )

class CommentList(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentDetail(APIView):
    def delete(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)
        return Response(
            {
                "message": "댓글이 성공적으로 삭제되었습니다.",
                "post_id": post_id,
                "comment_id": comment_id,
                "content": comment.content
            },
            status=status.HTTP_200_OK
        )