import requests
import json
from .image_manager import *
from .http import *
import time


# 顔ひとつに対してImageInfoが対応する
# imageData 顔部分の画像データ
# left top width height で 顔の位置を特定する
class FaceInfo:
    def __init__(self, imgdata, humanId, faceId, gender, age, left, top, width, height):
        self.imageData = imgdata
        self.humanId = humanId
        self.faceId = faceId
        self.gender = gender
        self.age = age
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class AzureManager:
    # e4a3ffeb1d4749afa3806c5982f8f94f (有料版 マツイくんより)
    # 9cd066b7026b44da9e2c58d845741d2e (有料版 マツイくんより)
    # 共通APIkey（無料版）
    # API_KEY = 'afd2b51a50a1499695d8113c8fb21c9e'

    API_KEY = 'e4a3ffeb1d4749afa3806c5982f8f94f'

    BASE_URI = "https://eastasia.api.cognitive.microsoft.com/face/v1.0/"
    # face detect url
    FACE_DETECT_URI = BASE_URI + "detect"
    # face verify url (類似チェック)
    FACE_VERIFY_URI = BASE_URI + "verify"
    # face find similar
    FACE_FIND_SIMILAR = BASE_URI + "findsimilars"

    # --------------------------------------------------------------------------------
    # Azure リクエスト

    # 引数の画像から顔認識
    # response jsonデータ
    def detect_face(self, image_file):
        headers = create_headers(content_type=CONTENT_TYPE_OCTET_STREAM, ocp_apim_subscriotion_key=self.API_KEY)
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender'
        }

        print("\n→→→→→→→→→→→→ start http connection  - detect face  →→→→→→→→→→→→")
        response = http_post_image(self.FACE_DETECT_URI, headers=headers, params=params, image=image_file)
        print(response.text)
        print("←←←←←←←←←←←← end   http connection  - detect face  ←←←←←←←←←←←←\n")
        return response

    # 2つの顔が同一人物か比較
    # rate = response["confidence"] で 値を取得できる
    # responseをjsonオブジェクトで使用するときは verify_faces(???,???).json()
    def verify_face(self, face_id_1, face_id_2):
        headers = create_headers(content_type=CONTENT_TYPE_JSON, ocp_apim_subscriotion_key=self.API_KEY)
        body = {
            'faceId1': face_id_1,
            'faceId2': face_id_2,
        }
        try:
            print("\n→→→→→→→→→→→→ start http connection  - verify face →→→→→→→→→→→→")
            response = http_post(self.FACE_VERIFY_URI, headers=headers, body=body)
            print(response.text)
            print("←←←←←←←←←←←← end   http connection  - verify face ←←←←←←←←←←←←\n")
            return response
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            return None
            # print(response.text)

    # 第一引数のface_idの顔が第二引数のfaceidarrayの中にいるか調べる
    def find_similar(self, face_id, face_id_array):
        headers = create_headers(content_type=CONTENT_TYPE_JSON, ocp_apim_subscriotion_key=self.API_KEY)

        body = {
            'faceId': face_id,
            'faceIds': face_id_array,
            'maxNumOfCandidatesReturned': 10,
            'mode': 'matchPerson'
        }

        try:
            print("\n→→→→→→→→→→→→ start http connection  - find similar →→→→→→→→→→→→")
            response = http_post(self.FACE_FIND_SIMILAR, headers=headers, body=body)
            print(response.text)
            print("←←←←←←←←←←←← end   http connection  - find similar ←←←←←←←←←←←←\n")
            return response
        except Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            return None

    # --------------------------------------------------------------------------------

    # ２つの顔を比較し同一人物のときはTrue　違うときはFalseを返す
    def compare_faces(self, face_id_1, face_id_2):
        # TODO しきい値を0.7に設定
        threshold = 0.7
        response = self.verify_face(face_id_1, face_id_2).json()
        # time.sleep(3)
        try:
            confidence_rate = response["confidence"]
            return float(confidence_rate) > threshold
        except  Exception as inst:
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            return False

    # 複数のfaceidから同一人物の顔が存在するかチェック
    # target_face_id → azureが発行
    # humans         → HumanTable model　のリスト
    # return humanid
    def __contains_humans(self, target_face_id, humans):
        threshold = 0.7
        try:
            faceIds = []
            for h in humans: faceIds.append(h.faceid)
            response = self.find_similar(target_face_id, faceIds).json()

            confidence_rate = response[0]["confidence"]
            print('confidence_rate : ' + str(confidence_rate))
            humanId = None
            if float(confidence_rate) > threshold:
                humanId = humans.get(faceid=response[0]["faceId"]).humanid

            return humanId
        except Exception as inst:
            # print(type(inst))  # the exception instance
            # print(inst.args)  # arguments stored in .args
            # print(inst)
            return None

    # 引数の画像データからFaceInfoリストを返すメソッド
    def detect_faces(self, image_data):
        # 画像をAzureに投げて顔の位置FaceIDなどを取得
        print()
        azure_response = self.detect_face(image_data)
        # print(azure_response.re)
        # time.sleep(1)

        # レスポンスより必要なデータのみのFaceInfoリストを作成する
        return self.__face_list_from_response(azure_response, image_data)

    # RequestsレスポンスからImageInfoインスタンスを生成
    # 戻り値はfaceListリスト
    @classmethod
    def __face_list_from_response(self, azure_response, original_image_data):
        json_dict = json.loads(azure_response.text)

        # 顔ごとに解析し、ImageInfo(必要なデータのみのオブジェクト)リストを作成する
        face_list = []
        for face_item in json_dict:
            # humanid と imagedataを除くFaceInfoオブジェクトを生成
            face_info = FaceInfo(
                original_image_data,  # 切り取り前の画像データを入れておく
                None,  # human_id
                face_item["faceId"],
                face_item["faceAttributes"]["gender"],
                face_item["faceAttributes"]["age"],
                face_item["faceRectangle"]["left"],
                face_item["faceRectangle"]["top"],
                face_item["faceRectangle"]["width"],
                face_item["faceRectangle"]["height"]
            )

            face_list.append(face_info)
        return face_list

    # 顔を切り取る
    # 各FaceInfoオブジェクトのimageDataフィールドにoriginalの画像データが入っている
    def clip_image_in_face_list(self, face_list):
        image_manager = ImageManager()
        face_list2 = []
        for face_item in face_list:
            try:
                clipped_image = image_manager.clip_bigger(face_item.imageData, face_item.left, face_item.top,
                                                          face_item.width,
                                                          face_item.height)
                face_item.imageData = clipped_image
                face_list2.append(face_item)
            except:
                continue
                # for face_item in face_list:
        return face_list2

    # ブラックリストに入っているかチェック
    # humanidからチェック
    def checkContainsBlackList(self, humanid):
        pass

    # いままで登録したことがある人物かどうか
    # 存在していた場合humanidを返す
    # 存在していなければ Noneを返す
    # 第二引数のhuman_list はHumanTableオブジェクト
    def apply_human_id(self, target_face_faceId, humans):
        return self.__contains_humans(target_face_faceId, humans)
