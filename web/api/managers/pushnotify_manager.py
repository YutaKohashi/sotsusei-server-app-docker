from .http import *


class PushManager:
    BASE_URI = "https://fcm.googleapis.com/fcm/"
    FCM_SEND_URI = BASE_URI + "send"
    # AUTHORIZATION_KEY = 'AAAAdg0Yke0:APA91bEyMcw72Lw3JaTE3CQq2_vSho4zANZ8b53yzf6_uPmrbJ-cAXHrtQ_Fp8NZkgic534D0H1v1MIa4FvoG1g7jx-hWftOf7aqXVCli2ySbDrFsoloYGtncg5f9zUF7O2mSvtbyADW'
    AUTHORIZATION_KEY = "AAAA4Tjx-xE:APA91bH90JUME_Pfz2iNGkSX3QPbHMtT9M1uI9AhzKpJEokVt0KwWYYKy7XxZM9mjRzEsGMkqtCaFz7tJ_HPvs6cplm_m8SVqA6GWJFg3TNiC6EQYWw7-Ul7aD0hKHLqsolmxTTDyns1"

    # プッシュ通知発動
    # 引数のstoreIdで範囲を絞れるように
    # storeidをトピックとする
    def push(self, storeId, humanName):
        headers = create_headers(content_type=CONTENT_TYPE_JSON, authorization=self.AUTHORIZATION_KEY)


        body = self.__create_msg(storeId=storeId, humanName=humanName)

        print("\n→→→→→→→→→→→→ start http connection  - detect face  →→→→→→→→→→→→")
        response = http_post(self.FCM_SEND_URI, headers=headers, body=body)
        print(response.text)
        print("←←←←←←←←←←←← end   http connection  - detect face  ←←←←←←←←←←←←\n")
        return response



    def __create_msg(self, storeId, humanName):
        return  {
            'to': '/topics/' + storeId,
            'data': {
                'title':'ブラックリストに存在する人を検知しました!',
                'message': '登録名 : ' + humanName
            }
        }