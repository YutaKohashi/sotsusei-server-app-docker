from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.managers.news_manager import NewsManager
from web.models import *

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
