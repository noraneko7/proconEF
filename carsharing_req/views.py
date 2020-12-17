from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from .models import CarsharUserModel, UsageModel
from .forms import CarsharUserCreateForm
from accounts .models import CustomUser
from parking_req .models import *
from owners_req .models import HostUserModel
from carsharing_booking .models import BookingModel
from parking_booking .models import ParkingBookingModel
import json, datetime
from django.core.mail import EmailMessage

# Create your views here.

# ゲスト/ユーザ 判定
def index(request):
    querySet = CarsharUserModel.objects.filter(email__contains = request.user.email)
    if querySet.first() is None:
        print('no data')
        return redirect(to='carsharing_req:create')
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
    else:
        print(request.user.email)
    return redirect(to='carsharing_req:set_session')

# user_idをSESSIONに格納・オーナー登録済か判定用flagをSESSIONに格納
def set_session(request):
    data = CarsharUserModel.objects.get(email=request.user.email)
    request.session['user_id'] = data.id
    paking_data = ParkingUserModel.objects.filter(user_id=data.id)
    if paking_data.first() is None:
        request.session['parking_flag'] = False
    else:
        request.session['parking_flag'] = True

    owner_data = HostUserModel.objects.filter(user_id=data.id)
    if owner_data.first() is None:
        request.session['owner_flag'] = False
    else:
        request.session['owner_flag'] = True
    check_usage_obj = checkUsage(request.session['user_id'])
    if check_usage_obj == None:
        print('ok')
    else:
        surveyMail(request, check_usage_obj)
        saveUsage(request, check_usage_obj)

    return redirect(to='carsharing_req:index')


# 説明ページ(HTML)ルーティング
def pages(request, num, page):
    if num == 1:
        if page == 0:
            return render(request, 'page/user_car.html')
        elif page == 1:
            return render(request, 'page/user_car_1.html')
        elif page == 3:
            return render(request, 'page/user_car_3.html')
    elif num == 2:
        return render(request, 'page/user_parking.html')
    elif num == 3:
        return render(request, 'page/owner_car.html')
    elif num == 4:
        return render(request, 'page/owner_parking.html')
    elif num == 0:
        pass
    else:
        return redirect(to='carsharing_req:index')


class CarsharUserInfo(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'Hello World!',
            'message': 'Not found your data.<br>Please send your profile.',
            'form': CarsharUserCreateForm(),
            'link': 'other',
        }
    
    def get(self, request):
        if str(request.user) == "AnonymousUser":
            print('ゲスト')
        else:
            print(request.user)
        # return render(request, 'carsharing_req/index.html', self.params)
        return render(request, 'carsharing_req/top.html', self.params)
    
    def post(self, request):
        msg = 'Your name is <b>' + request.POST['name'] + \
            '(' + request.POST['age'] + \
            ')</b><br>Your mail address is <b>' + request.POST['email'] + \
            '</b><br>Thank you send to me!'
        self.params['message'] = msg
        self.params['form'] = CarsharUserCreateForm(request.POST)
        return render(request, 'carsharing_req/index.html', self.params)

def carsharuserdata(request):
    data = CarsharUserModel.objects.get(id=request.session['user_id'])
    data2 = CustomUser.objects.get(email=request.user.email)
    params = {
        'title': '個人登録情報確認',
        'message': 'ユーザ情報',
        'data': data,
        'data2': data2,
    }
    return render(request, 'carsharing_req/userdata.html', params)


# class CarsharUserSendMail(generic.FormView):

#     template_name = "carsharing_req/index.html"
#     form_class = CarsharUserCreateForm
#     success_url = reverse_lazy('carsharing_req:index')


#     def form_valid(self, form):
#         form.send_email()
#         messages.success(self.request, 'メッセージを送信しました。')
#         return super().form_valid(form)



