from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse

from api.managers.token_manager import TokenManager
from web.models import *
import uuid

# 店舗ログインチェック
@api_view(['POST'])
def store_create_token(request):
    # ログインリクエスト　POSTのみ
    if request.method == 'POST':
        if __verify_store_id_pass(request):
            token_manager = TokenManager()
            sid = request.POST['sid']
            token = token_manager.create_token_sid(sid=sid)
            return JsonResponse(data={'token': token})
        else:
            return Response(status=400)


# 従業員ログインチェック
@api_view(['POST'])
def employee_create_token(request):
    if request.method == 'POST':
        if __verify_emp_id_pass(request):
            token_manager = TokenManager()
            eid = request.POST['eid']
            token = token_manager.create_token_eid(eid=eid)
            return JsonResponse(data={'token': token})
        else:
            return Response(status=400)


@api_view(['POST'])
def store_verify_token(request):
    if request.method == 'POST':
        token_manager = TokenManager()
        token = request.POST['token']
        sid = request.POST['sid']
        if token_manager.check_by_sid(sid, token):
            return JsonResponse(data={'res': 'success'})
        else:
            Response(status=400)


@api_view(['POST'])
def employee_verify_token(request):
    if request.method == 'POST':
        token_manager = TokenManager()
        token = request.POST['token']
        eid = request.POST['eid']
        if token_manager.check_by_eid(eid, token):
            return JsonResponse(data={'res': 'success'})
        else:
            Response(status=400)


@api_view(['POST'])
def revocation_token(request):
    token = request.POST['token']
    try:

        if TokenManager().revocation_token(token):
            return JsonResponse(data={'res': 'success'})
        else:
            Response(status=400)
    except Exception as e:
        print(e.args)
        Response(status=400)



'''
************************************************************************************
private methods
'''


# ログインチェックID（店舗）
def __verify_store_id_pass(request):
    # リクエストbodyを取得
    store_id = request.POST['sid']
    password = request.POST['password']
    print("store_id  -  " + store_id)
    print("password  -  " + password)

    try:
        # sid と password がデータベースに存在しているかチェック
        store = StoreTable.objects.get(sid=store_id)

        # 登録されているパスワードを取得
        registered_password = store.password

        # 登録されているパスワードとリクエストのパスワードが等しいかチェック
        if registered_password == password:
            return True
        else:
            return False

        # StoreTable.objects.get(password = password)
    except StoreTable.DoesNotExist:
        print("不正な店舗ID")
        return False


# ログインチェック(従業員)
def __verify_emp_id_pass(request):
    employee_id = request.POST['eid']
    store_id = request.POST['sid']
    password = request.POST['password']

    print("employee_id  -  " + employee_id)
    print("password - " + password)

    try:
        employee = EmployeeTable.objects.filter(sid=store_id, eid=employee_id).first()
        registered_password = employee.password

        if registered_password == password:
            return True
        else:
            return False

    except Exception as e:
        print('不正な従業員ID')
        return False

