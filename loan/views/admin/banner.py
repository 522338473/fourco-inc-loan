import logging

from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response, DynamicQuery
from loan.models import Banner
from loan.util import getTimeStamp
from loan.views.admin.adminForm import BannerForm



logging = logging.getLogger('banner')


# banner列表
def getBannerList(request):
    if request.method == 'GET':
        logging.info("get banner list start")
        code = 0
        bannerList = []
        req = request.GET
        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        start = (page - 1) * size
        end = start + size
        total = 0
        try:
            fields = [f.name for f in Banner._meta.fields]
            kwargs = DynamicQuery(request, [], *fields)
            logging.info('kwargs is %s , page is %d ,size is %d', kwargs, page, size)
            bannerList = Banner.objects.filter(**kwargs).order_by('-status','-updateAt')
            total = bannerList.count()
            bannerList = list(bannerList[start:end])
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_list_response(code, None, bannerList, page, size, total)
    else:
        return


# #新增banner
@csrf_exempt
def insertBanner(request):
    logging.info("create banner start")

    if request.method == 'POST':
        message = None
        code = 0
        bid = 0
        req = request.POST
        try:
            banner = Banner(createAt=getTimeStamp(), updateAt=getTimeStamp())
            bannerForm = BannerForm(req)
            if not bannerForm.is_valid():
                code = -10
                message = bannerForm.errors
            else:
                banner = BannerForm(req, instance=banner)
                result = banner.save()
                bid = result.id
                logging.info("banner create success ,id is %d", bid)
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, message, bid)
    else:
        return


# 修改删除 banner
@csrf_exempt
def editBanner(request, bannerId):
    code = 0
    message = None
    try:
        # 数据有效性验证
        banner = Banner.objects.filter(id=bannerId)
        if not banner.exists():
            code = -30
            return set_response(code, None, {})
        else:
            banner = banner.first()
            pass
        # 修改
        if request.method == 'POST' or request.method == 'PUT':
            req = request.POST
            logging.info("update banner start, id is %d", bannerId)
            banner.updateAt = getTimeStamp()
            bannerForm = BannerForm(req, instance=banner)
            if not bannerForm.is_valid():
                code = -10
                message = bannerForm.errors
            else:
                bannerForm.save()
                logging.info('update banner end')
                banner.url = request.POST.get('url')
        # 删除
        elif request.method == 'DELETE':
            logging.info("delete banner start,id is %d", bannerId)
            banner.delete()
            logging.info("delete end")
        else:
            return
    except Exception as e:
        logging.error(e)
        code = -10000
    finally:
        return set_response(code, message, bannerId)


# banner详情
def getBannerDetail(request, bannerId):
    if request.method == 'GET':
        code = 0
        banner = {}
        try:
            logging.info("get banner detail start ,id is %d", bannerId)
            banner = Banner.objects.filter(id=bannerId).first()
            if banner:
                banner = banner.to_dire()
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, None, banner)
    else:
        return


# banner上下架
@csrf_exempt
def updateBannerStatus(request, bannerId, status):
    message = None
    code = 0
    logging.info("update bannerId start")
    logging.info("productId is %s status is %s", bannerId, status)

    if request.method == 'POST':
        try:
            # 校验数据是否存在
            banner = Banner.objects.get(id=bannerId)
            if not banner:
                code = -30
                return set_response(code, message, {})

            banner.updateAt = getTimeStamp()
            banner.status = status
            banner.save()
            logging.info('update product status success')
        except Exception as e:
            code = -10000
            logging.error(e)
        finally:
            return set_response(code, message, bannerId)
    else:
        return
