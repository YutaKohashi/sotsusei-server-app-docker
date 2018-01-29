from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.managers.news_manager import NewsManager
from web.models import *
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
