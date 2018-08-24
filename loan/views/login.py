# Create your views here.
import json
import logging
import re
import traceback

from django import forms
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from loan.checkUtil import setToken, smsTemplate, TEST_MODEL
from loan.common import set_response, getRequestUid, getRandomNumber, getXmlEle
from loan.util import getTimeStamp, getTodayZeroTime, sendSms
from ..models import User, Sms, Medium_Statistics, Medium, MediumLink

logging = logging.getLogger("login")


# 校验手机
def checkMobile(mobile):
    pattern = re.compile(r"^1[3-9]\d{9}$")
    return pattern.match(mobile)


# 登录参数校验Z
class LoginForm(forms.Form):
    mobile = forms.CharField(required=True, error_messages={'required': '手机号不能为空'})
    validCode = forms.CharField(required=True, error_messages={'required': '验证码不能为空'})
    amount = forms.CharField(required=True, error_messages={'required': '额度不能为空'})


# 获取验证码参数校验
class validCodeForm(forms.Form):
    mobile = forms.CharField(required=True, error_messages={'required': '手机号不能为空'})


# 注册校验
class RegisterForm(forms.ModelForm):
    nick = forms.CharField(required=True, error_messages={'required': '姓名不能为空'})
    idCard = forms.CharField(required=True, error_messages={'required': '身份证号不能为空'})
    estate = forms.CharField(required=True, error_messages={'required': '请勾选房产选项'})
    car = forms.CharField(required=True, error_messages={'required': '车产信息未勾选'})
    card = forms.CharField(required=True, error_messages={'required': '信用卡信息未勾选'})
    sex = forms.IntegerField(required=True, error_messages={'required': '性别信息未勾选'})
    city = forms.IntegerField(required=True, error_messages={'required': '城市信息未勾选'})
    lifeInsurance = forms.CharField(required=True, error_messages={'required': '寿单信息未勾选'})
    feeInsurance = forms.CharField(required=True, error_messages={'required': '年保费信息未勾选'})
    livingTime = forms.CharField(required=True, error_messages={'required': '居住时间未勾选'})
    profession = forms.CharField(required=True, error_messages={'required': '职业信息未勾选'})
    income = forms.CharField(required=False, error_messages={'required': '收入信息未勾选'})
    provident = forms.CharField(required=False, error_messages={'required': '公积金信息未勾选'})
    workExp = forms.CharField(required=False, error_messages={'required': '工作时间信息未勾选'})
    productIndex = forms.IntegerField(required=False)
    salaryPayment = forms.IntegerField(required=False)
    overdue = forms.IntegerField(required=False)
    secure = forms.CharField(required=False)

    class Meta:
        model = User
        exclude = ['id', 'source', 'sourceLink', 'amount', 'isDone', 'createAt', 'updateAt', 'mobile', 'linkId',
                   'doneAt', 'productIndex']


