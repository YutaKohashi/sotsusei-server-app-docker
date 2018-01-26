from enum import Enum

from web.models import *


class NewsType(Enum):
    SHUTTER = 0  # sidで管理 eidで誰が行ったかを管理
    IHO_CHUSHA = 1  # gidで管理 eidで登録者を管理
    BLACK_LIST = 2  # gidで管理 eidで誰がblacklistに入れたかを管理


# 最新情報を取得するためのクラス、メソッド
# ex.NewsManager().get_news_by_gid(NewsType.BLACK_LIST,0001)
class NewsManager:

    def get_news_by_sid(self, newsType, sid):
        return NewsTable.objects.get(sid=sid, type=newsType.value).values()

    def get_news_by_gid(self, newsType, gid):
        return NewsTable.objects.get(gid=gid, type=newsType.value).values()

    # シャッタイベントを登録するメソッド
    def register_event_shutter(self, sid, eid, comment):
        self.__register_event_sid_eid(type=NewsType.SHUTTER, sid=sid, eid=eid, comment=comment)

    # 違法駐車を登録するメソッド
    def register_event_ihochusha(self, gid, eid, comment):
        self.__register_event_gid_eid(type=NewsType.IHO_CHUSHA, gid=gid, eid=eid, comment=comment)

    # ブラックリストを登録するメソッド
    def register_event_blacklist(self, gid, comment):
        self.__register_event_gid(type=NewsType.BLACK_LIST, gid=gid, comment=comment)

    # ブラックリストに存在する
    def def_msg_balcklist(self, target_name):
        return "ブラックリストのユーザ " + target_name + " がカメラ内に認識されました"

    def def_msg_shtter(self,emp_id, emp_name):
        return "従業員ID:" + emp_id + " " + emp_name + "さんが写真を記録しました"

    def def_msg_ihochusha(self, emp_id, emp_name):
        return "従業員ID:" + emp_id + " " + emp_name + "さんがナンバープレートを登録しました"

    '''
    private methods
    '''

    #
    def __register_event_gid_eid(self, type, gid, eid, comment=""):
        NewsTable(type=type.value, gid=GroupStoreTable(gid=gid), eid=EmployeeTable(eid=eid), comment=comment).save()

    def __register_event_sid_eid(self, type, sid, eid, comment=""):
        NewsTable(type=type.value, sid=StoreTable(sid=sid), eid=EmployeeTable(eid=eid), comment=comment).save()

    def __register_event_gid(self, type, gid, comment=""):
        NewsTable(type=type.value, gid=GroupStoreTable(gid=gid), comment=comment).save()
