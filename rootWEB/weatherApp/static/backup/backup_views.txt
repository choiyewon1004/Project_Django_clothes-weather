from django.shortcuts import render, redirect
from .models import *
import csv

#비동기 통신 모듈
from django.http    import JsonResponse

# page 기능 도입
from django.core.paginator import Paginator

# 날씨
import requests
import json
import math
from datetime import datetime, timedelta, date
from urllib.parse import urlencode, quote_plus


# Create your views here.

#홈페이지 부분
#첫 페이지
#로그인 시 main으로 접속하면 yIndex.html로 보냄

def main(request) :
    #clothes_insert(request)
    #user_insert(request)

    print(">>>>>> debug client path : login/ login(), render login.html")
    #로그인 세션 유지 바꿔야함
    if request.session.get('session_user_id'):
        print(">>>>>> debug, session exists")
        context = {}
        context['id'] = request.session['session_user_id']
        context['name'] = request.session['session_name']
        return render(request, 'index.html', context)

    return render(request, 'login.html')

#로그인 구현 및 세션(id, pwd, name) 전송
def login(request) :
    print(">>>>>> debug client path : login/ login(), render home.html")
    id  = request.POST['login_id']

    pwd = request.POST['login_password']

    print(">>>>>> debug, params ", id, pwd)

    try:
        user = user_tbl.objects.get(user_id=id, user_pwd=pwd)
        request.session['session_user_id'] = user.user_id
        request.session['session_name'] = user.user_name

        context = {}
        context['id'] = request.session['session_user_id']
        context['name'] = request.session['session_name']

        return render(request, 'index.html', context)
    except:
        pass
        return render(request, 'login.html')


#회원가입
def join(request) :
    print(">>>>>> debug client path : join/ join(), redirect main.html")
    id      = request.POST['join_id']
    pwd     = request.POST['join_password']
    name    = request.POST['join_name']

    user_tbl(user_id=id, user_pwd=pwd, user_name=name).save()

    return redirect('main')


#index.html 오른쪽 icon 에서 logout 기능 구현
def logout(request) :
    print(">>>>>> debug client path : logout/ logout(), redirect login.html")
    request.session['session_user_id'] = {}
    request.session['session_name'] = {}
    return redirect('main')


