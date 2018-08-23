import decimal
import json

# 返回json数据
import logging
import time

import requests

from loan.constant import constant

logging = logging.getLogger("django")


def res(code: object, message: object, o: object) -> object:
    r = {
        'code': code,
        'message': message,
        'data': o
    }
    return json.dumps(r, cls=DecimalEncoder)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def resList(code: object, message: object, o: list, page: object, size: object, total: object, **kwargs) -> object:
    for a in range(len(o)):
        o[a] = o[a].to_dire()
    r = {
        'code': code,
        'message': message,
        'page': page,
        'size': size,
        'total': total,
        'data': o
    }
    for k, v in kwargs.items():
        r[k] = v

    return json.dumps(r, cls=DecimalEncoder)


def getTimeStamp():
    return int(round(time.time() * 1000))

def timeStampToDate(timeStamp:int):
    x = time.localtime(timeStamp/1000)
    return time.strftime('%Y-%m-%d %H:%M:%S',x)
def timeStampFormatDate(timeStamp:int,str):
    x = time.localtime(timeStamp/1000)
    return time.strftime(str,x)

def getTodayZeroTime():
    t = time.localtime(time.time())
    time1 = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t), '%Y-%m-%d %H:%M:%S'))
    return int(time1) * 1000



def sendSms(mobile, msg):
    params = {
        'un': constant.smsAccout,
        'pwd': constant.smsPwd,
        'mobile': mobile,
        'msg': msg
    }
    return requests.get(constant.smsUrl, params=params)

