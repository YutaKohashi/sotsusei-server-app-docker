'''
    APIのキーをまとめたファイルです
    プログラム内でAPIキーを使用するときはこのファイルを参照しています
'''


'''
    AzureのFaceAPIキーを記述してください
    顔認識に使用します
    キーが2つ発行されますが、どちらでも構いません
    
    FaceAPIについては以下のリンクに詳細情報が記述されています
    https://azure.microsoft.com/ja-jp/services/cognitive-services/face/
    無料版の制限については以下のリンクに詳細情報が記述されています
    https://azure.microsoft.com/ja-jp/pricing/details/cognitive-services/face-api/
'''
# AZURE_FACE_API_KEY = "df276913865f47e797721416f4c15364"

# 共通APIkey（無料版）
AZURE_FACE_API_KEY = 'afd2b51a50a1499695d8113c8fb21c9e'



'''
 FirebaseのFirebaseCloudMessagingのAPIキーを記述してください
 ブラックリストに存在する人がカメラ内に映ったときに従業員側のアプリケーションに対して
 プッシュ通知を行うときに使用しています
 
 Firebaseについては以下のリンクに詳細情報が記述されています
 https://firebase.google.com
 FirebaseCloudMessagingについては以下のリンクに詳細情報が記述されています
 https://firebase.google.com/docs/cloud-messaging/
'''
FIREBASE_CLOUD_MESSAGING_KEY = "AAAA4Tjx-xE:APA91bH90JUME_Pfz2iNGkSX3QPbHMtT9M1uI9AhzKpJEokVt0KwWYYKy7XxZM9mjRzEsGMkqtCaFz7tJ_HPvs6cplm_m8SVqA6GWJFg3TNiC6EQYWw7-Ul7aD0hKHLqsolmxTTDyns1"