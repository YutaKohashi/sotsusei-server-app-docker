from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.conf import settings
from api.managers.news_manager import *
from .urls import *
import enum, os, socket, re, copy, uuid
from .models import *

appName = 'web'

imageid_dic2 = {}

class SessionType:
    EID_AND_SID =0
    EID_ONlY = 1
    SID_ONLY = 2
    EID_AND_SID_NONE = 3

class SessionManager:

    def loginCheck(self, def_request):

        if 'sid' in def_request.session:
            if 'eid' in def_request.session:
                return SessionType.EID_AND_SID
            else:
                return SessionType.SID_ONLY
        elif 'eid' in def_request.session:
            return SessionType.EID_ONlY
        else:
            return SessionType.EID_AND_SID_NONE

    # セッションの状態によってリダイレクトする
    def redirecter(self, def_request, status, eidflg=False):

        if eidflg:
            if status == SessionType.EID_ONlY:
                # EIDだけあるので店舗ログインへ遷移
                def_request.session.clear()
                return HttpResponseRedirect('../web/login_sid')

            if status == SessionType.SID_ONLY:
                # SIDだけあるので従業員ログインへ遷移
                return HttpResponseRedirect('../../web/login_eid')

        else:
            if status == SessionType.EID_AND_SID:
                # どちらもあるのでそのまま処理
                return True

            if status == SessionType.EID_AND_SID_NONE or status == SessionType.EID_ONlY:
                # どちらも無いので店舗ログインへ遷移
                template = loader.get_template('web/store_login.html')
                context = {
                    'location_home': True,
                }
                return HttpResponse(template.render(context, def_request))

            if status == SessionType.SID_ONLY:
                # SIDだけあるので従業員ログインへ遷移
                template = loader.get_template('web/employee_login.html')
                context = {
                    'location_home': True,
                }
                return HttpResponse(template.render(context ,def_request))


# 旧ログイン
# def index(request):
#     template = loader.get_template('web/login-sid.html')
#     context = {
#         'location_home': True,
#     }
#     return HttpResponse(template.render(context, request))

