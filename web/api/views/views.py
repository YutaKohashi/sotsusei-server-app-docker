
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from api.serializer import *
from api.serializer import EmployeeSerializer


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