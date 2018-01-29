from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token
from api.views import image_views, views, account_verify_view, camera_shutter_view,number_plate_view
# from api import views


router = routers.DefaultRouter()
router.register(r'images', views.UploadedImagesViewSet, r'images')
router.register(r'employee', views.EmployeeViewSet, 'employee_info')
router.register(r'group', views.GroupViewSet)
# 店舗情報を取得
router.register(r'store/info', views.StoreViewSet)
router.register(r'employee/info', views.EmployeeViewSet)

app_name = 'api'
urlpatterns = [
    url(r'^', include(router.urls)),

    # 画像アップロード,削除
    url(r'^image/$', image_views.image_view),

    # シャッター
    url(r'^shutter',camera_shutter_view.camera_shutter),

    # 店舗トークン作成
    url(r'^store/createtoken',account_verify_view.store_create_token),
    # 従業員トークン作成
    url(r'^employee/createtoken', account_verify_view.employee_create_token),

    url(r'^store/verifytoken', account_verify_view.store_verify_token),
    url(r'^employee/verifytoken',account_verify_view.employee_verify_token),

    url(r'^revocationtoken',account_verify_view.revocation_token),

    # ナンバープレート登録
    url(r'^numberplate',number_plate_view.register_number_plate)

]
