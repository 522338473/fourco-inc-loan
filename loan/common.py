import decimal
import json
import logging
import random
import traceback

from xml.etree import ElementTree

from django.core import serializers
from django.db.models import Model
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import render

from loan.constant import constant
from loan.util import res, resList

logging = logging.getLogger("django")


def page_not_found(request):
    return render(request, '404.html')


def page_error(request):
    return render(request, '404.html')


def permission_denied(request):
    return render(request, '404.html')


def set_response(code, message, o):
    resp = res(0, message, {})
    try:
        if not code:
            code = 0

        if not message:
            message = constant.code.get(code)

        if not o:
            o = {}
        resp = res(code, message, o)
    except Exception as e:
        logging.error(e)

    finally:
        return HttpResponse(resp, content_type="application/json")


def set_list_response(code, message, o, page, size, total, **kwargs):
    try:

        if not code:
            code = 0

        if not message:
            message = constant.code.get(code)

        if not o:
            o = []
        resp = resList(code, message, o, page, size, total, **kwargs)

        return HttpResponse(resp, content_type="application/json")
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        pass


def getRequestUid(request):
    cookie = request.COOKIES.get('user', None)
    if cookie:
        logging.info("request uid is " + cookie.split("|")[0])
        return cookie.split("|")[0]
    else:
        logging.warn("this request uid is not found")


# 处理动态查询字段
# containsParams 中包含的是模糊搜索的字段
# 可选参数field 传入model field值，不存在的搜索条件将被过滤
def DynamicQuery(request, containsParams: list, *field, **other):
    kwargs = {}
    req = request.GET or request.POST
    keys = req.keys()
    for key in keys:
        if field and not field.__contains__(key):
            continue
        elif req.get(key):
            if containsParams.__contains__(key):
                nk = key + '__contains'
            else:
                nk = key
                pass
            kwargs[nk] = req.get(key)
        else:
            pass
    return kwargs


def getRandomNumber(n):
    num = ''

    for i in range(0, n):
        num += (random.randint(0, 9).__str__())
    return num


def getXmlEle(xml):
    return ElementTree.fromstring(xml)


# form表单转换model
def formToModel(o: Model, f: Form):
    fv = f.cleaned_data
    for key in fv.keys():
        o.__setattr__(key, fv.get(key))
    return o


# serializers化
def serializersConvert(data):
    return serializers.serialize('json', data)


def strEncrypted(s: str, start: int, end: int):
    s1 = s[0:start]
    s2 = s[end:]
    ns = ''
    for i in range(end - start):
        ns += '*'
    return s1 + ns + s2