def login_home_sid(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if not session_status_result:
        return session_status_result

    template = loader.get_template('web/store_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))

def login_home_eid(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if not session_status_result:
        return session_status_result

    template = loader.get_template('web/employee_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))

# 新ログイン(店舗)
def login_auth_store(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if not session_status_result:
        return session_status_result

    # Login
    if 'sid' in request.POST and 'spass' in request.POST:
        post_sid = request.POST['sid']
        try:
            storeTable = StoreTable.objects.get(sid=post_sid)
            # POSTされたeidがDBにあるかチェック
            if storeTable.password == request.POST['spass']:
                request.session['sid'] = request.POST['sid']
                request.session['spass'] = request.POST['spass']
                print('Login Success')
            else:
                print('Login Missed. PW')

        except StoreTable.DoesNotExist:
            print('Login Missed. sid')
            return HttpResponse(status=400)

    if 'logout' in request.POST:
        request.session.clear()

    if 'sid' in request.session and 'spass' in request.session:
        name = request.session['sid']

        return HttpResponseRedirect('../')

#
# 新ログイン(従業員)　参考：http://webcache.googleusercontent.com/search?q=cache:I_r71dI_fxsJ:python.zombie-hunting-club.com/entry/2017/11/06/222409+&cd=1&hl=ja&ct=clnk&gl=jp
#
def login_auth_employee(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if not session_status_result:
        return session_status_result

    session_sid = request.session['sid']
    session_eid = request.session['eid']

    # 店舗ログイン済みの場合のみ、従業員ログインの処理を行う
    if 'sid' in request.session:
        # sessionSid = request.session['sid']
        # POSTされた値に、eidとepassがあるかチェック
        if 'eid' in request.POST and 'epass' in request.POST:
            post_eid = request.POST['eid']
            try:
                employeeTable = EmployeeTable.objects.get(sid=session_sid, eid=post_eid)
                # POSTされたeidがDBにあるかチェック

                if employeeTable.password == request.POST['epass']:
                    request.session['eid'] = request.POST['eid']
                    request.session['epass'] = request.POST['epass']
                    print('Login Success')
                else:
                    print('Login Missed. PW')

            except EmployeeTable.DoesNotExist:
                print('Login Missed. eid')
                return HttpResponse(status=400)

        if 'logout' in request.POST:
            #e eid kesu
            request.session.clear()

        if 'eid' in request.session and 'epass' in request.session:
            name = request.session['eid']
            loggedIn = True

    # return render(request, "web/logined-eid.html", {'loggedIn': loggedIn, 'name': name})
    return HttpResponseRedirect('../', {'sid':session_sid, 'eid':session_eid})

def logout(request):
    # セッション削除
    request.session.clear()

    # 店舗ログインに遷移
    template = loader.get_template('web/store_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))

#
# ホーム（ログイン後のトップページ）
#
def home(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    session_sid = request.session['sid']
    session_eid = request.session['eid']

    # 新しい順に取得(最大30件)
    newstables = NewsTable.objects.filter(sid=session_sid).order_by('-datetime').values()[:30]

    news_ary = []
    news_ihouchusha_ary = []
    news_blacklist_ary = []
    for news in newstables:
        news_type = news['type']
        news_comment = news['comment']
        if NewsType.IHO_CHUSHA.value == news_type:
            news_ary.append({'url':'ihou', 'comment':news_comment})
            news_ihouchusha_ary.append({'url':'ihou', 'comment':news_comment})
        if NewsType.BLACK_LIST.value == news_type:
            news_ary.append({'url':'black', 'comment':news_comment})
            news_blacklist_ary.append({'url':'ihou', 'comment':news_comment})

    template = loader.get_template('web/home_bulma.html')
    context = {
        'location_home': True,
        'news_ary': news_ary,
        'news_ihouchusha_ary': news_ihouchusha_ary,
        'news_blacklist_ary': news_blacklist_ary,
        'sid':session_sid,
        'eid':session_eid,
    }
    return HttpResponse(template.render(context, request))



#
# 画像一覧ページ
#
def image(request):

    session_sid = request.session['sid']
    session_eid = request.session['eid']

    imageid_dic = {}

    #
    # 画像一覧表示
    #
    humanTable = HumanTable.objects.all().values()
    org_image_datas = ImageTable.objects.filter(sid=session_sid, shutterflg=True, originalflg=True).order_by('-datetime').values() # 日付が新しい順にソートして取得
    not_org_image_datas = ImageTable.objects.filter(sid=session_sid, originalflg=False).order_by('-datetime').values()

    # if len(imageid_dic) != 0:
    #     imageid_dic.clear()

    result = [[[]]]
    date = ''
    rowIndex = 0
    colIndex = 0
    for image in org_image_datas:
        date2 = "{0:%Y/%m/%d}".format(image['datetime'])
        image_url = 'http://' + request.get_host() + '/media_' + session_sid + '/' + os.path.basename(image['path'])
        org_imageid = str(image['imageid'])
        child_imageid_list = not_org_image_datas.filter(originalimageid=org_imageid) # 同じ写真に写っている人
        child_imageid_ary = []

        # 写真に2人以上写っている場合は、その個別の画像のパスを配列にする
        if len(child_imageid_list) != 0:
            for child_imageid in child_imageid_list:
                child_image_url = 'http://' + request.get_host() + '/media_' + session_sid + '/' + os.path.basename(child_imageid['path'])
                child_imageid_ary.append(child_image_url)
                print(child_image_url)
                imageid_dic[child_image_url] = str(child_imageid['imageid'])
        else:
            child_image_url = 'http://' + request.get_host() + '/media_' + session_sid + '/' + os.path.basename(image_url)
            child_imageid_ary.append(child_image_url)
            # imageid_dic[child_image_url] = org_imageid['']
            # child_imageid_ary.append('https://github.com/identicons/97621d420f24ab078969e8b5675bf871.png')
            print('写真には一人しか写っていない')

        if(date == '') :
            date = date2
            result.append([date, [image_url], child_imageid_ary])
            imageid_dic[image_url] = org_imageid
        elif (date == date2):
            result[rowIndex+1][1].append(image_url)
            imageid_dic[image_url] = org_imageid
        else:
            rowIndex += 1
            date = date2
            result.append([date, [image_url], child_imageid_ary])
            imageid_dic[image_url] = org_imageid

    result.pop(0)
    imgs = result

    #
    # 画像一覧の複数人が写っている場合のリストを作る
    #


    #
    # ブラックリスト登録（FlagをTrueにする）
    #
    if request.method == 'POST':
        if 'bl_path' in request.POST:
            print(imageid_dic)
            bl_path = request.POST['bl_path']
            # imageid = imageid_dic[bl_path]
            org_imageid = imageid_dic[bl_path]

            # 該当imageidからhumanidを特定してブラックリストフラグをたてる
            human_row = ImageTable.objects.filter(sid=session_sid, imageid=org_imageid).values()
            image_humanid = human_row[0]['humanid_id']
            blackflag_register_human_row = HumanTable.objects.filter(humanid=image_humanid).values()
            blackflag_register_human_row.update(blflg=True) # ブラックリストフラグをたてて上書きする

            '''
            ニューステーブルに追加
            '''
            gid = StoreTable.objects.filter(sid=session_sid).values().first()['gid_id']
            employee_name = EmployeeTable.objects.filter(sid=session_sid).values().first()['employeename']
            comment = NewsManager().def_msg_ihochusha(session_eid, employee_name)
            NewsManager().register_event_blacklist(gid, comment)

            # id = models.UUIDField(primary_key=True, default=uuid.uuid4)
            # gid = models.ForeignKey(GroupStoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
            # sid = models.ForeignKey(StoreTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
            # eid = models.ForeignKey(EmployeeTable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
            # type = models.IntegerField(default=0)  # 0 シャッター, 1違法駐車 ,2 ブラックリスト
            # datetime = models.DateTimeField(auto_now_add=True)
            # comment = models.CharField(max_length=255, default=None, blank=True, null=True)

            # i = 0
            # for imagedata in org_image_datas:
            #
            #     # 2週目は処理の必要がない（地球祭前なので適当に処置中）
            #     if i == 1:
            #         break
            #
            #     imageHumanId = imagedata['humanid_id']
            #     if imageHumanId == None:
            #         continue
            #
            #     try:
            #         fullBlImagePathMatch = re.finditer('media\_(.*)', bl_path) # blImagePath は http://127..../media_[sid]~となってる
            #         fullBlImagePath = ''
            #         for match in fullBlImagePathMatch:
            #             fullBlImagePath = str(match.groups()[0])
            #
            #         fullBlImagePath2 = os.path.expanduser('~\\sotsusei') + '\\' + fullBlImagePath.replace('/', '\\') #re.escape(fullBlImagePath)
            #         imageRecord = org_image_datas.filter(path=fullBlImagePath2)
            #         imageHumanId = str(imageRecord[0]['humanid_id'])
            #         HumanFilterData = humanTable.filter(humanid=imageHumanId)
            #         blFlag = HumanFilterData[0]['blflg']
            #         if blFlag:
            #             break # すでにTrueなので処理しない
            #         else:
            #             # ブラックリストFlagをTrueにする https://stackoverflow.com/questions/25906799/django-is-it-efficient-to-save-queryset-items-in-loop
            #             HumanFilterData.update(blflg=True)
            #             break # 1回の処理でいいのでfor抜ける
            #
            #     except:
            #         i += 1
            #         print('例外エラー: 画像のレコードにHumanIdが設定されていな可能性があります。')


    #
    # ブラックリストFlagのある画像だけ取り出す
    #
    blFlagImagePath = []
    # imageHumanIdData = ImageTable.objects.values_list('humanid')
    # imagePathData = ImageTable.objects.values_list('path')
    for imagedata in org_image_datas:
        imageHumanId = imagedata['humanid_id']
        if imageHumanId == None:
            continue

        try:
            HumanFilterData = humanTable.filter(humanid=imageHumanId)
            blFlag = HumanFilterData[0]['blflg']

            if blFlag:
                blFlagImagePath.append('http://' + request.get_host() + '/media_' + str(imagedata['sid_id']) + '/' + os.path.basename(imagedata['path']))
        except:
            pass

    #
    # HTMLテンプレートで扱いやすくするため、１つのリストにまとめる
    #
    # imgsNameNext = copy.deepcopy(imgName) # 配列のコピー
    # imgsNameNext.append(imgName[0])

    dataList = []
    for i, _ in enumerate(imgs):

        dataList.append({
            'datetime': imgs[i][0],
            'img_path': imgs[i][1],
            'bl_img_paths': imgs[i][2],
            # 'imgPathNext': imgsNameNext[i+1],
            # 'imgName': imgName[i],
        })

    template = loader.get_template('web/image_bulma.html')
    context = {
        'location_image': True,
        'blFlagImagePath': blFlagImagePath,
        'dataList': dataList,
        # 'imgs2': imgs2,
    }
    return HttpResponse(template.render(context, request))


# 掲示板
def board(request):
    # DBからデータ取得
    threadCommentTuple = ThreadsTable.objects.values_list('comment')

    comments = []
    for comment in threadCommentTuple:
        comments.append(comment[0])

    # 画像
    # DBからpath列のデータをすべて取得
    imagePathTuple = ImageTable.objects.values_list('path')

    imgs = []
    for imgPath in imagePathTuple:
        imgs.append('http://' + request.get_host() + settings.MEDIA_URL + os.path.basename(imgPath[0]))

    template = loader.get_template('web/board_bulma.html')
    context = {
        'location_board': True,
        'comments': comments,
        'imgs': imgs,
    }
    return HttpResponse(template.render(context, request))

#
# ブラックリスト
#
def blacklist(request):

    session_sid = '0000'
    imageData = ImageTable.objects.filter(sid=session_sid).values()
    blFlagImagePath = []
    imgName = []
    humanTable = HumanTable.objects.filter(blflg=True).values()

    for imagedata in imageData:
        imageHumanId = imagedata['humanid_id']
        if imageHumanId == None:
            continue

        try:

            HumanFilterData = humanTable.filter(humanid=imageHumanId)
            blFlag = HumanFilterData[0]['blflg']

            if blFlag:
                blFlagImagePath.append(
                    'http://' + request.get_host() + '/media_' + str(imagedata['sid_id']) + '/' + os.path.basename(
                        imagedata['path']))
                imgName.append(os.path.basename(imagedata['path']).replace('.', '_'))

        except:
            pass

    dataList = []
    for i, _ in enumerate(blFlagImagePath):
        dataList.append({
            'blFlagImagePath': blFlagImagePath[i],
            'imgName': imgName[i],
        })

    template = loader.get_template('web/blacklist_bulma.html')
    context = {
        'location_bl': True,
        'blFlagImagePath': blFlagImagePath,
        'dataList': dataList,
    }
    return HttpResponse(template.render(context, request))

#
# 違法駐車
#
def parking(request):

    session_sid = '0000'
    session_eid = '1111'
    imageData = CarTable.objects.filter(sid=session_sid).values()

    # 迷惑駐車の情報登録
    if 'parking_add' in request.POST:

        #
        # フォームに入力されたナンバープレートの情報群
        #

        # プレートの色
        req_cartype = 0 #'white'
        if 'green' in request.POST:
            req_cartype = 5 #'green'
        if 'yellow' in request.POST:
            req_cartype = 6 #'yellow'
        if 'black' in request.POST:
            req_cartype = 0 #'black'

        # 車の色
        # req_colortype = 0  # 'white'
        # if 'green' in request.POST:
        #     req_colortype = 5  # 'green'
        # if 'yellow' in request.POST:
        #     req_colortype = 6  # 'yellow'
        # if 'black' in request.POST:
        #     req_colortype = 0  # 'black'

        location = request.POST['location']
        classnumber = request.POST['classnumber']
        hiragana = request.POST['hiragana']
        number = request.POST['number']

        # DBに登録する
        CarTable(sid_id=session_sid,
                 shiyohonkyochi =location,
                 bunruibango =classnumber,
                 # ひらがな1字
                 jigyoyohanbetsumoji =hiragana,
                 # ナンバー
                 ichirenshiteibango =number,
                 # 0:普通, 1:軽自動車, 3:事業用普通, 4:事業用系自動車, 5:外交官
                 cartype =req_cartype,
                 # 0:黒, 1:白, 2:グレー, 3:青系, 4:赤系, 5:緑系, 6:黄系
                 colortype =0,
                 # 0:トヨタ, 1:日産, 2:三菱, 3:ホンダ, 4:マツダ, 5:スバル, 6:すずき, 7:ダイハツ, 8:その他
                 makertype =0,
                 comment ='comment').save()

        '''
        ニューステーブルに追加
        '''
        gid = StoreTable.objects.filter(sid=session_sid).values().first()['gid_id']
        employee_name = EmployeeTable.objects.filter(sid=session_sid).values().first()['employeename']
        comment = NewsManager().def_msg_ihochusha(session_eid, employee_name)
        NewsManager().register_event_ihochusha(gid, session_eid, comment)

        # storetables = StoreTable.objects.filter(sid=session_sid).values()
        # gid = storetables[0]['gid_id']
        # NewsTable(gid_id=gid,
        #           sid_id=session_sid,
        #           eid_id=session_eid,
        #           type=1).save()

    # DBからpath列のデータをすべて取得
    parkingData = CarTable.objects.all().values()
    editData = parkingData
    storeData = StoreTable.objects.all().values()
    sname = []
    numberPlateImages = [] # ナンバープレート画像

    i = 0
    for parkingdata in parkingData:
        colortype = parkingdata['colortype']

        if colortype == 0:
            editData[i]['colortype'] = '黒'
        elif colortype == 1:
            editData[i]['colortype'] = '白'
        elif colortype == 2:
            editData[i]['colortype'] = 'グレー'
        elif colortype == 3:
            editData[i]['colortype'] = '青系'
        elif colortype == 4:
            editData[i]['colortype'] = '赤系'
        elif colortype == 5:
            editData[i]['colortype'] = '緑系'
        elif colortype == 6:
            editData[i]['colortype'] = '黄系'

        # 店名
        parking_sid = str(parkingdata['sid_id'])
        storeFilterData = storeData.filter(sid=parking_sid)
        sname.append(storeFilterData[0]['sname'])

        i += 1

    # CarTableからImageID取得
    carData = CarTable.objects.all().values()

    imageData = ImageTable.objects.all().values()

    for cardata in carData:
        # 追加済みかチェックしたほうがよさそう
        car_imageid = cardata['imageid_id']
        car_sid = cardata['sid_id']
        imgPath = ''

        # car_imageidから画像名取得する
        if car_imageid != None:
            imageFilterData = imageData.filter(sid=car_sid)
            imgPath = imageFilterData[0]['path']

        car_sid = cardata['sid_id']

        if car_imageid != None:
            numberPlateImages.append('http://' + request.get_host() + '/media_' + str(car_sid) + '/' + os.path.basename(imgPath))

            # imgs.append( 'http://' + request.get_host() + '/media_' + image_sid + '/' + os.path.basename(imgPath) )
            # imgName.append(os.path.basename(imgPath).replace('.', '_'))

    print(str(numberPlateImages))

    # car_imageid = str(carData['imageid_id'])
    # car_sid = str(carData['sid_id'])
    # storeFilterData = storeData.filter(sid=parking_sid)


    dataList = []
    for i, _ in enumerate(editData):
        dataList.append({
            'parking': editData[i],
            'sname': sname[i],
        })
    print(dataList)
    print(len(dataList))

    template = loader.get_template('web/parking_bulma.html')
    context = {
        'location_parking': True,
        'dataList': dataList,
        'numberPlate': numberPlateImages,
    }
    return HttpResponse(template.render(context, request))

#
# 設定 , 従業員追加
#
def setting(request):

    sessionSid = '0000'

    #
    # 従業員の追加
    #
    if 'eid' in request.POST:

        req_eid = request.POST['eid']
        req_ename = request.POST['ename']
        req_passward = request.POST['passward']
        req_status = 2

        EmployeeTable(eid=req_eid,
                      employeename=req_ename,
                      password=req_passward,
                      sid_id=sessionSid,
                      status=req_status,
                      plebel=0).save()

    template = loader.get_template('web/configuration_bulma.html')
    context = {
        'location_setting': True,
    }
    return HttpResponse(template.render(context, request))


@login_required
def mypage(request):
    return render(request, 'web/mypage.html')

@login_required
def redilect(request):
    return render(request, 'web/redirect.html')
