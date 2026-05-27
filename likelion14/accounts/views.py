from django.shortcuts import render
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from config.permissions import Isdaytime

# Create your views here.
class RegisterView(APIView):
    permission_classes = [Isdaytime]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        # 유효성 검사 
        if serializer.is_valid(raise_exception=True):
            
            # 유효성 검사 통과 후 객체 생성
            user = serializer.save()

            # user에게 refresh,access token 발급
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "user": serializer.data,
                    "message": "register success!",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }, 
                },
                status=status.HTTP_201_CREATED,
            )
            return res
        
# 로그인 담당 view
class AuthView(APIView):
    permission_classes = [Isdaytime]
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        
        # 유효성 검사
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']

            # user에게 refresh token 발급
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "message": "login success!",
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }, 
                },
                status=status.HTTP_200_OK,
            )

            res.set_cookie("access_token", access_token, httponly=True)
            res.set_cookie("refresh_token", refresh_token, httponly=True)
            return res
        
        # 유효성 검사 실패 시 오류 반환
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

class LogoutView(APIView):
    permission_classes = [Isdaytime]
    permission_classes = [IsAuthenticated] # 너 로그인한 사용자 맞아? 를 검사하는 permission

    def post(self, request):
        logout(request)
        return Response({"message": "logout success!"}, status=status.HTTP_200_OK)
    

from config.settings import get_secret

# 구글 소셜로그인
GOOGLE_REDIRECT = get_secret("GOOGLE_REDIRECT")
GOOGLE_CALLBACK_URI = get_secret("GOOGLE_CALLBACK_URI")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = get_secret("GOOGLE_SECRET")
GOOGLE_SCOPE = get_secret("GOOGLE_SCOPE")

from django.shortcuts import redirect
from json import JSONDecodeError
from django.http import JsonResponse
import requests 

def google_login(request): # 구글 로그인 페이지로 리다이렉트
    return redirect(f"{GOOGLE_REDIRECT}?client_id={GOOGLE_CLIENT_ID}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={GOOGLE_SCOPE}")

# 인가 코드를 받아 로그인 처리
def google_callback(request):
    code = request.GET.get("code")

    if code is None: # 인가 코드가 없는 경우 오류 반환
        return JsonResponse({"error": "Authorization code error."}, status=status.HTTP_400_BAD_REQUEST)
        #Response 대신 JsonResponse를 사용하는 이유: 프론트엔드에서 응답을 JSON 형태로 받기를 기대하기 때문입니다. Response는 DRF에서 제공하는 클래스이고, JsonResponse는 Django에서 제공하는 클래스입니다. JsonResponse는 자동으로 데이터를 JSON으로 직렬화하여 반환해주기 때문에, 프론트엔드에서 쉽게 처리할 수 있습니다.
    token_req = requests.post( #구글로 authorization code를 access token으로 바꿔달라고 요청
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_CALLBACK_URI,
        },
        timeout=10,
    )
    token_req_json = token_req.json()
    google_access_token = token_req_json.get("access_token")

    if token_req.status_code != 200 or google_access_token is None:
        return JsonResponse(
            {"status": 400, "message": "Failed to get access token", "detail": token_req_json},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {google_access_token}"},
        timeout=10,
    )

    if user_info_response.status_code != 200:
        return JsonResponse(
            {"status": 400, "message": "Failed to get user info"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_info = user_info_response.json()
    email = user_info.get("email")
    username = user_info.get("name") 
    # or user_info.get("given_name")
    # if not username and email:
    #     username = email.split("@")[0]
    # if not username:
    #     username = user_info.get("sub")

    data = {
        "username": username,
        "email": email,
    }

    serializer = OAuthSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data["user"]
        access_token = serializer.validated_data["access_token"]
        refresh_token = serializer.validated_data["refresh_token"]

        res = JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "message": "login success",
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        res.set_cookie("access-token", access_token, httponly=True)
        res.set_cookie("refresh-token", refresh_token, httponly=True)
        return res
