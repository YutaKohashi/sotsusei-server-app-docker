from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
import os, re
from django.shortcuts import redirect
# from api.urls import router as api_router

ApiVersion = 'v1/'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^api/' + ApiVersion, include(api_router.urls)),
    url(r'^api/' + ApiVersion, include('api.urls')),
    url(r'^web/', include('web.urls')),
    # url(r'^',lambda request: redirect("/admin/")), # adminへのリダイレクト処理
]

path = os.path.expanduser('~/sotsusei')
for dir in os.listdir(path):
    subdir = dir
    print('subdir-----------' + os.path.expanduser('~/sotsusei') + '/' + subdir)
    urlpatterns += static('/media_' + subdir + '/', document_root=os.path.expanduser('~/sotsusei') + '/' + subdir)  # /media/～のアップロード画像を見れるようにする

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # /media/～のアップロード画像を見れるようにする
# urlpatterns += static(settings.MEDIA_URL, document_root=os.path.expanduser('~/sotsusei') + '/' + subdir) # /media/～のアップロード画像を見れるようにする

