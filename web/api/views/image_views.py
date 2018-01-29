from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from api.managers.image_manager import ImageManager
from api.utils.fileUtil import *
from api.managers.azure_manager import AzureManager
from web.models import *
import time
import pytz
from datetime import datetime
from api.managers.pushnotify_manager import PushManager
from api.managers.news_manager import NewsManager


# from api.managers.opencv_manager import Opencv_Manager


# 画像アップロード 削除 sid必須
@api_view(['POST', 'DELETE'])
def image_view(request):
    if request.method == 'POST':
        # 画像アップロード
        print("画像アップロードリクエスト")
        return __upload_image(request)
    elif request.method == 'DELETE':
        # 画像削除
        # return delete_image(request, )
        pass


# 画像保存　データベース登録
'''TODO
 画像のアプロードは3秒おきに行われる前提
 つまり この upload_image 関数は3秒おきに呼ばれる
 faceIdが24時間で失効するのは考慮していない
 シャッタイベントのときに顔の情報を取りに行く使用にしたい
'''


def __upload_image(request):
    print("\n******************** start upload_image ********************")
    try:
        store_id = request.POST['sid']
        print("store_id  -  " + store_id)

        try:
            # sid がデータベースに存在しているかチェック
            StoreTable.objects.get(sid=store_id)
        except EmployeeTable.DoesNotExist:
            print("不正な店舗ID")
            return HttpResponse(status=400)

        # 画像を取得
        original_image_data = request.FILES['imageData']

        # オリジナルの画像保存 ------------------------------------------------
        # 店舗専用のディレクトリに保存する
        mkdir(os.path.expanduser('~/sotsusei'), store_id)
        save_dir = os.path.expanduser('~/sotsusei') + '/' + store_id + '/'

        # オリジナルの画像をデータベースに登録
        # データベースに登録
        original_image_id = uuid.uuid4()

        ImageTable(imageid=original_image_id,
                   sid=StoreTable(sid=store_id),
                   path=save_dir + 'original/' + str(original_image_id) + '.png',
                   originalimageid=ImageTable(imageid=original_image_id),
                   datetime=pytz.timezone('Asia/Tokyo').localize(datetime.now()),
                   humanid=None,
                   faceid=None,
                   faceiddatetime=pytz.timezone('Asia/Tokyo').localize(datetime.now()),
                   gendar=None,
                   age=None,
                   shutterflg=False,
                   originalflg=True).save()
        # 画像保存
        image_manager = ImageManager()
        # <<<<<<< HEAD
        '''
        if not Opencv_Manager().is_contains_faces(original_image_data):
            # ほんとは上でするべき
            mkdir(save_dir, 'original')
            image_manager.save_request_image(original_image_data, save_dir + 'original/',
                                             str(original_image_id) + '.png')
            return Response(status=200)
        '''
        # image_manager.save_request_image(original_image_data , save_dir, str(original_image_id) + '.png')
        # =======
        # >>>>>>> fc09edbb5d91bbf3e11425fecca9d5ac47e55f98

        # Azure利用した顔認識
        azure_manager = AzureManager()

        # ---------------------------------------------------------
        # 顔認識 → FaceInfoListの生成 → OriginalImageから顔の画像データを生成
        # 画像をAzureに投げて顔の位置FaceIDなどを取得
        face_list = azure_manager.detect_faces(original_image_data)
        # time.sleep(3)

        # ほんとは上でするべき
        mkdir(save_dir, 'original')
        image_manager.save_request_image(original_image_data, save_dir + 'original/', str(original_image_id) + '.png')

        # 顔が存在しない場合
        # TODO:レスポンスの生成
        if len(face_list) == 0:
            print("Not Found Faces")
            print("\n******************** end upload_image ********************\n")
            return JsonResponse(data={'res': 'success'})

        # それぞれのfaceInfolistの顔を切り取って
        # original の画像がfaceijnfoインスタンスの中に入っている
        face_list = azure_manager.clip_image_in_face_list(face_list)

        # ---------------------------------------------------------

        '''
        ここでブラックリストに入っているかを確認する場合
        人の認識はこの前でする必要がある
        以前はシャッターが押されたときにその画像から顔を切り取って比較という流れをイメージしていたが、
        都度のリクエストで顔の切り取り、faceIdの取得, blacklistに入っているかを確認する必要がある！
        '''
        registed_humans = HumanTable.objects.all()
        print("start face_list ------------------------------------------------------------------------------------")
        for face_item in face_list:
            print("\nface_item ----------------------------")
            # 人物IDを取得
            human_id = azure_manager.apply_human_id(face_item.faceId, registed_humans)
            if human_id is None:
                # いままで登録されたことのない人の場合
                human_id = uuid.uuid4()
                print("apply_human_id -- 新しい人")
                print("humanId   - " + str(human_id))
                HumanTable(sid=StoreTable(sid=store_id), humanid=human_id, faceid=face_item.faceId,
                           gendar=face_item.gender,
                           age=face_item.age).save()
            else:
                print("apply_human_id -- 以前登録済み")
                print("humanId   - " + str(human_id))
                # if HumanTable.objects.get(humanid=human_id).count == 0:
                #     human_id = uuid.uuid4()
                #     print("apply_human_id -- 新しい人")
                #     print("humanId   - " + str(human_id))
                #     HumanTable(sid=StoreTable(sid=store_id), humanid=human_id, faceid=face_item.faceId, gendar=face_item.gender,
                #                age=face_item.age).save()
                # else:
                name = HumanTable.objects.get(humanid=human_id).name
                if not name is None: print("humanName - " + str(name))

            face_item.humanId = human_id

            image_id = uuid.uuid4()
            save_dir1 = save_dir + str(human_id) + "/"
            ImageTable(imageid=image_id,
                       sid=StoreTable(sid=store_id),
                       path=save_dir1 + str(image_id) + ".png",
                       originalimageid=ImageTable(imageid=original_image_id),
                       datetime=pytz.timezone('Asia/Tokyo').localize(datetime.now()),
                       humanid=HumanTable(humanid=face_item.humanId),
                       faceid=face_item.faceId,
                       faceiddatetime=pytz.timezone('Asia/Tokyo').localize(datetime.now()),
                       gendar=face_item.gender,
                       age=face_item.age,
                       shutterflg=False,
                       originalflg=False).save()
            # 画像保存
            mkdir(save_dir, str(human_id))
            image_manager.save(face_item.imageData, save_dir1, str(image_id) + '.png')

            # ブラックリストに入っているかどうか
            if len(HumanTable.objects.filter(humanid=human_id, blflg=True)) > 0:
                # プッシュ通知発動
                print('\nブラックリストに存在\n')
                # topic = "sample"
                # PushManager().push(topic)
                newsManager = NewsManager()

                gid = __sid_to_gid(store_id)

                human = HumanTable.objects.filter(humanid=human_id).first()
                try:
                    humanName = human.name
                    if humanName is None:
                        humanName = " 未登録 "
                except Exception as e:
                    humanName = " 未登録 "

                if gid is not None:
                    text = newsManager.def_msg_balcklist(humanName)
                    newsManager.register_event_blacklist(gid=gid, comment=text)

                PushManager().push(storeId=store_id, humanName=humanName)

            else:
                print('\nブラックリストに存在しない\n')

        print("end face_list ------------------------------------------------------------------------------------")
        print("******************** end upload_image ********************\n")
        return JsonResponse(data={'res': 'success'})
    except Exception as inst:
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)
        print("******************** end upload_image ********************\n")
        return Response(status=400)


# 画像削除
def __delete_image(request, image_id):
    try:
        # sid がデータベースに存在しているかチェック
        StoreTable.objects.get(sid=id)
    except EmployeeTable.DoesNotExist:
        return HttpResponse(status=404)

    image_manager = ImageManager()
    # TODO imageidからデータベース検索 画像パスを取得
    image_path = ImageTable.objects.get(imageid=image_id).path
    # image_manager から　deleteメソッドで削除する
    image_manager.delete(image_path)


def __sid_to_gid(sid):
    try:
        store = StoreTable.objects.filter(sid=sid).first()
        return store.gid
    except Exception as e:
        return None
