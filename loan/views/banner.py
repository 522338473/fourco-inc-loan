import logging

from loan.common import set_response, DynamicQuery, set_list_response
from loan.models import Banner

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
            bannerList = Banner.objects.filter(**kwargs, status=1).order_by("-updateAt")
            total = bannerList.count()
            bannerList = list(bannerList[start:end])
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_list_response(code, None, bannerList, page, size, total)
    else:
        return


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
