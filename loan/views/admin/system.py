import json
import logging
import traceback

from django import forms
from django.views.decorators.csrf import csrf_exempt

from loan.common import set_response, set_list_response
from loan.models import Module, Role, Manager
from loan.util import getTimeStamp

logging = logging.getLogger("system")


class ModuleForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': 'name不能为空'})
    url = forms.CharField(required=False)
    permissions = forms.CharField(required=False)
    parentId = forms.IntegerField(required=False)
    level = forms.IntegerField(required=False)

    class Meta:
        model = Module
        exclude = ['createAt', 'updateAt']



class RoleForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': 'name不能为空'})
    modules = forms.CharField(required=True,error_messages={'required': 'modules不能为空'})
    permissions = forms.CharField(required=True,error_messages={'required': 'permissions不能为空'})


    class Meta:
        model = Role
        exclude = ['createAt', 'updateAt','updateBy','createBy']


# 添加模块
@csrf_exempt
def addModule(request):
    if request.method == 'POST':
        req = request.POST
        code = 0
        message = None
        try:
            moduleForm = ModuleForm(req)
            if moduleForm.is_valid():
                module = ModuleForm(req, instance=Module(createAt=getTimeStamp(), updateAt=getTimeStamp()))
                module.save()
                logging.info("add module success")
                pass
            else:
                code = -10
                message = moduleForm.errors
                pass
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})

    else:
        return


# 修改模块
@csrf_exempt
def updateModule(request, moduleId):
    if request.method == 'PUT':
        req = request.PUT
        code = 0
        message = None
        try:
            # 验证数据有效性
            module = Module.objects.filter(id=moduleId).first()
            if not module:
                code = -30
                return set_response(code, message, {})
            else:
                pass

            moduleForm = ModuleForm(req)
            if moduleForm.is_valid():
                module = ModuleForm(req, instance=module)
                module.save()
                logging.info("add module success")
                pass
            else:
                code = -10
                message = moduleForm.errors
                pass
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})
    if request.method == 'DELETE':
        code = 0
        message = None
        try:
            # 验证数据有效性
            module = Module.objects.filter(id=moduleId).first()
            if not module:
                code = -30
                return set_response(code, message, {})
            else:
                module.delete()
                pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})

    else:
        return


# 获取模块信息
@csrf_exempt
def getModules(request):
    if request.method == 'GET':
        req = request.GET
        code = 0
        message = None
        page = int(req.get('page', 1))
        size = int(req.get('size', 1000))
        start = (page - 1) * size
        end = start + size
        total = 0
        modules = []
        ids = req.getlist('ids', [])
        logging.info("ids is %s", ids)
        try:
            # 根据ids获取数据
            if len(ids) == 0:
                modules = Module.objects.all()
                pass
            else:
                modules = Module.objects.filter(id__in=ids)
            total = modules.count()
            modules = list(modules[start:end])
            logging.info("modules size is %d", len(modules))
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_list_response(code, message, modules, page, size, total)

    else:
        return



# 添加角色
@csrf_exempt
def addRole(request):
    if request.method == 'POST':
        req = request.POST
        code = 0
        message = None
        try:
            currentManager = json.loads(request.__getattribute__('manager'))
            roleForm = RoleForm(req)
            if roleForm.is_valid():
                role = RoleForm(req, instance=Role(createAt=getTimeStamp(), updateAt=getTimeStamp(),createBy=currentManager.get('name'),updateBy=currentManager.get('name')))
                role.save()
                logging.info("add role success")
                pass
            else:
                code = -10
                message = roleForm.errors
                pass
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})

    else:
        return


# 修改角色
@csrf_exempt
def updateRole(request, roleId):
    if request.method == 'PUT':
        req = request.PUT
        code = 0
        message = None
        try:
            currentManager = json.loads(request.__getattribute__('manager'))

            # 验证数据有效性
            role = Role.objects.filter(id=roleId).first()
            if not role:
                code = -30
                return set_response(code, message, {})
            else:
                pass

            roleForm = RoleForm(req)
            if roleForm.is_valid():
                role = RoleForm(req, instance=role)
                role.updateBy = currentManager.get('name')
                role.save()
                logging.info("add module success")
                pass
            else:
                code = -10
                message = roleForm.errors
                pass
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, {})

    elif request.method == 'GET':
        req = request.GET
        role = {}
        code = 0
        message = None
        try:
            # 验证数据有效性
            role = Role.objects.filter(id=roleId).first()
            if not role:
                code = -30
                return set_response(code, message, {})
            else:
                role = role.to_dire()
                pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, role)
    elif request.method == 'DELETE':
        role = {}
        code = 0
        message = None
        try:
            # 验证数据有效性
            role = Role.objects.filter(id=roleId).first()
            if not role:
                code = -30
                return set_response(code, message, {})
            else:
                managers = Manager.objects.filter(role=roleId)
                if managers.exists():
                    code = -60
                    return set_response(code,message,{})
                else:
                    role.delete()
                pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_response(code, message, role)

    else:
        return


# 获取角色信息
@csrf_exempt
def getRoles(request):
    if request.method == 'GET':
        req = request.GET
        code = 0
        page = int(req.get('page', 1))
        size = int(req.get('size', 10))
        start = (page - 1) * size
        end = start + size
        total = 0
        message = None
        roles = []
        ids = req.getlist('ids', [])
        logging.info("ids is %s", ids)
        try:
            # 根据ids获取数据
            if len(ids) == 0:
                roles = Role.objects.all()
                pass
            else:
                roles = Role.objects.filter(id__in=ids)
            total = roles.count()
            roles = list(roles[start:end])
            logging.info("modules size is %d", len(roles))
            pass
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            code = -10000
            pass
        finally:
            return set_list_response(code, message, roles, page, size, total)

    else:
        return



