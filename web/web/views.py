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


'''
画像のURLを生成する
'''
def create_image_url(host_address, sid, humanid, file_name, orgflg=False):
    if orgflg:
        return 'http://' + host_address + settings.MEDIA_URL + sid + '/original/' + file_name
    return 'http://' + host_address + settings.MEDIA_URL + sid + '/' + str(humanid) + '/' + file_name

# セッションの状態
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


'''
店舗ログインの画面
'''
def login_home_sid(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    template = loader.get_template('web/store_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))


'''
従業員ログインの画面
'''
def login_home_eid(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    template = loader.get_template('web/employee_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))


'''
店舗ログインの認証処理
'''
def login_auth_store(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    # if session_status_result != True:
    #     return session_status_result

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
                return HttpResponseRedirect('../login_eid/')
            else:
                print('Login Missed. PW')

        except StoreTable.DoesNotExist:
            print('Login Missed. sid')
            # ログイン情報が違う場合
            template = loader.get_template('web/store_login.html')
            context = {
                'location_home': True,
                'status':'店舗ログインに失敗しました。',
            }
            return HttpResponse(template.render(context, request), status=400)


    if 'logout' in request.POST:
        request.session.clear()


    if 'eid' not in request.session and 'sid' in request.session and 'spass' in request.session:
        # 従業員ログインへ
        return HttpResponseRedirect('../login_eid/')

    if 'sid' in request.session and 'spass' in request.session:
        name = request.session['sid']
        return HttpResponseRedirect('../')

    # 上記if文のどれにも、当てはまらない場合、店舗ログインへ
    return HttpResponseRedirect('../login_sid/')

'''
従業員ログインの認証処理
'''
def login_auth_employee(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    # if session_status_result != True:
    #     return session_status_result

    session_sid = request.session['sid']
    session_eid = ''

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
                    # ログイン情報が違う場合
                    template = loader.get_template('web/employee_login.html')
                    context = {
                        'location_home': True,
                        'status':'従業員ログインに失敗しました。',
                    }
                    return HttpResponse(template.render(context, request))


            except EmployeeTable.DoesNotExist:
                print('Login Missed. eid')
                # ログイン情報が違う場合
                template = loader.get_template('web/employee_login.html')
                context = {
                    'location_home': True,
                    'status': '従業員ログインに失敗しました。',
                }
                return HttpResponse(template.render(context, request), status=400)

        if 'logout' in request.POST:
            #e eid kesu
            request.session.clear()

        if 'eid' in request.session and 'epass' in request.session:
            name = request.session['eid']
            loggedIn = True

    # return render(request, "web/logined-eid.html", {'loggedIn': loggedIn, 'name': name})
    return HttpResponseRedirect('../')

'''
ログアウト処理
'''
def logout(request):
    # セッション削除
    request.session.clear()

    # 店舗ログインに遷移
    template = loader.get_template('web/store_login.html')
    context = {
        'location_home': True,
    }
    return HttpResponse(template.render(context, request))




'''
トップページ
'''
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
            news_ary.append({'url':'ihochusha', 'comment':news_comment})
            news_ihouchusha_ary.append({'url':'ihochusha', 'comment':news_comment})
        if NewsType.BLACK_LIST.value == news_type:
            news_ary.append({'url':'blacklist', 'comment':news_comment})
            news_blacklist_ary.append({'url':'blacklist', 'comment':news_comment})

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


'''
画像一覧ページ
'''
def image(request):
    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    session_sid = request.session['sid']
    session_eid = request.session['eid']

    imageid_dic = {}

    #
    # 画像一覧表示
    #
    humanTable = HumanTable.objects.filter(sid=session_sid).values()
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
        humanid = image['humanid_id']
        # image_url = 'http://' + request.get_host() + '/media_' + session_sid + '/' + os.path.basename(image['path'])
        image_url = create_image_url(request.get_host(), session_sid, '', os.path.basename(image['path']), True)
        org_imageid = str(image['imageid'])
        child_imageid_list = not_org_image_datas.filter(originalimageid=org_imageid) # 同じ写真に写っている人
        child_imageid_ary = []

        # 写真に2人以上写っている場合は、その個別の画像のパスを配列にする
        if len(child_imageid_list) != 0:
            for child_imageid in child_imageid_list:
                child_humanid = child_imageid['humanid_id']
                # child_image_url = 'http://' + request.get_host() + '/media_' + session_sid + '/' + os.path.basename(child_imageid['path'])
                child_image_url = create_image_url(request.get_host(), session_sid, child_humanid, os.path.basename(child_imageid['path']))
                black_flag = str(humanTable.filter(humanid=child_humanid).values().first()['blflg'])
                child_imageid_ary.append([{'path':child_image_url}, {'bl':black_flag}])
                imageid_dic[child_image_url] = str(child_imageid['imageid'])
        else:
            # 一人しか写っていない場合。
            child_image_url = create_image_url(request.get_host(), session_sid, humanid, os.path.basename(image_url), True)
            child_imageid_ary.append([{'path':child_image_url}, {'bl':'False'}])

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


    #
    # ブラックリストFlagのある画像だけ取り出す
    #
    blFlagImagePath = []
    for imagedata in org_image_datas:
        imageHumanId = imagedata['humanid_id']
        if imageHumanId == None:
            continue

        try:
            HumanFilterData = humanTable.filter(humanid=imageHumanId)
            blFlag = HumanFilterData[0]['blflg']

            if blFlag:
                # blFlagImagePath.append('http://' + request.get_host() + '/media_' + str(imagedata['sid_id']) + '/' + os.path.basename(imagedata['path']))
                blFlagImagePath.append(create_image_url(request.get_host(), session_sid, imageHumanId, os.path.basename(imagedata['path'])))
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
            # 'bl_flag': imgs[i][3],
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


'''
ブラックリスト
'''
def blacklist(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    session_sid = request.session['sid']

    '''
    ブラックリストの解除
    '''
    if 'blacklist_humanid' in request.POST:
        req_humanid = request.POST['blacklist_humanid']
        human_table = HumanTable.objects.filter(sid=session_sid, blflg=True, humanid=req_humanid).values()
        human_table.update(blflg=False) # フラグをFalseにして更新

    # ブラックリストに登録されているhumanidを取り出す
    human_tables = HumanTable.objects.filter(blflg=True).values()
    image_tables = ImageTable.objects.filter(sid=session_sid).values()
    blacklist_image_list = [[]]
    count = []

    for data in human_tables:
        humanid = str(data['humanid'])
        imagetable_filter_human = image_tables.filter(humanid=humanid).values()
        blacklist_human_imagepath = []

        for blacklist_human_image in imagetable_filter_human:
            blacklist_human_imagepath.append( create_image_url(request.get_host(), session_sid, humanid, os.path.basename(blacklist_human_image['path'])))

        blacklist_image_list.append([
                                     {'filename':os.path.basename(imagetable_filter_human[0]['path']).replace('.', '')},
                                     {'first':create_image_url(request.get_host(), session_sid, humanid, os.path.basename(imagetable_filter_human[0]['path']))},
                                     {'all':blacklist_human_imagepath},
                                     {'humanid': humanid}
                                    ])
        count.append('')

    blacklist_image_list.pop(0)
    print(blacklist_image_list)

    # テンプレートで使用する変数を1つにまとめる
    dataList = []
    for i, _ in enumerate(count):
        dataList.append({
            'filename': blacklist_image_list[i][0]['filename'],
            'first': blacklist_image_list[i][1]['first'],
            'all': blacklist_image_list[i][2]['all'],
            'humanid': blacklist_image_list[i][3]['humanid'],
        })

    template = loader.get_template('web/blacklist_bulma.html')
    context = {
        'location_bl': True,
        'dataList': dataList,
    }
    return HttpResponse(template.render(context, request))

'''
違法駐車
'''
def parking(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    session_sid = request.session['sid']
    session_eid = request.session['eid']

    # 迷惑駐車の情報登録(WEB用)
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

    # DBからpath列のデータをすべて取得
    parkingData = CarTable.objects.all().values()
    editData = parkingData
    storeData = StoreTable.objects.all().values()
    sname = []
    numberPlateImages = [] # ナンバープレート画像

    i = 0
    for parkingdata in parkingData:
        colortype = parkingdata['colortype']

        # 0:普通, 1:軽自動車, 3:事業用普通, 4:事業用系自動車, 5:外交官
        if colortype == 0:
            editData[i]['colortype'] = '白'
        elif colortype == 1:
            editData[i]['colortype'] = '黄'
        elif colortype == 2:
            editData[i]['colortype'] = '緑'
        elif colortype == 3:
            editData[i]['colortype'] = '黒'
        elif colortype == 4:
            editData[i]['colortype'] = '青' # 外交官

        # 店名
        parking_sid = str(parkingdata['sid_id'])
        storeFilterData = storeData.filter(sid=parking_sid)
        sname.append(storeFilterData[0]['sname'])

        i += 1

    dataList = []
    for i, _ in enumerate(editData):
        dataList.append({
            'parking': editData[i],
            'sname': sname[i],
        })

    template = loader.get_template('web/parking_bulma.html')
    context = {
        'location_parking': True,
        'dataList': dataList,
        'numberPlate': numberPlateImages,
    }
    return HttpResponse(template.render(context, request))

'''
設定　：　店舗情報の閲覧・従業員追加
'''
def setting(request):

    sessionManager = SessionManager()
    session_status = sessionManager.loginCheck(request)
    session_status_result = sessionManager.redirecter(request, session_status)

    if session_status_result != True:
        return session_status_result

    session_sid = request.session['sid']
    session_eid = request.session['eid']

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
                      sid_id=session_sid,
                      status=req_status,
                      plebel=0).save()


    '''
    WEB表示
    '''
    setting_dic = {}
    storetable = StoreTable.objects.filter(sid=session_sid).values().first()
    # 店舗情報
    setting_dic['address'] = storetable['address']
    setting_dic['store_pass'] = storetable['password']

    # アカウント情報(ログイン中の従業員パス)
    employeetable = EmployeeTable.objects.filter(sid=session_sid, eid=session_eid).values().first()
    setting_dic['employee_pass'] = employeetable['password']

    # 従業員一覧
    employee_list = []
    employeetable = EmployeeTable.objects.filter(sid=session_sid).values()
    for data in employeetable:
        employee_list.append({'eid':data['eid'],
                              'ename':data['employeename'],
                              'epass':data['password'],
                              'sid':data['sid_id'],
                              'date':data['date']})
    setting_dic['employee_list'] = employee_list

    template = loader.get_template('web/configuration_bulma.html')
    context = {
        'location_setting': True,
        'setting_dic': setting_dic,
    }
    return HttpResponse(template.render(context, request))


'''
掲示板
'''
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

@login_required
def mypage(request):
    return render(request, 'web/mypage.html')

@login_required
def redilect(request):
    return render(request, 'web/redirect.html')
