
from enum import Enum

class ReponseManager:

    #成功時のレスポンス
    def success(self, type):
        pass


    # 失敗時のレスポンス
    def failure(self):
        pass

class SuccessResType(Enum):
    DEFAULT = 0



class FailureResType(Enum):
    DEFAULT = 0

