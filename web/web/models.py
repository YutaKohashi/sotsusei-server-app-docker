import uuid

from django.db import models


class GroupStoreTable(models.Model):
    gid = models.CharField(primary_key=True,max_length=255, default=str(uuid.uuid4().hex))
    gname = models.CharField(max_length=255)

    def __str__(self):
        return str(self.gid)


class StoreTable(models.Model):
    sid = models.CharField(primary_key=True,max_length=255, default=str(uuid.uuid4().hex))
    gid = models.ForeignKey(GroupStoreTable, default=None, blank=True, null=True, on_delete=models.CASCADE)
    sname = models.CharField(max_length=255)
    ownername = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    address =  models.CharField(max_length=255,default=None, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, default=None, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, default=None, blank=True, null=True)
    date = models.DateField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.sid)


# プッシュ通知のregstration token を管理するテーブル
class RegistrationTokenTable(models.Model):
    registration_token = models.CharField(max_length=255, primary_key=True)
    sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)


# TODO
# ホーム画面で表示する情報を一括管理するテーブル
# シャッターボタンが押されたなど
class LatestInfoTable(models.Model):
    infoId = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.IntegerField()


class EmployeeTable(models.Model):
    eid = models.CharField(max_length=255, primary_key=True)
    employeename = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default=None, blank=True, null=True)
    sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.IntegerField()  # 0;削除, 1;無効, 2;有効
    plebel = models.IntegerField()  # 0:普通, 1;管理者
    date = models.DateField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.eid)


class HumanTable(models.Model):
    humanid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sid = models.ForeignKey(StoreTable, default=None, blank=True, on_delete=models.SET_NULL, null=True)
    faceid = models.CharField(max_length=255, default=None, blank=True, null=True)
    name = models.CharField(max_length=255, default=None, blank=True, null=True)
    comment = models.CharField(max_length=255, default=None, blank=True, null=True)
    gendar = models.CharField(max_length=255, default=None, blank=True, null=True)
    age = models.FloatField(default=None, blank=True, null=True)
    blflg = models.BooleanField(default=False)

    def __str__(self):
        return str(self.humanid)


class ImageTable(models.Model):
    imageid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sid = models.ForeignKey(StoreTable, on_delete=models.SET_NULL, null=True)
    path = models.CharField(max_length=255)
    originalimageid = models.ForeignKey('ImageTable', default=None, blank=True, on_delete=models.SET_NULL,
                                        null=True)  # 元の画像の画像I
    datetime = models.DateTimeField(default=None, blank=True, null=True)
    # humanid = models.ForeignKey('HumanTable', default="-1", on_delete=models.CASCADE)
    humanid = models.ForeignKey(HumanTable, default=None, blank=True, on_delete=models.SET_NULL, null=True)
    faceid = models.CharField(max_length=255, default=None, blank=True, null=True)
    faceiddatetime = models.DateTimeField(default=None, blank=True, null=True)
    gendar = models.CharField(max_length=255, default=None, blank=True, null=True)
    age = models.FloatField(default=None, blank=True, null=True)
    shutterflg = models.BooleanField(default=False)
    originalflg = models.BooleanField(default=True)

    def __str__(self):
        return str(self.imageid)


class ThreadsTable(models.Model):
    threadid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    gid = models.ForeignKey(GroupStoreTable, on_delete=models.CASCADE)
    # imageid = models.ForeignKey(ImageTable, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)
    deleteflg = models.BooleanField()

    def __str__(self):
        return str(self.threadid)


class CarTable(models.Model):
    carid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sid = models.ForeignKey(StoreTable, blank=True, null=True, on_delete=models.SET_NULL)
    humanid = models.ForeignKey(HumanTable, blank=True, null=True, on_delete=models.SET_NULL)
    imageid = models.ForeignKey(ImageTable, blank=True, null=True, on_delete=models.SET_NULL)
    shiyohonkyochi = models.CharField(max_length=255, default=None, blank=True, null=True)
    bunruibango = models.CharField(max_length=255, default=None, blank=True, null=True)
    # ひらがな1字
    jigyoyohanbetsumoji = models.CharField(max_length=255, default=None, blank=True, null=True)
    # ナンバー
    ichirenshiteibango = models.CharField(max_length=255, default=None, blank=True, null=True)
    # 0:普通, 1:軽自動車, 3:事業用普通, 4:事業用系自動車, 5:外交官
    cartype = models.IntegerField(default=0)
    # 0:黒, 1:白, 2:グレー, 3:青系, 4:赤系, 5:緑系, 6:黄系
    colortype = models.IntegerField(default=0)
    # 0:トヨタ, 1:日産, 2:三菱, 3:ホンダ, 4:マツダ, 5:スバル, 6:すずき, 7:ダイハツ, 8:その他
    makertype = models.IntegerField(default=0)
    comment = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.carid)


class TokenTable(models.Model):
    sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    eid = models.ForeignKey(EmployeeTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    token = models.CharField(primary_key=True, max_length=255)
    datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enabled = models.BooleanField(blank=True, default=True)

    def __str__(self):
        return str(self.token)


class NewsTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    gid = models.ForeignKey(GroupStoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    eid = models.ForeignKey(EmployeeTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.IntegerField(default=0)  # 0 シャッター, 1違法駐車 ,2 ブラックリスト
    datetime = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.comment)
