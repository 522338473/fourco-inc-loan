# 返回json数据

from django.contrib.auth.hashers import make_password, check_password

from loan.constant import *
from loan.models import User


def setToken(uid, mobile):
    s = {
        'id': uid,
        'mobile': mobile,
        'key': constant.key
    }
    return uid + '|' + make_password(s)


def checkToken(uid, mobile, token):
    token = token.split("|")[1]
    s = {
        'id': uid,
        'mobile': mobile,
        'key': constant.key
    }
    if check_password(s, token):
        return uid
    else:
        return False


def checkIdentity(request):
    cookie = request.COOKIES.get('user', None)
    uid = cookie.split("|")[0]
    token = cookie.split("|")[1]
    user = User.objects.filter(id=uid).first()
    if checkToken(uid, user.mobile.__str__(), token):
        request.GET['user'] = user
        return request
    else:
        return False
