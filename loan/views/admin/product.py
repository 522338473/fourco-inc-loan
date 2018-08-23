import json
import logging
import traceback

import xlwt
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response, DynamicQuery
from loan.models import Product, MediumLink, Product_Statistics, Medium, Contents, Recommend_Statistics
from loan.util import getTimeStamp, getTodayZeroTime, timeStampFormatDate
from loan.views.admin.adminForm import ProductForm, ContentsForm

logging = logging.getLogger("product")


def getProductList(request):
    logging.info("get product list start")
    if request.method == 'GET':
        req = request.GET
        code = 0
        page = req.get('page', 1)
        size = req.get('size', 10)
        total = 0
        productList = []
        try:
            target = None
            targetId = None
            # 需要进行模糊搜索的参数
            containsParams = ['name']
            fields = [f.name for f in Product._meta.fields]
            kwargs = DynamicQuery(request, containsParams, *fields)
            linkId = req.get('linkId', None)
            mediumId = req.get('mediumId', None)
            if linkId or mediumId:
                if linkId:
                    logging.info("is link sort")
                    targetId = linkId
                    target = MediumLink.objects.filter(id=linkId).first()
                    pass
                else:
                    logging.info("is medium sort")
                    targetId = mediumId
                    target = Medium.objects.filter(id=mediumId).first()
                pass
            logging.info("query params is %s", kwargs)
            productList = Product.objects.filter(**kwargs).order_by('sort', '-createAt')
            # 取出当前客户列表ids,避免出现新加了客户，但是不在排序列表里的情况出现，这里把排序里不存在的id push进去
            productIds = list(productList.values_list('id', flat=True))
            logging.info("product ids size is %d", len(productIds))
            logging.info("targetId is %s ", targetId)
            # 处理不同媒介、链接的排序，排序只能生效一种，链接优先
            if target:
                sort = []
                if req.get('type', None) == '1' and target.productSort1:
                    sort = json.loads(target.productSort1)
                    pass
                elif req.get('type', None) == '2' and target.productSort2:
                    sort = json.loads(target.productSort2)
                    pass
                newList = []
                # 开始把取出的结果按照载体顺序进行排序
                if len(sort) > 0:
                    # 把sort里没有的客户id推进去
                    if len(productIds) > len(sort):
                        logging.info("Sort missing some id, should be push  ")
                        differenceIds = list(set(productIds).difference(set(sort)))
                        logging.info("difference is %s", differenceIds)
                        sort.extend(differenceIds)
                    productList = dict((product.id, product) for product in productList)
                    logging.info("dict product is %s", productList)
                    # productList = [productList[pid] for pid in sort]
                    for productId in sort:
                        logging.info("productList item is %s , id is %s", productList.get(productId), productId)
                        # 先判断排序里的id是不是存在，可能出现改id被删除的情况，有的话就直接跳过
                        if productList.get(productId):
                            newList.append(productList[productId])
                            pass
                        else:
                            logging.info("item not found ,id is %s", productId)
                            pass
                        pass

                    productList = newList
                    logging.info("new list is %s", newList)
                    pass
                else:
                    # QuerySet to list
                    logging.info("queryset to list %s", productList)
                    productList = list(productList)
                    pass
                logging.info("sort size is %s", len(productList))
                pass
            else:
                total = productList.count()
                logging.info("list size is " + productList.count().__str__())
                productList = list(productList)
                pass
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_list_response(code, None, productList, page, size, total=total)
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


# 客户新增
@csrf_exempt
def createProduct(request):
    message = None
    code = 0
    pid = 0
    logging.info("create product start")
    if request.method == 'POST':
        try:

            req = request.POST
            obj = ProductForm(req)
            if obj.is_valid():
                pType = req.get('type', None)

                # 检查是否有重名元素
                product = Product.objects.filter(name=obj.cleaned_data.get('name'), type=obj.cleaned_data.get('type'))
                if product.exists():
                    code = -1041
                    return set_response(code, message, {})
                else:
                    product = Product(updateAt=getTimeStamp(), createAt=getTimeStamp())
                    pass

                # 表单元素转model
                # product = formToModel(Product(updateAt=getTimeStamp(), createAt=getTimeStamp()), obj)
                logging.info("type is " + pType)
                if pType == '1':
                    # 简介必填
                    introduce = req.get('introduce', None)
                    if introduce:
                        logging.info("introduce is %s", introduce)
                        product.introduce = introduce
                    else:
                        code = -1040
                        return set_response(code, message, {})
                elif pType == '2':
                    # url、利率必填
                    url = req.get('url', None)
                    rateStart = req.get('rateStart', None)
                    rateEnd = req.get('rateEnd', None)
                    if url and rateStart and rateEnd:
                        logging.info("url is %s ,rateStart is %s ,ratEnd is %s", url, rateStart, rateEnd)
                        product.url = url
                        product.rateStart = rateStart
                        product.rateEnd = rateEnd
                    else:
                        code = -1042
                        return set_response(code, message, {})
                else:
                    code = -10
                    return set_response(code, message, {})

                productObj = ProductForm(req, instance=product)
                result = productObj.save()
                logging.info('create product success')
                pid = result.id
            else:
                code = -10
                message = obj.errors
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, message, pid)
    else:
        return