class CreateView(TemplateView):
    def __init__(self):
        self.params = {
        'title': 'Member Create',
        'form': CarsharUserCreateForm(),
    }

    def post(self, request):
        
        email = request.user.email
        name = request.POST['name']
        gender = 'gender' in request.POST
        age = request.POST['age']
        birthday = request.POST['birthday']
        zip01 = request.POST['zip01']
        pref01 = request.POST['pref01']
        addr01 = request.POST['addr01']
        addr02 = request.POST['addr02']
        record = CarsharUserModel(email = email,name = name, gender = gender, age = age, birthday = birthday, zip01 = zip01, pref01 = pref01, addr01 = addr01, addr02 = addr02)
        record.save()
        return redirect(to='carsharing_req:first')
        
    def get(self, request):
        querySet = CarsharUserModel.objects.filter(email__contains = request.user.email)
        if querySet.first() is None:
            print('no data')
        else:
            print('data　exist')
            return redirect(to='carsharing_req:index')
        return render(request, 'carsharing_req/create.html', self.params)




class CalendarView(TemplateView):
    def __init__(self):
        self.params = {
        'title': 'FullCalendar',
        'events': ''
    }

    def get(self, request):
        # カーシェアリング予約
        events = []
        booking = BookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).order_by('end_day', 'end_time')
        booking = booking.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in booking:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', 'カーシェアリング予約'+str(title)], ['start', start], ['end', end], ['color', '#9BF9CC']))
            events.append(event)
        
        # 駐車場予約
        booking2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).order_by('end_day', 'end_time')
        booking2 = booking2.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in booking2:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '駐車場予約'+str(title)], ['start', start], ['end', end], ['color', '#A7F1FF']))
            events.append(event)
        
        # 車両貸し出し制限
        loaning1 = BookingModel.objects.filter(user_id=request.session['user_id'], charge=-1).order_by('end_day', 'end_time')
        loaning1 = loaning1.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in loaning1:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '車両貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#00CC33']))
            events.append(event)


        # 駐車場貸し出し制限
        loaning2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id'], charge=-1).order_by('end_day', 'end_time')
        loaning2 = loaning2.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in loaning2:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '駐車場貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#6495ED']))
            events.append(event)
        self.params['events'] = json.dumps(events)
        
        return render(request, 'carsharing_req/calendar.html', self.params)


def details(request):
    dt_now = datetime.datetime.now()
    d_now = dt_now.strftime('%Y-%m-%d')
    booking = BookingModel.objects.filter(user_id=request.session['user_id'], end_day__lt=dt_now).exclude(charge=-1).order_by('-end_day', '-end_time')
    booking2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id'], end_day__lt=dt_now).exclude(charge=-1).order_by('-end_day', '-end_time')
    params = {
        'data': booking,
        'data2': booking2,
    }
    return render(request, 'carsharing_req/details.html', params)





def checkUsage(user_id):
    dt_now = datetime.datetime.now()
    d_now = dt_now.strftime('%Y-%m-%d')
    t_now = dt_now.strftime('%H:%M')
    usage = UsageModel.objects.filter(user_id=user_id).values('booking_id')
    print(usage)
    if len(usage) == 0:
        print('first')
        booking = BookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(charge=-1).values().order_by('end_day', 'end_time').last()
    else:
        usage_list = []
        for booking_id in usage:
            usage_list.append(booking_id['booking_id'])
            booking = BookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(id__in=usage_list).exclude(charge=-1).exclude(end_time__gte=t_now).values().order_by('end_day', 'end_time').last()
    print(booking)
    return booking


def surveyMail(request, booking):
    
    subject = "アンケート回答のお願い"
    attachments = "http://127.0.0.1:8000/survey/questionnaire"
    message = str(request.user) + "様\n \
        時間内の返却ありがとうございました。\n \
        またのご利用をお待ちしております。\n\n \
        開始日: " + booking['start_day'] + "\n \
        開始時刻: " + booking['start_time'] + "\n \
        終了日: " + booking['end_day'] + "\n \
        終了時刻: " + booking['end_time'] + "\n \
        料金: " + str(booking['charge']) + "円\n\n \
        アンケートにお答え下さい。\n \
        URL: " + attachments + "\n"
    user = request.user  # ログインユーザーを取得する
    from_email = 'admin@gmail.com'  # 送信者
    user.email_user(subject, message, from_email)  # メールの送信
    pass


def saveUsage(request, booking):
    booking_id = BookingModel.objects.get(id=booking['id'])
    record = UsageModel(user_id=booking['user_id'], car_id=booking['car_id'], \
        booking_id=booking_id, start_day=booking['start_day'], start_time=booking['start_time'], \
        end_day=booking['end_day'], end_time=booking['end_time'], charge=booking['charge'])
    record.save()
    pass