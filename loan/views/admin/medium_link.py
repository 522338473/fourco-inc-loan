import logging
import traceback
from urllib.parse import unquote

from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response, DynamicQuery
from loan.constant import HOME_HOST, PARAMS, TEST_MODEL, HOME_HOST_ONLINE
from loan.models import MediumLink, Medium
from loan.util import getTimeStamp


logging = logging.getLogger("link")


# 媒体链接列表
def getMediumLinkList(request, mediumId):
    logging.info('API is /admin/u/medium/list ,get mediumList begin :')
    code = 0
    mediumLinkList = []
    total = 0

    if request.method == 'GET':
        req =request.GET
        try:
            # fields = [f.name for f in MediumLink._meta.fields]
            # kwargs = DynamicQuery(request, ['link'], *fields)
            kwargs = {}
            link = req.get("link",None)
            logging.info("link is %s", link)
            if link:
                kwargs = {"link__contains": unquote(link)}
            logging.info("kwargs is %s", kwargs)
            mediumLinkList = MediumLink.objects.filter(**kwargs, mediumId=mediumId)
            total = mediumLinkList.count()
            logging.info("link count is  %d", total)
            mediumLinkList = list(mediumLinkList)
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_list_response(code, None, mediumLinkList, 1, 10000, total)
    else:
        return


# 媒体链接新增
@csrf_exempt
def insertMediumLink(request):
    logging.info('API is /admin/u/link ,insert medium_link begin :')
    code = 0
    linkId = 0
    if request.method == 'POST':
        try:
            req = request.POST
            mediumId = req.get('mediumId')
            logging.info("mediumId is %s", mediumId)
            # 皮肤
            template = req.get('template', '01')
            # 前端路由url
            login = ""
            if not template:
                template = '1'
                pass
            else:
                login = template
                pass
            # 取媒介
            medium = Medium.objects.filter(id=mediumId).first()
            if not medium:
                code = -30
                return set_response(code, None, {})
            else:
                pass
            url = HOME_HOST_ONLINE + login + PARAMS
            if TEST_MODEL:
                url = HOME_HOST + login + PARAMS
            newLink = MediumLink(createAt=getTimeStamp(),updateAt=getTimeStamp(),mediumId=mediumId,type=mediumId, link=url)
            newLink.save()
            linkId = newLink.id
            logging.info("create a new link ,medium id is %s , link id is  %s", mediumId, linkId)

            # 链接生成
            if TEST_MODEL:
                url = HOME_HOST + login + PARAMS.replace('{source}', mediumId).replace('{sub}', str(linkId)).replace(
                    '{template}', template)
            else:
                url = HOME_HOST_ONLINE + login + PARAMS.replace('{source}', mediumId).replace('{sub}', str(linkId)).replace(
                    '{template}', template)

            logging.info(url)
            MediumLink.objects.filter(id=linkId).update(link=url)
            if newLink:
                # 更新媒介数量
                logging.info('update medium link count: %d --> %d:', medium.linkCount, medium.linkCount + 1)
                medium.linkCount = medium.linkCount + 1
                medium.save()


        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
        finally:
            return set_response(code, None, linkId)
    else:
        return


# 媒体链接删除
@csrf_exempt
def deleteMediumLink(request, mediumLinkId):
    logging.info('API is /admin/u/link/{id} ,delete medium_link begin :')
    code = 0
    if request.method == 'DELETE':
        try:
            logging.info('delete link start,id is %d', mediumLinkId)
            mediumLink = MediumLink.objects.filter(id=mediumLinkId)
            if not mediumLink.exists():
                code = -30
                return set_response(code, None, {})
            else:
                medium = Medium.objects.filter(id=mediumLink.first().mediumId).first()
                logging.info('medium link count :%d --> %d', medium.linkCount, medium.linkCount - 1)
                medium.linkCount = medium.linkCount - 1
                mediumLink.delete()
                # 更新媒介链接数量
                medium.save()
                logging.info('delete link end')
        except Exception as e:
            logging.error(e)
            code = -10000
        finally:
            return set_response(code, None, mediumLinkId)
    else:
        return