# 登录
@csrf_exempt
def login(request):
    user = {}
    userInfo = {}
    message = None
    code = -1
    logging.info("login start")
    try:
        if request.method == 'POST':
            obj = LoginForm(request.POST)
            ret = obj.is_valid()
            if ret:
                mobile = request.POST.get('mobile', None)
                amount = request.POST.get('amount', None)
                validCode = request.POST.get('validCode', None)
                # 媒介
                mediumId = request.POST.get('source', 0)
                # 处理传空字符串问题
                if not mediumId:
                    mediumId = 0
                # 处理传空字符串问题
                linkId = request.POST.get('sub', None)
                if not linkId:
                    linkId = None
                url = request.POST.get('url', None)
                # 完整的链接
                host = request.get_host()
                path = request.get_full_path()
                referer = request.META.get('HTTP_REFERER ', '')
                logging.info("host is %s ,path is %s ,referer is  %s", host, path, referer)
                logging.info("mobile is %s ,amount is %s ,validCode is %s , mediumId is %s, linkId is %s,url is %s",
                             mobile, amount, validCode, mediumId, linkId, url)

                # 验证手机
                if checkMobile(mobile):
                    code = 0
                    # 验证码
                    # 获取验证码

                    sms = Sms.objects.filter(mobile=mobile, msg=validCode).order_by('-sendAt')[0:1].first()
                    logging.info("TEST_MODEL is %s", TEST_MODEL)

                    if TEST_MODEL and validCode == '555555':
                        pass
                    else:
                        if sms:
                            logging.info("last sms id is " + sms.id.__str__() + " code is " + sms.msg)
                            if sms and (getTimeStamp() - sms.createAt) <= 600000:
                                pass
                            else:
                                logging.info("this sms sent at %s ,now is %s ", sms.createAt, getTimeStamp())
                                code = -1005
                                return set_response(code, None, {})
                        else:
                            logging.info("sms is not found")
                            code = -1004
                            return set_response(code, None, {})

                    # 判断手机号是否注册
                    users = User.objects.filter(mobile=mobile)
                    if users.exists():
                        user = users.first()
                        # 设置用户当前已看过的产品数量
                        logging.info("update user productIndex")
                        user.productIndex = user.productIndex + 3
                        user.save()
                        logging.info("this user id is " + user.id.__str__() + ",isDone is " + user.isDone.__str__())
                        # 已注册用户验证是否填写表单
                        if user.isDone == 0:
                            code = -1
                        user = user.to_dire()

                    else:
                        logging.info("mobile is not register")
                        nUser = User(mobile=mobile, nick='新用户', amount=amount, createAt=getTimeStamp(),
                                     updateAt=getTimeStamp(), source=mediumId, linkId=linkId, sourceLink=url)
                        nUser.save()
                        logging.info("create mew user success ,id is " + nUser.id.__str__())
                        # 媒介用户统计
                        if mediumId != 0:
                            updateMediumStatistics(mediumId, linkId, nUser.id, 'new')

                        code = -1
                        user = nUser.to_dire()
                        pass
                    # 设置简单token
                    userInfo = setToken(user.get('id').__str__(), mobile)
                else:
                    code = -1000
            else:
                message = obj.errors
        else:
            return
        # 加密用户信息
        response = HttpResponse(set_response(code, message, user), content_type='application/json')
        response.set_cookie('user', userInfo, max_age=24 * 60 * 60)
        return response
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        code = -10000
        return set_response(code, message, {})
    finally:
        pass


# 发送验证码
@csrf_exempt
def sendCode(request):
    logging.info("get validCode start")
    code = 0
    response = {
        # 'validCode': None
    }
    obj = validCodeForm(request.GET)
    if obj.is_valid():
        mobile = request.GET.get('mobile', None)
        logging.info("mobile is " + mobile)
        if mobile:
            # 查短信记录
            # 开始时间
            start = getTodayZeroTime()
            end = getTodayZeroTime() + 86400000 - 1
            smsList = Sms.objects.filter(mobile=mobile, sendAt__range=(start, end)).order_by('-sendAt')
            logging.info('size is ' + smsList.count().__str__())
            if smsList.count() >= 5:
                code = -1002
            else:
                # 获取上一条短信发送时间
                if smsList.exists():
                    lastSms = smsList.first()
                    logging.info(
                        "last sms id is " + lastSms.id.__str__() + " send at " + lastSms.sendAt.__str__() + 'now is ' + getTimeStamp().__str__())
                    # 发送时间不能小于1分钟
                    if getTimeStamp() - lastSms.sendAt < 60000:
                        code = -1003
                        return set_response(code, None, response)
                    else:
                        pass
                # 获取随机码
                randomCode = getRandomNumber(6)
                if TEST_MODEL:
                    # 本地测试用
                    # 本地测试用

                    xml = '<?xml version="1.0" encoding="gb2312"?><Root><Result>1</Result><CtuId>01805231841490003630</CtuId><SendNum>1</SendNum><MobileNum>1</MobileNum></Root>'
                else:
                    # 发送验证码
                    ret = sendSms(mobile, smsTemplate(randomCode))
                    logging.info('ret is ' + ret.url)
                    logging.info('ret is ' + ret.text)
                    # 解析xml结果
                    xml = ret.text

                logging.info("xml is " + xml)
                root = getXmlEle(xml)
                result = root.findall('Result')

                for note in result:
                    logging.info("key is " + note.tag.__str__())
                    logging.info("value is " + note.text.__str__())
                    # 不为1则发送失败
                    if note.text != '1':
                        # if False:
                        code = -1001
                    else:
                        sms = Sms(mobile=mobile, msg=randomCode, createAt=getTimeStamp(), updateAt=getTimeStamp(),
                                  sendAt=getTimeStamp())
                        sms.save()
                        logging.info("sms save success")


        else:
            code = -1000
    else:
        code = -1000
    return set_response(code, None, response)


