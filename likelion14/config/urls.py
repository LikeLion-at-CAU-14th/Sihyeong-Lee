"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from posts.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls')), #http://127.0.0.1:8000/posts/ url은 post관련 view에 해당!! #rest위해 복수형으로
    path('categories/', include('posts.urls')), #categories로 접속, posts, categories 둘 다 posts.urls로 접속해서 중첩생김
]
