# Create your views here.
import json
import logging
import traceback

import xlwt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from loan.common import DynamicQuery, set_list_response, strEncrypted
from loan.models import User, Product_User_Relation, Medium, MediumLink, Medium_Statistics, Record
from loan.util import DecimalEncoder, timeStampToDate

logging = logging.getLogger("user")


# 用户列表
@csrf_exempt
def getUserList(request):
    logging.info("get user list start")
    logging.info("method -%s", request.method)
    if request.method == "GET" or request.method == "POST":
        code = 0
        req = request.GET or request.POST
        page = int(req.get("page", 1))
        size = int(req.get("size", 10))
        total = 0
        ids = req.getlist('ids', [])
        # 处理搜索入参
        try:
            fields = [field.name for field in User._meta.fields]
            kwargs = DynamicQuery(request, ['mobile'], *fields)
            # 注册时间
            registerStart = req.get("registerStart", None)
            registerEnd = req.get("registerEnd", None)
            userType = req.get("userType", None)
            logging.info("userType is %s", userType)
            doneStart = req.get("doneStart", None)
            doneEnd = req.get("doneEnd", None)
            productId = req.get("productId", None)
            logging.info("productId is %s", productId)
            # 搜新注册用户
            linkParams = {}
            if registerStart:
                kwargs.__setitem__("createAt__gte", registerStart)
                linkParams.__setitem__("createAt__gte", registerStart)
            if registerEnd:
                kwargs.__setitem__("createAt__lte", registerEnd)
                linkParams.__setitem__("createAt__lte", registerEnd)
            # 搜索某段时间内注册的1新用户2旧用户3总用户 4推荐统计用户
            if userType == '1':
                linkParams.__setitem__("linkId", req.get("linkId"))
                logging.info("search new user by %s", linkParams)
                medium_Statistics = Medium_Statistics.objects.filter(**linkParams).first()
                if medium_Statistics:
                    newIds = json.loads(medium_Statistics.newIds)
                    ids = ids + newIds
                    kwargs.__setitem__("id__in", newIds)
                    pass
                pass
            # 搜索所有用户，直接用统计里取两者之和返回
            elif userType == '3':
                allParams = {}
                allStart = req.get("allStart", None)
                allEnd = req.get("allStart", None)
                if allStart:
                    allParams.__setitem__("createAt__gte", allStart)
                if doneEnd:
                    allParams.__setitem__("createAt__lte", allEnd)
                allParams.__setitem__("linkId", req.get("linkId"))
                logging.info("search old user by %s", allParams)
                medium_Statistics = Medium_Statistics.objects.filter(**allParams).first()
                if medium_Statistics:
                    newIds = json.loads(medium_Statistics.newIds)
                    oldIds = json.loads(medium_Statistics.oldIds)
                    allIds = newIds + oldIds
                    ids = ids + allIds
                    kwargs.__setitem__("id__in", ids)
                    pass
                pass
            # 搜索推荐统计的用户,timeStart/end查询主体为推荐客户访问记录表，查出相关的ids列表
            elif userType == '4':
                recommendParams = {}
                statisticsStart = req.get("statisticsStart", None)
                statisticsEnd = req.get("statisticsEnd", None)
                if statisticsStart:
                    recommendParams.__setitem__("createAt__gte", statisticsStart)
                if statisticsEnd:
                    recommendParams.__setitem__("createAt__lte", statisticsEnd)
                recommendId = req.get("recommendId", None)
                linkId = req.get("linkId", None)
                recommendParams.__setitem__("productId", recommendId)
                recommendParams.__setitem__("linkId", linkId)
                logging.info("recommendParams is %s", recommendParams)
                record = Record.objects.filter(**recommendParams).values_list("userId", flat=True)
                logging.info("record is %s", list(record))
                kwargs.__setitem__('id__in', list(record))
                kwargs.__delitem__('linkId')
                pass

            # 搜填单老用户
            if doneStart:
                kwargs.__setitem__("doneAt__gte", doneStart)
            if doneEnd:
                kwargs.__setitem__("doneAt__lte", doneEnd)

            # 用户分单归属
            if productId:
                p_kwargs = {
                    'productId': productId,
                }
                startTime = req.get('startTime', None)
                endTime = req.get('endTime', None)
                if startTime:
                    p_kwargs.__setitem__("createAt__gte", startTime)
                if endTime:
                    p_kwargs.__setitem__("createAt__lte", endTime)
                logging.info("p_kwargs is %s ", p_kwargs)
                p_uid = Product_User_Relation.objects.filter(**p_kwargs).values_list('userId', flat=True)
                ids = ids + list(p_uid)
                kwargs.__setitem__('id__in', ids)
            else:
                pass

            ids = list(set(ids))
            logging.info("ids is %s", ids)
            if len(ids) > 0:
                kwargs.__setitem__('id__in', ids)

            logging.info("kwargs is %s", kwargs)
            userList = User.objects.filter(**kwargs).order_by("-createAt")
            # 所有媒介相关ids
            mediumIds = userList.values_list('source', flat=True)
            # 导出list参数
            outputList = userList
            userIds = list(userList.values_list('id', flat=True))[(page - 1) * size:(page - 1) * size + size]
            logging.info("user ids is %s", userIds)
            total = userList.count()
            userList = userList[(page - 1) * size:(page - 1) * size + size]
            # 取媒介信息
            returnMediumIds = list(userList.values_list('source', flat=True))
            logging.info("return ids is %s", returnMediumIds)
            # 在列表中返回给前端的数据
            returnMediumList = Medium.objects.filter(id__in=returnMediumIds)
            logging.info("return medium list size is %s", returnMediumList.count())
            returnMediumList = list(medium.to_dire() for medium in returnMediumList)

            for user in userList:
                user.mobile = strEncrypted(user.mobile, 3, 7)

            userList = list(user.to_dire() for user in userList)
            logging.info("user list size is %d", len(userList))

            # 查分单信息
            relations = Product_User_Relation.objects.filter(userId__in=userIds)
            logging.info("relations size is %d", relations.count())
            # 拼接用户归属信息
            productInfo = {}
            for relation in relations:
                if productInfo.get(relation.userId):
                    productInfo[relation.userId].append(relation.productName)
                    productInfo[relation.userId] = list(set(productInfo[relation.userId]))
                    pass
                else:
                    productInfo[relation.userId] = [relation.productName]
            obj = {
                'userList': userList,
                'productInfo': productInfo,
                'mediumList': returnMediumList
            }

            from loan.constant import constant
            r = {
                'code': code,
                'message': constant.code[code],
                'page': page,
                'size': size,
                'total': total,
                'data': obj
            }
            obj = json.dumps(r, cls=DecimalEncoder)

            # 导出操作
            if req.get('output') == '1':
                mediumList = Medium.objects.filter(id__in=mediumIds)
                mediumDirt = dict((medium.id, medium) for medium in mediumList)
                logging.info("mediumDirt is %s", mediumDirt)
                # 指定返回为excel文件
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment;filename=users.xls'
                # 创建工作簿
                workbook = xlwt.Workbook(encoding='utf-8')
                # 创建工作页
                sheet = workbook.add_sheet("sheet1")
                row0 = [u'id', u'姓名', u'电话', u'房产', u'汽车', u'信用卡',
                        u'寿单', u'年保费', u'居住时间', u'职业',
                        u'注册时间', u'媒介来源', u'媒介链接', u'客户归属'
                        ]
                for i in range(0, len(row0)):
                    sheet.write(0, i, row0[i])
                num = 1

                for d in outputList.values():
                    sheet.write(num, 0, d['id'])
                    sheet.write(num, 1, d['nick'])
                    sheet.write(num, 2, strEncrypted(d['mobile'], 3, 7))
                    sheet.write(num, 3, constant.userContent.get('estate').get(d['estate']))
                    sheet.write(num, 4, constant.userContent.get('car').get(d['car']))
                    sheet.write(num, 5, constant.userContent.get('card').get(d['card']))
                    sheet.write(num, 6, constant.userContent.get('lifeInsurance').get(d['lifeInsurance']))
                    sheet.write(num, 7, constant.userContent.get('feeInsurance').get(d['feeInsurance']))
                    sheet.write(num, 8, constant.userContent.get('livingTime').get(d['livingTime']))
                    sheet.write(num, 9, constant.userContent.get('profession').get(d['profession']))
                    sheet.write(num, 10, timeStampToDate(d['createAt']))
                    if mediumDirt.get(d['source']):
                        sheet.write(num, 11, mediumDirt.get(d['source']).name)
                        pass
                    else:
                        pass
                    sheet.write(num, 12, d['sourceLink'])
                    if productInfo.get(d['id'], None):
                        sheet.write(num, 13, ",".join(iter(productInfo.get(d['id'], None))))
                        pass

                    num = num + 1
                workbook.save(response)
                return response
            pass
            return HttpResponse(obj, content_type="application/json")
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            return set_list_response(code, None, {}, page, size, total)
        finally:
            pass
    else:
        return