# 客户修改
@csrf_exempt
def updateProduct(request, productId):
    message = None
    code = 0
    logging.info("update product start")

    if request.method == 'POST':
        try:
            # 校验数据是否存在
            product = Product.objects.get(id=productId)
            if not product:
                code = -30
                return set_response(code, message, {})
            else:
                pass

            req = request.POST
            product.updateAt = getTimeStamp()
            obj = ProductForm(req, instance=product)
            if obj.is_valid():
                pType = req.get('type', None)
                logging.info("type is %s", pType)

                # 检查是否有重名元素
                checkNameProduct = Product.objects.filter(name=req.get('name'), type=pType)
                if checkNameProduct.exists():
                    if checkNameProduct.first().id != productId:
                        code = -1041
                        return set_response(code, message, {})
                    else:
                        pass
                else:
                    pass

                if pType == '1':
                    # 简介必填
                    introduce = obj.cleaned_data.get('introduce')
                    if introduce:
                        logging.info("introduce is %s", introduce)
                    else:
                        code = -1040
                        return set_response(code, message, {})
                elif pType == '2':
                    # url、利率必填
                    url = obj.cleaned_data.get('url')
                    rateStart = req.get('rateStart', None)
                    rateEnd = req.get('rateEnd', None)
                    if url and rateStart and rateEnd:
                        logging.info("url is %s ,rateStart is %s ,ratEnd is %s", url, rateStart, rateEnd)
                        product.url = url
                        product.rateStart = rateStart
                        product.rateEnd = rateEnd
                    else:
                        code = -1042
                        return set_response(code, message, {})
                else:
                    code = -10
                    return set_response(code, message, {})

                obj.save()
                logging.info('create product success')

            else:
                code = -10
                message = obj.errors
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, message, productId)
    else:
        return


# 客户上下架
@csrf_exempt
def updateProductStatus(request, productId, status):
    message = None
    code = 0
    logging.info("update product start")
    logging.info("productId is %s status is %s", productId, status)

    if request.method == 'POST':
        try:
            # 校验数据是否存在
            product = Product.objects.get(id=productId)
            if not product:
                code = -30
                return set_response(code, message, {})
            # 校验分单客户是否配置,未配置可下架，不可上架
            else:
                if status == 1 and product.type == 1 and product.isConfig == 0:
                    code = -1044
                    return set_response(code, message, {})
            product.updateAt = getTimeStamp()
            product.status = status
            product.save()
            logging.info('update product status success')
        except Exception as e:
            code = -10000
            logging.error(e)
        finally:
            return set_response(code, message, productId)
    else:
        return


# 客户配置
@csrf_exempt
def updateProductConfig(request, productId, isConfig):
    message = None
    code = 0
    logging.info("update product isConfig start")
    logging.info("productId is %s isConfig is %s", productId, isConfig)

    if request.method == 'POST':
        try:

            # 校验数据是否存在
            product = Product.objects.get(id=productId)
            if not product:
                code = -30
                return set_response(code, message, {})
            # 设置未配置，自动下架
            if isConfig == 1 or isConfig == 0:
                if isConfig == 0:
                    product.status = 0
                pass
            else:
                code = -10
                return set_response(code, message, {})

            product.updateAt = getTimeStamp()
            product.isConfig = isConfig
            product.save()
            logging.info('update product isConfig success')
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, message, productId)
    else:
        return


# 客户排序
'''
以json传输数据 前端设置application/json请求头
'''


