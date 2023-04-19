"""rootWEB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

from django.urls import path
from weatherApp import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #홈페이지 부분
    #메인
    path('', views.main, name = 'main'),
    #로그인
    path('login/', views.login),
    #회원가입
    path('join/', views.join),
    #로그아웃
    path('logout/', views.logout),

    #지도-날씨 API 부분
    #검색하면 날씨로 비동기 통신
    path('searchWeather/', views.searchWeather),

    #옷 추천 부분
    #검색하면 데이터베이스에서 날짜에 맞는 옷을 비동기 통신으로 전달
    path('clothRecommend/', views.clothRecommend),
    path('recommend_clothes/', views.recommend_clothes),

    #옷 위젯 클릭시 넘어가는 화면 체크박스와 연동 시키는 부분
    path('combination/', views.combination),
]

#이미지 파일 업로드 위해 추가 4월 15일 21:28
# 이미지 URL 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)