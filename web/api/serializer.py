from rest_framework import serializers

from web.models import *


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('name', 'mail')

class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageTable
        fields = ('path', 'imageid')


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTable
        fields = ('sid', 'gid', 'sname', 'ownername', 'latitude', 'longitude', 'date')


# 従業員取得シリアライザー
class EmployeeSerializer(serializers.ModelSerializer):
    #
    #
    # def employee_info(self,eid):
    #     i = 1
    #sid = StoreInfoSerializer()
    class Meta:
        model = EmployeeTable
        fields = ('eid', 'employeename', 'sid', 'status', 'plebel', 'date')


class GroupStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupStoreTable
        fields = ('gid', 'gname')



# 従業員認証
class AuthInputSerializer(serializers.Serializer):
    eid = serializers.EmailField()
    password = serializers.CharField()


# ナンバープレート登録serializer
class NumberPlateRegisterSerializer(serializers.Serializer):
    class Meta:
        model = CarTable
        fields = ('sid',
                  'humanid',
                  'imageid',
                  'shiyohonkyochi',
                  'bunruibango',
                  'jigyoyohanbetsumoji',
                  'ichirenshiteibango',
                  'cartype',
                  'colortype',
                  'makertype',
                  'comment',
                  'datetime')