@csrf_exempt
def updateProductSort(request):
    message = None
    code = 0
    logging.info("update product start")
    if request.method == 'POST':
        try:
            #
            req = request.body
            jsonObj = json.loads(req)
            logging.info("json is %s", jsonObj)
            # 取排序id
            ids = jsonObj.get('ids', [])
            logging.info("ids size is %d", len(ids))
            # 取数据
            productList = Product.objects.filter(id__in=ids)
            logging.info("productList size is %s", productList.count())
            # 取排序类型
            sortType = jsonObj.get('type', 1)
            # 取客户类型
            productType = jsonObj.get('productType', None)
            if sortType != 1 and not productType:
                code = - 1043
                return set_response(code, None, {})
            medium = None
            if sortType == 1:
                logging.info("sort type is product")
                # 按 id 入参顺序进行排序
                productList = dict([(product.id, product) for product in productList])
                productList = [productList[productId] for productId in ids]

                i = 1
                for product in productList:
                    product.sort = i
                    product.save()
                    i += 1
            # 媒介下排序

            elif sortType == 2:
                logging.info("sort type is medium")
                mediumId = jsonObj.get('mediumId')
                if not mediumId:
                    code = -10
                    return set_response(code, None, {})
                else:
                    medium = Medium.objects.filter(id=mediumId).first()
                    pass
                # 获取媒介下链接未排序列表
                if productType == 1:
                    # 结果保存在媒介上
                    logging.info("update medium product sort,type is 1")
                    medium.productSort1 = json.dumps(ids)
                    medium.save()
                    linkList = MediumLink.objects.filter(productSort1__isnull=True, mediumId=mediumId)

                elif productType == 2:
                    logging.info("update medium product sort,type is 2")
                    medium.productSort2 = json.dumps(ids)
                    medium.save()
                    linkList = MediumLink.objects.filter(productSort2__isnull=True, mediumId=mediumId)
                else:
                    code = - 30
                    message = 'productType is request'
                    return set_response(code, message, {})
                logging.info("sort link size is %s", linkList.count())
                if productType == 1:
                    linkList.update(productSort1=json.dumps(ids), updateAt=getTimeStamp())
                else:
                    linkList.update(productSort2=json.dumps(ids), updateAt=getTimeStamp())

            # 链接下排序
            elif sortType == 3:
                logging.info("sort type is link")
                linkId = jsonObj.get('linkId')
                if not linkId:
                    code = -10
                    return set_response(code, None, {})
                else:
                    pass
                # 获取链接
                link = MediumLink.objects.filter(id=linkId).first()
                if link:
                    link.productSort = json.dumps(ids)
                    link.updateAt = getTimeStamp()
                    if productType == 1:
                        link.productSort1 = json.dumps(ids)
                    else:
                        link.productSort2 = json.dumps(ids)

                    link.save()
                else:
                    code = -30
                    return set_response(code, None, {})
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
        finally:
            return set_response(code, message, {})
    else:
        return


# 分单统计
@csrf_exempt
def getProductStatistics(request):
    if request.method == "GET":
        code = 0
        req = request.GET
        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        start = (page - 1) * size
        end = start + size
        total = 0
        statisticsList = []
        orderTotal = 0
        message = None
        try:
            fields = [f.name for f in Product_Statistics._meta.fields]
            kwargs = DynamicQuery(request, [], *fields)
            startTime = req.get("startTime", None)
            endTime = req.get("endTime", None)
            if startTime:
                kwargs.__setitem__("createAt__gte", startTime)
            if endTime:
                kwargs.__setitem__("createAt__lte", endTime)
            logging.info("kwargs is %s", kwargs)
            result = Product_Statistics.objects.filter(**kwargs).order_by('-createAt')
            total = result.count()
            orderTotal = 0
            # 当前条件总单数
            for statistics in result:
                orderTotal += statistics.orderCount

            logging.info('result size is %d ,orderTotal is %s', total, orderTotal)
            statisticsList = list(result[start:end])
            pass
        except Exception as e:
            logging.error(e)
            code = -10000
            pass
        finally:
            sup = {
                'orderTotal': orderTotal
            }
            return set_list_response(code, message, statisticsList, page, size, total, **sup)
        pass
    else:
        return


