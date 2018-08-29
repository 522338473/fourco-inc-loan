import json
import logging
import traceback

import requests
from django.views.decorators.csrf import csrf_exempt

from loan.common import set_list_response, DynamicQuery, set_response
from loan.constant import constant
from loan.models import Product, MediumLink, Product_User_Relation, Product_Statistics, User, Contents, \
    Recommend_Statistics, Record, Medium
from loan.util import getTimeStamp, getTodayZeroTime
from loan.views.loanForm import ProductForm

logging = logging.getLogger('product')


# 获取客户列表（会将用户信息给分单客户推送）
@csrf_exempt
def getProductList(request):
    logging.info("get product list start")
    if request.method == 'GET':
        productList = []
        req = request.GET

        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        total = 0
        code = 0
        logging.info("page is " + page.__str__() + " size is " + size.__str__())
        start = (page - 1) * size
        end = start + size

        try:
            ProductForm(request.GET)
            containsParams = ['name']
            fields = [f.name for f in Product._meta.fields]
            kwargs = DynamicQuery(request, containsParams, *fields)
            logging.info("query params is " + kwargs.__str__())
            # 取客户数据
            productList = Product.objects.filter(**kwargs, status=1).order_by('sort', '-createAt')
            productIds = list(productList.values_list('id', flat=True))
            logging.info("product ids is %s", productIds)
            total = productList.count()
            logging.info("list size is " + productList.count().__str__())
            # 取用户信息
            user = json.loads(request.__getattribute__('user'))
            linkId = user.get('linkId')
            # 取对应链接
            link = MediumLink.objects.filter(id=linkId).first()
            if link:
                logging.info("linkId is %d", linkId)
                # 判断该链接是否有排序
                if link.productSort1 or link.productSort2:
                    type = req.get('type', None)
                    productSort = []

                    #  获取链接下客户排序id list
                    if type == 1:
                        logging.info("link.productSort2 is %s", link.productSort1)
                        if link.productSort1:
                            productSort = json.loads(link.productSort1)
                    else:
                        logging.info("link.productSort2 is %s", link.productSort2)
                        if link.productSort2:
                            productSort = json.loads(link.productSort2)
                    logging.info("productSort is %s", productSort)

                    newList = []

                    # 当链接下有排序数据时，进行排序
                    if len(productSort) > 0:
                        if len(productIds) > len(productSort):
                            logging.info("Sort missing some id, should be push  ")
                            differenceIds = list(set(productIds).difference(set(productSort)))
                            logging.info("difference is %s", differenceIds)
                            productSort.extend(differenceIds)
                        # 按 id 入参顺序进行排序
                        logging.info("sort start")
                        productList = dict([(product.id, product) for product in productList])
                        for productId in productSort:
                            logging.info("productList item is %s", productList.get(productId))
                            if productList.get(productId, None):
                                newList.append(productList[productId])
                                pass
                            else:
                                logging.info("item not found ,id is %s", productId)
                                pass
                        pass
                        productList = newList
                        logging.info("new list is %s", newList)
                    # 链接下没有拍数据时 按照
                    else:
                        # QuerySet to list
                        logging.info("queryset to list %s", productList)
                        # productList = list(productList)
                        pass
                    pass
                else:
                    logging.info("this link productSort is null")
                    pass
            productList = list(productList)
            allList = productList.copy()

            # 输出新排序 只有当type是分单的时候才进行切割处理
            if req.get('type') == '1':
                # 用户当前看到的排序下标
                productIndex = user.get('productIndex')
                logging.info('user  linkId is %s productIndex is %s', linkId, productIndex)
                '''
                根据下标除以数据量取余，判断是否需要进行数据填充
                '''
                if productIndex > total:
                    n = productIndex % total
                else:
                    n = productIndex
                # 预补一次数据用以展示
                # productList.extend(productList)
                if len(productList) > 3:
                    productList.extend(productList)
                    productList = list(productList[n:n + size])
                    pass
                else:
                    pass
                logging.info("list size is %s", len(productList))

                # 将用户分发给客户, 获取N值
                content = Contents.objects.get(id=1)
                valueN = int(content.value)
                logging.info("content N is %d", valueN)

                # 每次登录根据用户登录次数和n值取推送的数据进行推送
                allList.extend(allList)
                pushList = list(allList[n:n + valueN])
                logging.info("push limit is %d - %d", n, n + valueN)
                # 调用数据推送方法
                distributionOrder(request, uid=user.get('id'), productList=pushList)
                pass
            # type为推荐的时候不切割数据
            else:
                productList = list(productList[start:end])
                logging.info("list size is %s", len(productList))
                logging.info("list  is %s", productList)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = - 10000
        finally:
            return set_list_response(code, None, productList, page, size, total=total)
        pass
    else:
        return