# 填写表单
@csrf_exempt
def editUserInfo(request, uid):
    if request.method == 'POST':
        code = 0
        message = None
        req = request.POST
        try:
            logging.info("edit user info start")
            logging.info("uid is " + uid.__str__())

            # 验证用户身份
            checkForm = RegisterForm(request.POST)
            if uid.__str__() == getRequestUid(request):
                if checkForm.is_valid():
                    logging.info("update user start")
                    user = User.objects.get(id=uid)
                    # 职业验证
                    profession = req.get('profession', None)
                    income = req.get('income', 0)
                    workExp = req.get('workExp', 0)
                    provident = req.get('provident', 0)
                    flag = income + workExp + provident
                    logging.info("flag is %s,", flag)
                    if profession == '2':
                        logging.info("this user is not student")
                        pass
                    elif not income or not provident or not workExp:
                        code = -10
                        return set_response(code, message, {})
                    # 新用户记录填表时间
                    if user.isDone == 0:
                        user.isDone = 1
                        user.doneAt = getTimeStamp()
                        # 用户转变统计
                        linkId = user.linkId
                        mediumId = user.source
                        logging.info("create a new register data")
                        updateMediumStatistics(mediumId, linkId, uid, 'old')
                        pass
                    else:
                        logging.info("this user is old")
                        pass
                    user.updateAt = getTimeStamp()
                    user_form_obj = RegisterForm(request.POST, instance=user)
                    user_form_obj.save()
                    logging.info("update user end")
                else:
                    code = -30
                    message = checkForm.errors
                    pass
            else:
                code = -10
                pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})
    else:
        return


# 用户详情
@csrf_exempt
def getUserInfo(request, uid):
    logging.info("edit user info start")
    logging.info("uid is " + uid.__str__())
    if uid.__str__() == getRequestUid(request):
        logging.info("get user detail start")
        code = 0
        user = User.objects.get(id=uid)
        logging.info("get user detail end")
    else:
        code = -10
        return set_response(code, None, {})
    return set_response(code, None, user.to_dire())


# 更新媒介统计信息
def updateMediumStatistics(mediumId, linkId, uid, type):
    try:
        if mediumId and linkId:

            mediumStatistics = Medium_Statistics.objects.filter(
                createAt__range=(getTodayZeroTime(), getTimeStamp() + 86399999), mediumId=mediumId,
                linkId=linkId).first()
            if mediumStatistics:
                logging.info("update today register data")
                mediumStatistics.updateAt = getTimeStamp()
                # 记录新用户数量
                if type == 'new':
                    logging.info("a new user")
                    newIds = json.loads(mediumStatistics.newIds)
                    newIds.append(uid)
                    mediumStatistics.newIds = json.dumps(newIds)
                    mediumStatistics.newCount = mediumStatistics.newCount + 1
                else:
                    logging.info("a old user")
                    oldIds = json.loads(mediumStatistics.oldIds)
                    oldIds.append(uid)
                    mediumStatistics.oldIds = json.dumps(oldIds)
                    mediumStatistics.oldCount = mediumStatistics.oldCount + 1

                    # 检查今天新用户有没有这个人，有的话清掉
                    newIds = json.loads(mediumStatistics.newIds)
                    if newIds.__contains__(uid):
                        logging.info("remove this uid ,uid is %s", uid)
                        newIds.remove(uid)
                        mediumStatistics.newIds = json.dumps(newIds)
                        mediumStatistics.newCount = mediumStatistics.newCount - 1
                        pass
                    else:
                        logging.info("the statistics new ids is not found this uid")
                        pass
                mediumStatistics.save()
            else:
                logging.info("create a new register data")
                medium = Medium.objects.get(id=mediumId)
                link = MediumLink.objects.get(id=linkId)
                if medium and link:
                    mediumStatistics = Medium_Statistics(updateAt=getTimeStamp(), createAt=getTimeStamp(),
                                                         mediumId=mediumId,
                                                         mediumName=medium.name, linkId=linkId,
                                                         link=link.link)
                    if type == 'new':
                        logging.info("a new user")
                        mediumStatistics.newIds = json.dumps([uid])
                        mediumStatistics.newCount = 1

                        mediumStatistics.oldIds = json.dumps([])
                        mediumStatistics.oldCount = 0

                    else:
                        logging.info("a old user")
                        mediumStatistics.oldIds = json.dumps([uid])
                        mediumStatistics.oldCount = 1
                        mediumStatistics.newIds = json.dumps([0])
                        mediumStatistics.newCount = 0
                    mediumStatistics.save()
                    pass
                else:
                    logging.info("this medium id or link id not found")
                    pass
                pass
            pass
        else:
            logging.info("this user's mediumId is not found")
            pass
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        pass
    finally:
        pass