# 获取推荐统计
@csrf_exempt
def getRecommendProductStatistics(request):
    if request.method == "GET" or request.method == "POST":
        code = 0
        req = request.GET
        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        start = (page - 1) * size
        end = start + size
        total = 0
        statisticsList = []
        message = None
        try:
            startTime = str(req.get("startTime", getTodayZeroTime()))
            endTime = str(req.get("endTime", getTimeStamp()))
            productId = req.get("productId", None)
            logging.info("startTime is %s, endTime is %s, productId is %s", startTime, endTime, productId)
            sql = "1"
            if startTime:
                sql += " and rs.create_at >= " + str(startTime)
            if endTime:
                sql += " and rs.create_at <= " + str(endTime)
            if productId:
                sql += " and rs.product_id = " + productId

            logging.info("sql is %s", sql)
            result = Recommend_Statistics.objects.raw(
                "select rs.id,rs.medium_id,rs.medium_name,rs.product_id,rs.product_name,rs.link_id,"
                "(select count(distinct(loan_record.user_id)) from loan_record where rs.product_id=loan_record.product_id and rs.link_id=loan_record.link_id) uv,"
                "sum(rs.pv) as pv,rs.update_at,rs.create_at "
                "from loan_recommend_statistics as rs where " + sql + " group by rs.product_id,rs.link_id")
            total = len(list(result))
            logging.info('result size is %d', total)
            statisticsList = list(result[start:end])

            if req.get('output') == '1':
                # 指定返回为excel文件
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment;filename=statistics.xls'
                # 创建工作簿
                workbook = xlwt.Workbook(encoding='utf-8')
                # 创建工作页
                sheet = workbook.add_sheet("sheet1")
                row0 = [u'序号', u'日期', u'推荐客户名称', u'媒介名称', u'链接ID', u'UV',
                        u'PV']
                for i in range(0, len(row0)):
                    sheet.write(0, i, row0[i])
                num = 1
                logging.info("date is %s",
                             timeStampFormatDate(int(startTime), '%Y-%m-%d') + "~" + timeStampFormatDate(int(endTime),
                                                                                                         '%Y-%m-%d'))
                for d in list(result):
                    sheet.write(num, 0, num)
                    sheet.write(num, 1, timeStampFormatDate(int(startTime), '%Y-%m-%d') + "~" + timeStampFormatDate(
                        int(endTime), '%Y-%m-%d'))
                    sheet.write(num, 2, d.productName)
                    sheet.write(num, 3, d.mediumName)
                    sheet.write(num, 4, d.linkId)
                    sheet.write(num, 5, d.uv)
                    sheet.write(num, 6, d.pv)
                    num = num + 1
                workbook.save(response)
                return response
            else:
                sup = {
                    'startTime': startTime,
                    'endTime': endTime
                }
                return set_list_response(code, message, statisticsList, page, size, total, **sup)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            logging.info("startTime = getTimeStamp() %s", startTime)
            sup = {
                'startTime': startTime,
                'endTime': endTime
            }
            return set_list_response(code, message, statisticsList, page, size, total, **sup)
            pass
    else:
        return


# 添加常量
@csrf_exempt
def addContent(request):
    if request.method == "POST":
        code = 0
        req = request.POST
        message = None
        try:
            contentForm = ContentsForm(req)
            if contentForm.is_valid():
                logging.info("add content start")
                content = ContentsForm(req, instance=Contents(createAt=getTimeStamp(), updateAt=getTimeStamp()))
                result = content.save()
                logging.info("add content success ,id is %d", result.id)
                pass
            else:
                message = contentForm.errors
                code = -10
        except Exception as e:
            logging.error(e)
            code = -10000
            pass
        finally:
            return set_response(code, message, {})
        pass
    else:
        return


# 查看/修改常量
@csrf_exempt
def getOrUpdateContent(request, contentId):
    code = 0
    message = None
    if request.method == "PUT":
        logging.info("update content start,contentId is %d", contentId)
        req = request.PUT
        try:
            # 数据有效性验证
            content = Contents.objects.filter(id=contentId).first()
            if not content:
                code = -30
                return set_response(code, message, {})
            else:
                pass
            # 表单验证
            contentForm = ContentsForm(req)
            if contentForm.is_valid():
                logging.info("add content start")
                content = ContentsForm(req, instance=content)
                result = content.save()
                logging.info("add content success ,id is %d", result.id)
                pass
            else:
                message = contentForm.errors
                code = -10
        except Exception as e:
            logging.error(e)
            code = -10000
            pass
        finally:
            return set_response(code, message, {})
        pass
    elif request.method == "GET":
        logging.info("update content start,contentId is %d", contentId)
        content = {}
        try:
            content = Contents.objects.filter(id=contentId).first()
            if content:
                content = content.to_dire()
        except Exception as e:
            logging.error(e)
            code = -10000
            pass
        finally:
            return set_response(code, message, content)
        pass
    else:
        return

# # 查询分单统计用户
# @csrf_exempt
# def getProductUserList(request):
#     if  request.method == "GET":
#         code = 0
#         req = request.GET
#         page = int(req.get('page', 1))
#         size = int(req.get('size', 10))
#         start = (page - 1) * size
#         end = start + size
#         total = 0
#         userList = []
#         message = None
#         try:
#             kwargs = DynamicQuery(request,[])
#             startTime = req.get("startTime", None)
#             endTime = req.get("endTime", None)
#             if startTime:
#                 kwargs.__delitem__('startTime')
#                 kwargs.__setitem__("createAt__gte", startTime)
#             if endTime:
#                 kwargs.__delitem__('endTime')
#                 kwargs.__setitem__("createAt__lte", endTime)
#             result = Product_User_Relation.objects.filter(**kwargs).values_list('userId',flat=True)
#             total = result.count()
#             logging.info('result size is %d ', total)
#             result = list(result)
#             logging.info("result is %s",result)
#             userList = User.objects.filter(id__in=result)
#             for user in userList:
#                 user.mobile = strEncrypted(user.mobile,3,7)
#             userList = list(userList[start:end])
#             pass
#         except Exception as e:
#             logging.error(e)
#             code = -10000
#             pass
#         finally:
#
#             return set_list_response(code,message,userList,page,size,total)
#         pass
#     else:
#         return