# 获取客户信息
@csrf_exempt
def getProductDetail(request, productId):
    logging.info("get product start")
    product = {}
    code = 0
    if request.method == 'GET':
        try:

            if not productId:
                code = -10
            else:
                querySet = Product.objects.filter(id=productId)
                if querySet.exists():
                    product = querySet.first().to_dire()
                    logging.info("product is %s", product)
                else:
                    code = -30
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, None, product)
    else:
        return


# 推荐数据客户PV、UV统计
@csrf_exempt
def recommendStatistics(request):
    logging.info("recommend product statistics")
    code = 0
    if request.method == 'POST':
        req = request.POST
        try:
            productId = req.get("productId", None)
            if not productId:
                code = -10
                return set_response(code, None, None)
            else:
                logging.info("productId is %s", productId)
            user = json.loads(request.__getattribute__("user"))
            uid = user.get("id")
            mediumId = user.get('source')
            linkId = user.get('linkId')
            if not mediumId or not linkId:
                logging.info("this user's medium or linkId is not found")
                pass
            else:
                logging.info("this user's medium is %s, linkId is %s", mediumId, linkId)
                medium = Medium.objects.filter(id=mediumId).first()
                product = Product.objects.filter(id=productId).first()
                # 查询这名用户是否有这个推荐产品的访问记录
                logging.info("product is %s", product.to_dire())
                oRecord = Record.objects.filter(userId=uid, productId=productId, createAt__gte=getTodayZeroTime(),
                                                createAt__lte=getTimeStamp()).first()

                # 生成访问记录，每条记录都保存
                record = Record(createAt=getTimeStamp(), updateAt=getTimeStamp(), userId=uid, mediumId=mediumId,
                                linkId=linkId, productId=productId)
                record.save()
                logging.info("add record success")
                '''
                统计数据，如果该媒介链接相关统计数据存在，则进行修改，否则进行新增
                '''
                recommendStatistics = Recommend_Statistics.objects.filter(linkId=linkId,
                                                                          productId=productId, createAt__range=(
                        getTodayZeroTime(), getTimeStamp() + 86399999)).first()
                # 数据存在，进行修改
                if recommendStatistics:
                    recommendStatistics.pv = recommendStatistics.pv + 1
                    # 根据访问记录是否存在判断是否更新uv
                    if not oRecord:
                        recommendStatistics.uv = recommendStatistics.uv + 1
                        pass
                    recommendStatistics.save()
                    pass
                # 数据不存在，进行新增
                else:
                    Recommend_Statistics(mediumId=mediumId, linkId=linkId, createAt=getTimeStamp(),
                                         updateAt=getTimeStamp(), productId=productId, pv=1, uv=1,
                                         mediumName=medium.name, productName=product.name).save()
                    pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
        finally:
            return set_response(code, None, None)
    else:
        return


#  分单操作
def distributionOrder(request, uid, productList: list):
    logging.info("distributionOrder start:uid is %d,ids is %s", uid, productList)
    try:
        for product in productList:
            logging.info("product id is %d", product.id)
            # 查分单记录
            relation = Product_User_Relation.objects.filter(userId=uid, productId=product.id)
            # 没有记录则执行分单推送操作，推送成功，则生成分单关系
            if not relation.exists():
                # 给分单客户发用户信息
                # 查token是否存在，不存在直接跳过这条数据
                if product.token:
                    logging.info("this product token is %s", product.token)
                    pass
                else:
                    logging.error("this product token is not found")
                    continue
                # 查用户信息
                user = User.objects.filter(id=uid).first()
                if user:
                    logging.info("sendUserData start")
                    result = sendUserData(product.token, product, user)
                    sec_result = secure(request, user)
                    if sec_result.error_code == 0:
                        user.secure = sec_result.company
                        user.save()
                    logging.info('sendUserData response is  %s', result.text)
                    if result.status_code == 200:
                        result = result.json()
                        if result.get('errorCode') != 0:
                            # 推送不成功直接跳过数据
                            logging.error("sendUserData error ,message is %s", result.get('errMsg'))
                            continue
                        else:
                            logging.info("sendUserData success")
                            pass
                        pass
                    else:
                        # 推送不成功直接跳过数据
                        logging.error("sendUserData error,result.status_code is %s", result.status_code)
                        continue
                    pass
                else:
                    # 推送不成功直接跳过数据
                    logging.info("user data error or user medium is null")
                    continue
                # 到这里已经说明信息推送客户成功了
                # 建立用户客户关系-记录名称为归属信息
                relation = Product_User_Relation(userId=uid, productId=product.id, createAt=getTimeStamp(),
                                                 updateAt=getTimeStamp(), productName=product.belongName)
                relation.save()
                logging.info("create relation success")

                # 分单统计
                # productStatistics = Product_Statistics.objects.filter(productId=product.id, createAt__range=(
                productStatistics = Product_Statistics.objects.filter(productName=product.belongName, createAt__range=(
                    getTodayZeroTime(), getTimeStamp() + 86399999)).first()
                if productStatistics:
                    logging.info("update today statistics data")
                    productStatistics.updateAt = getTimeStamp()
                    # 记录新分单用户
                    logging.info("a new order")
                    productStatistics.orderCount = productStatistics.orderCount + 1
                    productStatistics.save()
                else:
                    logging.info("create a new statistics data")
                    product = Product.objects.get(id=product.id)
                    if product:
                        productStatistics = Product_Statistics(updateAt=getTimeStamp(), createAt=getTimeStamp(),
                                                               productId=product.id, orderCount=1,
                                                               productName=product.belongName)
                        productStatistics.save()
                        pass
                    else:
                        logging.info("this product not found")
                        pass
                    pass
                pass
            else:
                logging.info("this relation is exists")
                pass
            pass
        pass
    except Exception as e:
        logging.error(e)
        pass
    finally:
        pass


