import json
import logging
import traceback

from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response, DynamicQuery
from loan.models import Medium, Medium_Statistics
from loan.util import getTimeStamp
from loan.views.admin.adminForm import MediumForm

logging = logging.getLogger('medium')


# 媒介列表
def getMediumList(request):
    if request.method == "GET":
        logging.info('API is /admin/u/medium/list ,get mediumList begin :')
        code = 0
        if request.method == 'GET':
            mediumList = []
            req = request.GET
            page = int(req.get('page', 1))
            size = int(req.get('size', 10))
            start = (page - 1) * size
            end = start + size
            total = 0
            try:
                fields = [f.name for f in Medium._meta.fields]
                kwargs = DynamicQuery(request, ['name'], *fields)
                logging.info('kwargs is %s , page is %d ,size is %d', kwargs, page, size)
                mediumList = Medium.objects.filter(**kwargs).order_by('sort', '-createAt')
                total = mediumList.count()
                logging.info("total is %d", total)
                mediumList = list(mediumList[start:end])
            except Exception as e:
                logging.error(e)
                code = -10000
            finally:
                return set_list_response(code, None, mediumList, page, size, total)
    else:
        return


# 媒介编辑
@csrf_exempt
def updateMedium(request, mediumId):
    logging.info('API is /admin/u/medium/{id} ,update medium begin :')
    code = 0
    message = None
    if request.method == 'POST':
        req = request.POST
        try:
            medium = Medium.objects.filter(id=mediumId)
            if not medium.exists():
                code = -30
                return set_response(code, None, {})
            else:
                medium = medium.first()
                medium.updateAt = getTimeStamp()
                pass
            obj = MediumForm(req)
            if not obj.is_valid():
                code = -10
                message = obj.errors
            else:
                name = req.get('name')
                # 检查是否有重名元素
                checkNameMedium = Medium.objects.filter(name=name)
                if checkNameMedium.exists() and checkNameMedium.first().id != mediumId:
                    code = -1041
                    return set_response(code, None, {})
                else:
                    medium = MediumForm(req, instance=medium)
                    medium.save()
                    logging.info('update medium success')
        except Exception as e:
            code = -10000
            logging.error(e)
        finally:
            return set_response(code, message, mediumId)
    else:
        return


# 媒介新增
@csrf_exempt
def insertMedium(request):
    if request.method == 'POST':
        logging.info('API is /admin/u/medium ,insert medium begin :')
        code = 0
        message = None
        req = request.POST
        mediumId = None
        try:
            obj = MediumForm(req)
            if not obj.is_valid():
                code = -10
                message = obj.errors
                return set_response(code, message, mediumId)
            else:
                pass

            # 检查是否有重名元素
            name = req.get('name')
            logging.info("name is %s", name)
            checkNameMedium = Medium.objects.filter(name=name)
            if checkNameMedium.exists():
                code = -1041
                return set_response(code, None, {})
            else:
                pass
            medium = Medium(name=name, createAt=getTimeStamp(), updateAt=getTimeStamp())
            medium.save()
            logging.info('create success')
            mediumId = medium.id
            medium.type = mediumId
            medium.save()
            logging.info('medium id is %s', mediumId)

        except Exception as e:
            code = -10000
            logging.error(e)
        finally:
            return set_response(code, message, mediumId)
    else:
        return


# 媒介上下架
@csrf_exempt
def updateMediumStatus(request, mediumId, status):
    logging.info('API is /admin/u/medium/{mediumId}/{status} ,update medium status  begin :')
    code = 0
    message = None
    if request.method == 'POST':
        try:
            # result 返回的是受影响的记录条数
            result = Medium.objects.filter(id=mediumId).update(status=status,updateAt=getTimeStamp())
            logging.info('result is : ' + str(result))
            if result == 1:
                pass
            else:
                code = -1050
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, message, mediumId)
    else:
        return


# 媒介名称验证
def checkMediumName(request):
    logging.info('API is /admin/u/medium/name ,check medium name  begin :')
    if request.method == 'GET':
        code = 0
        try:
            # 检查是否有重名元素
            checkNameMedium = Medium.objects.filter(name=request.GET.get('name'))
            if checkNameMedium.exists():
                code = -1050
                return set_response(code, None, {})
            else:
                pass
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, None, {})
    else:
        return


# 媒介统计
@csrf_exempt
def mediumStatistics(request):
    logging.info('get medium statistics  begin :')
    code = 0
    req = request.GET
    page = int(req.get('page', 1))
    size = int(req.get('size', 10))
    start = (page - 1) * size
    end = start + size
    total = 0
    mediumStatisticsList = []
    message = None
    newTotal = 0
    oldTotal = 0
    newUserIds = []
    oldUserIds = []
    if request.method == 'GET':
        try:
            fields = [f.name for f in Medium_Statistics._meta.fields]
            kwargs = DynamicQuery(request, [], *fields)
            startTime = req.get("startTime", None)
            endTime = req.get("endTime", None)
            if startTime:
                kwargs.__setitem__("createAt__gte", startTime)
            if endTime:
                kwargs.__setitem__("createAt__lte", endTime)
            result = Medium_Statistics.objects.filter(**kwargs).order_by('-createAt')
            total = result.count()
            logging.info('result size is %d ', total)

            # 统计人数
            for statistics in result:
                newUserIds += json.loads(statistics.newIds)
                oldUserIds += json.loads(statistics.oldIds)
            logging.info("new user ids is %s",newUserIds)
            logging.info("old user ids is %s",oldUserIds)
            # 新旧用户去重复处理
            # 新用户数量为 新用户数组中排除掉老用户数组中的id
            newUserIds = set(newUserIds).difference(set(oldUserIds))
            newTotal = len(newUserIds)
            # 老用户数量为旧用户数组去重
            oldUserIds = set(oldUserIds)
            oldTotal = len(oldUserIds)
            mediumStatisticsList = list(result[start:end])
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
        finally:
            sup = {
                'newTotal': newTotal,
                'newIds': list(newUserIds),
                'oldTotal': oldTotal,
                'oldIds': list(oldUserIds)
            }
            return set_list_response(code, message, mediumStatisticsList, page, size, total, **sup)
    else:
        return
