# Create your views here.
import json
import logging
import traceback

from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response, DynamicQuery
from loan.models import Manager, Role
from loan.util import getTimeStamp

logging = logging.getLogger("login")


# 登录参数校验
class LoginForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})
    pwd = forms.CharField(required=True, error_messages={'required': '密码不能为空'})

    class Meta:
        model = Manager
        exclude = ['createAt', 'updateAt', 'role', 'permission','createBy','updateBy']


# 新增参数校验
class CreateForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': '用户名不能为空'})
    pwd = forms.CharField(required=True, error_messages={'required': '密码不能为空'})
    role = forms.IntegerField(required=True, error_messages={'required': '角色不能为空'})

    class Meta:
        model = Manager
        exclude = ['createAt', 'updateAt', 'permission','createBy','updateBy']


# 登录
@csrf_exempt
def login(request):
    if request.method == "POST":
        code = 0
        message = None
        try:

            obj = LoginForm(request.POST)
            if obj.is_valid():
                manager = Manager.objects.filter(name=request.POST.get('name')).first()
                if manager:
                    if check_password(request.POST.get('pwd'), manager.pwd):
                        logging.info("login success")
                        manager.pwd = ''
                        response = HttpResponse(set_response(code, None, manager.to_dire()),
                                                content_type='application/json')
                        response.set_cookie('manager',
                                            manager.id.__str__() + "|" + make_password(manager.name),
                                            max_age=24 * 60 * 60)
                        return response
                    else:
                        code = -2
                else:

                    code = -2
            else:
                code = -1
                message = obj.errors
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000


    else:
        return
    return set_response(code, message, {})


# 注销
@csrf_exempt
def logout(request):
    logging.info("logout start")
    if request.method == "POST":
        code = 0
        response = HttpResponse(set_response(code, None, {}), content_type='application/json')
        response.delete_cookie('manager')
        return response
    else:
        return


# 新增账号
@csrf_exempt
def createManager(request):
    code = -1
    message = None
    if request.method == "POST":
        req = request.POST
        try:
            currentManager = json.loads(request.__getattribute__('manager'))
            manager = Manager(createAt=getTimeStamp(), updateAt=getTimeStamp(),createBy=currentManager.get('name'),updateBy=currentManager.get('name'))
            obj = CreateForm(request.POST, instance=manager)
            if obj.is_valid():
                pwd = req.get('pwd', None)
                name = req.get('name')
                # 名字检查
                oManager = Manager.objects.filter(name=name).first()
                if oManager:
                    code = -40
                    return set_response(code, message, {})

                # 检查角色是否存在
                role = Role.objects.filter(id=req.get('role', 0)).first()
                if not role:
                    code = -30
                    return set_response(code, message, {})
                logging.info("pwd id %s", pwd)
                manager.pwd = make_password(pwd)

                manager.save()
                logging.info("create manager success ")
                code = 0
                pass
            else:
                message = obj.errors
            return set_response(code, message, {})
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            return set_response(code, None, {})
    else:
        return


# 修改密码
@csrf_exempt
def updateManagerPassword(request, managerId):
    message = None
    if request.method == "POST":
        req = request.POST
        logging.info("update manager password start")
        try:
            currentManager = json.loads(request.__getattribute__('manager'))
            if currentManager.get('id') == managerId or currentManager.get('role') == 1:
                pass
            else:
                code = -50
                return set_response(code, message, {})
            manager = Manager.objects.filter(id=managerId).first()
            if not manager:
                code = -30
                return set_response(code, message, {})
            else:
                pass
            password = req.get('pwd', None)
            newPassword = req.get('newPassword', None)
            if not password or not newPassword:
                logging.info("params error")
                code = -10
                return set_response(code, message, {})
            if check_password(password, manager.pwd):
                logging.info("new password is %s", password)
                manager.pwd = make_password(newPassword)
                manager.save()
                logging.info("update manager password success ")
                code = 0
                pass
            else:
                logging.info("paw error")
                code = -2
            return set_response(code, message, {})
        except Exception as e:
            logging.info(e)
            traceback.print_exc()
            code = -10000
            return set_response(code, None, {})
    else:
        return


# 查看修改删除账户
@csrf_exempt
def getOrUpdateManager(request, managerId):
    message = None
    if request.method == "PUT":
        req = request.PUT
        logging.info("update manager start")
        try:
            currentManager = json.loads(request.__getattribute__('manager'))
            if currentManager.get('id') == managerId or currentManager.get('role') == 1:
                pass
            else:
                code = -50
                return set_response(code, message, {})
            manager = Manager.objects.filter(id=managerId).first()
            if not manager:
                code = -30
                return set_response(code, message, {})
            else:
                pass
            password = req.get('pwd', None)
            if password:
                logging.info("change pwd")
                manager.pwd = make_password(password)
                pass
            else:
                pass

            # 检查角色是否存在
            role = Role.objects.filter(id=req.get('role', 0)).first()
            logging.info("role id is %s", req.get('role', 0))
            if not role:
                code = -30
                return set_response(code, message, {})
            else:
                manager.role = role.id

            manager.updateAt = getTimeStamp()
            manager.updateBy = currentManager.get('name')
            manager.save()
            logging.info("update manager password success ")
            code = 0
            pass

            return set_response(code, message, {})
        except Exception as e:
            logging.info(e)
            traceback.print_exc()
            code = -10000
            return set_response(code, None, {})
    elif request.method == 'GET':
        req = request.GET
        code = 0
        message = None
        manager = {}
        logging.info("manager id is %d", managerId)
        try:
            manager = Manager.objects.filter(id=managerId).first()
            if manager:
                manager.pwd = ''
                manager = manager.to_dire()
                pass
            else:
                logging.info("manager is not found")
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, manager)
    elif request.method == 'DELETE':
        code = 0
        message = None
        manager = {}
        logging.info("delete manager id is %d", managerId)
        try:
            manager = Manager.objects.filter(id=managerId).first()
            if manager:
                manager.delete()
                pass
            else:
                logging.info("manager is not found")
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, manager)
    else:
        return



# 获取账号列表
@csrf_exempt
def getManagerList(request):
    if request.method == 'GET':
        req = request.GET
        code = 0
        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        total = 0
        start = (page - 1) * size
        end = start + size
        logging.info("start is %s,end is %s", start, end)
        message = None
        managers = []
        ids = req.getlist('ids', [])
        fields = [f.name for f in Manager._meta.fields]
        container = ['name']
        kwargs = DynamicQuery(request, container, *fields)
        try:
            # 根据ids获取数据
            if len(ids) == 0:
                managers = Manager.objects.filter(**kwargs)
                pass
            else:
                managers = Manager.objects.filter(id__in=ids)
            total = managers.count()
            managers = list(managers[start:end])

            logging.info("managers size is %d", len(managers))
            return set_list_response(code, message, managers, page, size, total)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            return set_list_response(code, message, managers, page, size, total)

    else:
        return