#날씨-지도 API 구현 부분
#검색하면 날씨 비동기 통신 연결
def searchWeather(request) :
    print(">>>>>> debug client path: searchWeather/ searchWeather(), ajax JsonResponse")

    lat = float(request.POST.get('lat'))
    lon = float(request.POST.get('lng'))
    print(">>>>>> debug, params = ", lat, lon)

    Re = 6371.00877  ##  지도반경
    grid = 5.0  ##  격자간격 (km)
    slat1 = 30.0  ##  표준위도 1
    slat2 = 60.0  ##  표준위도 2
    olon = 126.0  ##  기준점 경도
    olat = 38.0  ##  기준점 위도
    xo = 210 / grid  ##  기준점 X좌표
    yo = 675 / grid  ##  기준점 Y좌표
    first = 0

    PI = math.asin(1.0) * 2.0
    DEGRAD = PI / 180.0
    RADDEG = 180.0 / PI

    re = Re / grid
    slat1 = slat1 * DEGRAD
    slat2 = slat2 * DEGRAD
    olon = olon * DEGRAD
    olat = olat * DEGRAD

    sn = math.tan(PI * 0.25 + slat2 * 0.5) / math.tan(PI * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(PI * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(PI * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    first = 1

    ra = math.tan(PI * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > PI:
        theta -= 2.0 * PI
    if theta < -PI:
        theta += 2.0 * PI
    theta *= sn
    x = (ra * math.sin(theta)) + xo
    y = (ro - ra * math.cos(theta)) + yo
    grid_x = int(x + 1.5)
    grid_y = int(y + 1.5)

    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

    serviceKeyDecoded = "a1+ueyWqfojp8TLmo3eE/fyZKd23AQldV28JjM7odiUWiqkSyv/3G//rOxAeJLxdf74/0b5TYuXUBn0//pywOw=="  # 공공데이터 포털에서 생성된 본인의 서비스 키를 복사 / 붙여넣기
    # 공데이터 포털에서 제공하는 서비스키는 이미 인코딩된 상태이므로, 디코딩하여 사용해야 함

    now = datetime.now()

    today = datetime.today().strftime("%Y%m%d")
    y = date.today() - timedelta(days=1)
    yesterday = y.strftime("%Y%m%d")
    nx = grid_x
    ny = grid_y
    Base = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']

    # base_time와 base_date 구하는 함수 (30분단위의 자료를 매시각 45분이후 호출하므로 다음과 같은 if 설정)
    if now.minute < 45:
        if now.hour == 0:
            base_time = Base[-1]
            base_date = yesterday
        else:
            pre_hour = now.hour - 1

            if pre_hour < 10:
                base_time = "0" + str(pre_hour) + "00"
            else:
                base_time = str(pre_hour) + "00"
            base_date = today
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "00"
        else:
            base_time = str(now.hour) + "00"
        base_date = today
    current_time = base_time[0:2] + '00'

    print(base_time, base_date)
    print("if문 직전" + base_time)
    print(type(base_time))
    if base_time in ["0100"]:
        base_time = Base[-1]
        base_date = yesterday
        print("1번" + base_time)
    if base_time in ['0200', "0300"]:
        base_time = Base[0]
        print("2번" + base_time)
    if base_time in ['0600', '0700']:
        base_time = Base[1]
        print("3번" + base_time)
    if base_time in ['0900', '1000']:
        base_time = Base[2]

    if base_time in ['1200', '1300']:
        base_time = Base[3]

    if base_time in ['1500', '1600']:
        base_time = Base[4]

    if base_time in ['1800', '1900']:
        base_time = Base[5]

    if base_time in ['2100', '2200']:
        base_time = Base[6]

    if base_time in ['2400']:
        base_time = Base[7]

    print('요청para base_time값' + base_time)
    queryParams = {'serviceKey': serviceKeyDecoded, 'pageNo': '1', 'numOfRows': '1000', 'dataType': 'JSON',
                   'base_date': base_date, 'base_time': base_time, 'nx': nx, 'ny': ny}

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)

    res = requests.get(url, params=queryParams, verify=False)
    res_json = json.loads(res.content)

    items = res_json["response"]['body']['items']

    weather_data = dict()

    for item in items['item']:

        if item['category'] == 'TMP' and item['baseDate'] == base_date and item['fcstTime'] == current_time:
            weather_data['tmp'] = item['fcstValue']
        if item['category'] == 'POP' and item['baseDate'] == base_date and item['fcstTime'] == current_time:
            weather_data['percent'] = item['fcstValue']
        if item['category'] == 'REH' and item['baseDate'] == base_date and item['fcstTime'] == current_time:
            weather_data['hum'] = item['fcstValue']

        if item['category'] == 'SKY' and item['baseDate'] == base_date and item['fcstTime'] == current_time:
            if item['fcstValue'] == '1':
                weather_data['sky'] = '맑음'
                weather_data['img'] = 'free-icon-sun-7755606.png'
            elif item['fcstValue'] == '3':
                weather_data['sky'] = '구름많음'
                weather_data['img'] = 'free-icon-bright-9477120.png'
            elif item['fcstValue'] == '4':
                weather_data['sky'] = '흐림'
                weather_data['img'] = 'free-icon-rainy-7198663.png'

        if item['category'] == 'TMX' and item['baseDate'] == base_date:
            weather_data['max'] = item['fcstValue']

        if item['category'] == 'TMN' and item['baseDate'] == base_date:
            weather_data['min'] = item['fcstValue']

        if item['category'] == 'WSD' and item['baseDate'] == base_date:
            weather_data['wind'] = item['fcstValue']

    weather_data['time'] = now

    context = {'weather': weather_data}
    # context처럼 dict타입으로 넣어도 되나????
    # response_json =[] 꼭 안써도 됨
    return JsonResponse(context, safe=False)


#옷 추천 부분
#검색하면 데이터베이스에서 날짜에 맞는 옷을 비동기 통신으로 전달
def clothRecommend(request) :
    print(">>>>>> debug client path: clothRecommend/ clothRecommend(), ajax JsonResponse")

    month = int(request.POST.get('month'))

    pngs = CLOTHES_INFO.objects.filter(CLOTHES_MON=month).values( 'CLOTHES_IDX', 'CLOTHES_PNG')

    print(pngs)

    length = len(pngs)
    print("pngs 길이 =", len(pngs))
    src = {}

    print(src)

    context = {'select_list': pngs}
    print(">>>>>> debug, params = ", month)
    response_json = []


    return JsonResponse(response_json, safe=False)

def combination(request) :
    print(">>>>>> debug client path: combination/ combination() render yIndex.html")

    selects = CLOTHES_INFO.objects.filter(CLOTHES_MON=4)

    paginator = Paginator(selects, 9)
    page = int(request.GET.get('page', 1))
    select_list = paginator.get_page(page)

    context = {'selects': select_list}

    return render(request, 'yIndex.html', context)


# 데이터 삽입 부분
def clothes_insert(request):

    path = 'C:/Users/esthe/0.project/weather_clothe/code/rootWEB/weatherApp/static/csv/final_clothes_csv.csv'
    file = open(path, 'r',encoding='UTF8')
    reader2 = csv.reader(file)

    list = []

    for row in reader2:
        list.append(CLOTHES_INFO(
            CLOTHES_IDX=row[0], CLOTHES_MON=row[1], CLOTHES_PNG=row[2], CLOTHES_LOC=row[3],
            CLOTHES_SHIRT_SHORT=row[4], CLOTHES_SHIRT_LONG=row[5], CLOTHES_SHIRT_SWEAT=row[6], CLOTHES_SWEATER=row[7], CLOTHES_SHIRT=row[8],
            CLOTHES_BLOUS=row[9], CLOTHES_ONEPICE=row[10], CLOTHES_NEET=row[11], CLOTHES_SHIRT_POLO=row[12], CLOTHES_KARDIGUN=row[13],
            CLOTHES_JUMPER=row[14], CLOTHES_JACKET=row[15], CLOTHES_COAT=row[16], CLOTHES_PADDING=row[17], CLOTHES_JEANS=row[18],
            CLOTHES_PANTS_WINTER=row[19],  CLOTHES_PANTS_SUMMER=row[20], CLOTHES_SKERT=row[21], CLOTHES_PANTS_CAGO=row[22], CLOTHES_SHOOSE_GUDU=row[23],
            CLOTHES_SHOOSE_RUNNING=row[24], CLOTHES_SHOOSE_SNIKERS=row[25], CLOTHES_SHOOSE_SANDAL=row[26], CLOTHES_SHOOSE_WAKER=row[27],
            CLOTHES_SHOOSE_BOOTS=row[28], CLOTHES_1=row[29], CLOTHES_2=row[30], CLOTHES_3=row[31],CLOTHES_4=row[32])
        )
    print(list)

    CLOTHES_INFO.objects.bulk_create(list)

    pass

def user_insert(request):

    path = 'C:/Users/esthe/0.project/weather_clothe/code/rootWEB/weatherApp/static/csv/user.csv'
    file = open(path, 'r',encoding='UTF8')
    reader2 = csv.reader(file)

    list = []

    for row in reader2:
        list.append(user_tbl(
            user_id = row[1], user_pwd = row[2], user_name = row[1])
        )
    print(list)

    user_tbl.objects.bulk_create(list)

    pass
