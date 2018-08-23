# Create your views here.
import logging
import os

from django import forms
from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response
from loan.models import Img



logging = logging.getLogger("common")


# 登录参数校验
class LoginForm(forms.Form):
    name = forms.CharField(required=True, error_messages={'required': '手机号不能为空'})
    pwd = forms.CharField(required=True, error_messages={'required': '验证码不能为空'})


# 图片上传
@csrf_exempt
def uploadFile(request):
    logging.info("get user list start")
    host = request.get_host()
    logging.info("server host is %s", request.get_host())

    img = ''
    if request.method == "POST":
        if 'image' in request.FILES:
            image = request.FILES['image']
            img = Img(image=image)
            type_list = ['.jpg', '.png', '.gif', '.webp', 'jpeg']
            if os.path.splitext(image.name)[1].lower() in type_list:
                logging.info("update start")
                img.save()
                logging.info("im " + img.image.__str__())
                logging.info("update end")
    else:
        return

    return set_response(0, None, {'url': '//' + host + '/' + img.image.__str__()})
