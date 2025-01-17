from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .garden import Garden
import pprint


# Create your views here.
def index(request):
    context = {}
    return render(request, 'attendance/index.html', context)


# 정원사들 리스트
def users(request):
    garden = Garden()
    users = garden.get_member()
    return JsonResponse(users, safe=False)


def user(request, user):
    garden = Garden()
    result = garden.find_attendance_by_user(user)

    output = {}
    output[user] = []

    for (date, commits) in result.items():
        output[user].append({"date":date, "commits": commits})
        print(date)

    return JsonResponse(output)


# slack_messages 수집
def collect(request):
    oldest = datetime.strptime(request.GET.get('start'), "%Y-%m-%d").timestamp()
    latest = datetime.strptime(request.GET.get('end'), "%Y-%m-%d").timestamp()

    garden = Garden()
    garden.collect_slack_messages(oldest, latest)

    return JsonResponse({})


def csv(request):
    garden = Garden()
    garden.generate_attendance_csv()

    return JsonResponse({})


# 특정일의 출석 데이터 불러오기
def get(request, date):
    garden = Garden()
    result = garden.get_attendance(datetime.strptime(date, "%Y%m%d").date())
    # pprint.pprint(result)
    return JsonResponse(result, safe=False)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# 전체 출석부 조회
def gets(request):
    garden = Garden()

    result = []

    users = garden.get_member()
    for user in users:
        attendances = garden.find_attendance_by_user(user)

        # convert key type datetime.date to string
        for key_date in list(attendances.keys()).copy():
            formatted_date = key_date.strftime("%Y-%m-%d")
            attendances[formatted_date] = attendances.pop(key_date)[0]["ts"]

        result.append({"user": user, "attendances": attendances})

    return JsonResponse(result, safe=False)