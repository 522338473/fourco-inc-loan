import json
import logging
import traceback

from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, QueryDict, HttpRequest
from django.shortcuts import HttpResponseRedirect

from loan.common import set_response
from loan.constant import constant
from loan.models import User, Manager, Role

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


# 拦截器
class SimpleMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request: HttpRequest):
        logging.info("request url is " + request.__str__())

        try:
            if request.path.__contains__('admin'):
                # TODO后台拦截
                if not request.path.__contains__('/u/'):
                    pass
                else:
                    cookie = request.COOKIES.get('manager', None)
                    '''
                    这里获取COOKIE应该用COOKIES 而不是COOKIE
                    通过cookie里获取的信息进行校验，如果不通过则返回未登录
                    '''
                    if cookie:
                        uid = cookie.split("|")[0]
                        name = cookie.split("|")[1]
                        manager = Manager.objects.filter(id=uid).first()
                        if check_password(manager.name, name):
                            logging.info("Successful verification")
                            request.__setattr__('manager', json.dumps(manager.to_dire()))
                            # 根据角色信息控制读写权限
                            if request.method != 'GET' and not request.path.__contains__('/u/logout'):
                                role = Role.objects.filter(id=manager.role).first()
                                if not role:
                                    code = -30
                                    return set_response(code,None,{})
                                else:
                                    permissions = role.permissions
                                    logging.info("this role name is %s", role.name)
                                    logging.info("this role permissions is %s", role.permissions)
                                    if permissions != 'rw':
                                        code = -50
                                        return set_response(code,None,{})

                            pass
                        else:
                            return set_response(-20, None, {})
                    else:
                        return set_response(-20, None, {})
                    pass
            else:
                # 前台拦截带u接口
                if not request.path.__contains__('/u/'):
                    pass
                else:
                    cookie = request.COOKIES.get('user', None)
                    '''
                    这里获取COOKIE应该用COOKIES 而不是COOKIE
                    通过cookie里获取的信息进行校验，如果不通过则返回未登录
                    '''

                    if cookie:
                        logging.info("cookie is %s", cookie)
                        uid = cookie.split("|")[0]
                        user = User.objects.filter(id=uid).first()
                        logging.info("uid is " + uid + " ,mobile is " + user.mobile.__str__() + " ,cookie is " + cookie)
                        if checkToken(uid, user.mobile, cookie):
                            logging.info("Successful verification")
                            request.__setattr__('user', json.dumps(user.to_dire()))
                            pass
                        else:
                            return set_response(-20, None, {})
                    else:
                        return set_response(-20, None, {})
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
        finally:
            # 处理其他请求
            http_method = request.META['REQUEST_METHOD']
            logging.info("method is %s", http_method.upper())
            if http_method.upper() not in ('GET', 'POST'):
                setattr(request, http_method.upper(), QueryDict(request.body))
            pass

    @staticmethod
    def process_response(request, response):
        if response.status_code != 200:
            return HttpResponse('error code:' + response.status_code.__str__())
        else:
            return response


def checkToken(uid, mobile, cookie):
    token = cookie.split("|")[1]
    s = {
        'id': uid,
        'mobile': mobile,
        'key': constant.key
    }
    if check_password(s, token):
        return uid
    else:
        return False