def sendUserData(token, product, user: User):
    logging.info('user is %s', user.to_dire().__str__())
    params = {
        'token': token,
        'data': {}
    }
    userData = {
        'name': user.nick,
        'phone': user.mobile,
        'media': product.pushName,
        'loan_limit': user.amount,
        'repay_term': 12,
        'credit': user.overdue,
        'house': 0,
        'car': 0,
        'is_work': 0,
        'is_fund': 0,
        'is_insurance': 0,
        'id_card': user.idCard,
        'city_id': user.city,
        'profession': user.profession,
        'gender': 0,
        'salary_bank_private': user.salaryPayment,
        'salary': 0
    }

    if not userData['media']:
        userData['media'] = product.name
        pass

    if user.estate == 3:
        userData['house'] = 0
        pass
    else:
        userData['house'] = 1
        pass
    if user.car == 3:
        userData['car'] = 0
        pass
    else:
        userData['car'] = 1
        pass
    if user.profession == 5:
        userData['is_work'] = 0
        pass
    else:
        userData['is_work'] = 1
        pass
    if user.provident == 3:
        userData['is_fund'] = 0
        pass
    else:
        userData['is_fund'] = 1
        pass
    if user.lifeInsurance == 2:
        userData['is_insurance'] = 0
        pass
    else:
        userData['is_insurance'] = 1
        pass
    if user.sex == 1:
        userData['gender'] = 1
        pass
    else:
        userData['gender'] = 0
        pass
    if user.income == 1:
        userData['salary'] = 4000
        pass
    elif user.income == 2:
        userData['salary'] = 6000
        pass
    elif user.income == 3:
        userData['salary'] = 10000
        pass

    params['data'] = userData
    logging.info("params is %s", json.dumps(params))
    return requests.post(constant.zdAPI, data=json.dumps(params))


import pyDes
import base64
import hashlib


Des_Key = b"f2155bca"                                 # Key
Des_IV = b"\x22\x33\x35\x81\xBC\x38\x5A\xE7"          # 自定IV向量


def desencrypt(s):
    k = pyDes.des(Des_Key, pyDes.ECB, Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
    encrystr = k.encrypt(s.decode())
    return base64.b64encode(encrystr)


def secure(request, user: User):
    base_url = 'https://www.heiniubao.com/insurance/enhanced'
    key = 'baoxian-$@'
    channel = 'jmposji'                                  # 一级渠道名
    subchannel = 'posjiapi1'                             # 二级渠道名
    name = user.nick                                     # 原始用户名
    phone = user.mobile                                  # 用户手机号
    id_card = user.idCard                                # 用户身份证
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']        # 用户真实ip
    else:
        ip = request.META['REMOTE_ADDR']                 # 用户本地ip
    if 'HTTP_USER_AGENT' in request.META:
        agent = request.META['HTTP_USER_AGENT']          # user_agent
    else:
        agent = None

    # 接口签名拼接字符串
    sign_body = id_card + name + phone + channel + key
    # 加密后的sign
    sign = hashlib.md5((sign_body).encode('utf-8')).hexdigest()

    des_name = desencrypt(name).decode()
    des_phone = desencrypt(phone).decode()
    des_id_card = desencrypt(id_card).decode()
    params = {
        'name': des_name,
        'phone': des_phone,
        'channel': channel,
        'subchannel': subchannel,
        'customer_ip': ip,
        'sign': sign,
        'id_no': des_id_card,
        'user_agent': agent
    }
    return requests.get(base_url, params=params)