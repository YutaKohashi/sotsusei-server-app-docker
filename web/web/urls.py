from django.conf.urls import url, static
from django.contrib.auth import views as auth_views
from . import views
# from django.contrib.auth import views as auth_views

app_name = 'web'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^image/$', views.image, name='image'),
    # url(r'^board/$', views.board, name='board'),
    url(r'^blacklist/$', views.blacklist, name='blacklist'),
    url(r'^setting/$', views.setting, name='setting'),
    url(r'^ihochusha/$', views.parking, name='parking'),

    # ～.htmlにあわせてる
    # url(r'^image_bulma.html/$', views.image, name='image'),
    # # url(r'^board_bulma.html/$', views.board, name='board'),
    # url(r'^blacklist_bulma.html/$', views.blacklist, name='blacklist'),
    # url(r'^configuration_bulma.html/$', views.setting, name='setting'),
    # url(r'^parking_bulma.html/$', views.parking, name='parking'),

    # url(r'^mypage/$', views.mypage, name='mypage'),
    # url(r'^redirect/$', views.redilect, name='redirect'),
    url(r'^login_sid/$', views.login_home_sid, name='login_home_sid'),
    url(r'^login_eid/$', views.login_home_eid, name='login_home_eid'),
    url(r'^login_auth_store/$', views.login_auth_store, name='login_auth_store'),
    url(r'^login_auth_employee/$', views.login_auth_employee, name='login_auth_employee'),
    url(r'^logout/$', views.logout, name='logout'),

    # 上記以外
    url(r'^', views.home, name='other'),
]
