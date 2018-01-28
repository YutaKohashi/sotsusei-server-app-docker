from functools import singledispatch, update_wrapper  # オーバーロードで使用

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from api.serializer import *
from api.serializer import EmployeeSerializer

from api.managers.news_manager import NewsManager


# Create your views here.
def index(request):
    return HttpResponse("hello - API")
    # return render(request, appName + '/index.html')


class UploadedImagesViewSet(viewsets.ModelViewSet):
    queryset = ImageTable.objects.all()
    serializer_class = UploadImageSerializer

    def post(self):
        print("sended @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = EmployeeTable.objects.all()
    serializer_class = EmployeeSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = StoreTable.objects.all()
    serializer_class = StoreSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = GroupStoreTable.objects.all()
    serializer_class = GroupStoreSerializer


class GroupViewListSet(ListAPIView):
    queryset = GroupStoreTable.objects.all()
    serializer_class = GroupStoreSerializer


# ナンバープレート
class NumberPlateRegisterViewListSet(viewsets.ModelViewSet):
    queryset = CarTable.objects.all()
    serializer_class = NumberPlateRegisterSerializer


'''
シャッターイベント
'''


@api_view(['POST'])
# 従業員アプリからシャッターが押されたとき
def camera_shutter(request):
    # 該当の画像のシャッタフラグをTrueに
    if request.method == 'POST':
        store_id = request.POST['sid']
        emp_id = request.POST['eid']
        try:
            image_row = ImageTable.objects.filter(sid=store_id, originalflg=True).order_by('datetime').reverse().first()
            image_row.shutterflg = True
            image_row.save()

            # TODO 最新情報に追加
            newsManager = NewsManager()
            emp = EmployeeTable.objects.filter(eid=emp_id).first()
            text = newsManager.def_msg_shtter(emp_id=emp_id, emp_name=emp.employeename)
            newsManager.register_event_shutter(sid=store_id, eid=emp_id, comment=text)

            return JsonResponse(data={'res': 'success'})
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            return Response(status=400)


'''
ナンバープレートを登録するリクエスト
'''


@api_view(['POST'])
def register_number_plate(request):
    try:
        eid = request.POST['eid']
        sid = request.POST['sid']
        shiyohonkyochi = request.POST['shiyohonkyochi']
        bunruibango = request.POST['bunruibango']
        jigyoyohanbetsumoji = request.POST['jigyoyohanbetsumoji']
        ichirenshiteibango = request.POST['ichirenshiteibango']
        cartype = request.POST['cartype']
        colortype = request.POST['colortype']
        makertype = request.POST['makertype']
        comment = request.POST['comment']

        CarTable(sid=StoreTable(sid=sid),
                 shiyohonkyochi=shiyohonkyochi,
                 bunruibango=bunruibango,
                 jigyoyohanbetsumoji=jigyoyohanbetsumoji,
                 ichirenshiteibango=ichirenshiteibango,
                 cartype=cartype,
                 colortype=colortype,
                 makertype=makertype,
                 comment=comment).save()
        try:
            emp = EmployeeTable.objects.filter(eid=eid).first()
            gid = __sid_to_gid(sid=sid)
            news_manager = NewsManager()
            text = news_manager.def_msg_ihochusha(emp_id=emp.eid, emp_name=emp.employeename)
            news_manager.register_event_ihochusha(gid=gid, eid=emp.eid, comment=text)
        except Exception as e:
            print(e.args)

        return JsonResponse(data={'res': 'success'})
    except Exception as inst:
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)
        return Response(status=400)


def __sid_to_gid(sid):
    try:
        store = StoreTable.objects.filter(sid=sid).first()
        return store.gid
    except Exception as e:
        return None
