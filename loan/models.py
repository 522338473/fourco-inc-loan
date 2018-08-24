# Create your models here.

from django.db import models
from loan_sys.storage import ImageStorage


# 用户
class User(models.Model):
    id = models.AutoField(primary_key=True)
    nick = models.CharField(max_length=20)
    idCard = models.CharField(db_column='id_card', max_length=20, default='')
    mobile = models.CharField(max_length=20)
    isDone = models.IntegerField(db_column='is_done', default=0)
    amount = models.IntegerField(default=0)
    estate = models.IntegerField(default=0)
    car = models.IntegerField(default=0)
    card = models.IntegerField(default=0)
    lifeInsurance = models.IntegerField(default=0, db_column='life_insurance')
    feeInsurance = models.IntegerField(default=0, db_column='fee_insurance')
    livingTime = models.IntegerField(default=0, db_column='living_time')
    profession = models.IntegerField(default=0)
    income = models.IntegerField(default=0)
    provident = models.IntegerField(default=0)
    workExp = models.IntegerField(default=0, db_column='work_exp')
    source = models.IntegerField(default=0)
    sourceLink = models.CharField(max_length=300, db_column='source_link', null=True)
    linkId = models.BigIntegerField(db_column='link_id', null=True)
    productIndex = models.IntegerField(db_column='product_index', default=0)
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    doneAt = models.BigIntegerField(db_column='done_at', null=True)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    sex = models.IntegerField(default=0)
    city = models.IntegerField(default=0)
    salaryPayment = models.IntegerField(default=0, db_column='salary_payment')
    overdue = models.IntegerField(default=0)
    secure = models.CharField(db_column='secure', max_length=256, default='')

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# banner表
class Banner(models.Model):
    id = models.AutoField(primary_key=True)
    img = models.CharField(max_length=500)
    source = models.CharField(max_length=200, null=True)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=200, null=True)
    content = models.CharField(max_length=500, null=True)
    status = models.IntegerField(default=0)
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 媒介表
class Medium(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    sort = models.IntegerField(default=1)
    linkCount = models.IntegerField(db_column='link_count', default=0)
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    productSort1 = models.TextField(db_column='product_sort_1', null=True, default=None)
    productSort2 = models.TextField(db_column='product_sort_2', null=True, default=None)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 媒体链接表
class MediumLink(models.Model):
    id = models.AutoField(primary_key=True)
    mediumId = models.BigIntegerField(db_column='medium_id', default=None)
    type = models.IntegerField(default=id)
    link = models.CharField(max_length=500)
    sort = models.IntegerField(default=1)
    productSort1 = models.TextField(db_column='product_sort_1', null=True, default=None)
    productSort2 = models.TextField(db_column='product_sort_2', null=True, default=None)
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)

    class Meta:
        db_table = 'loan_medium_link'

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 短信
class Sms(models.Model):
    id = models.AutoField(primary_key=True)
    msg = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    count = models.IntegerField(default=1)
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    sendAt = models.BigIntegerField(db_column='send_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    type = models.IntegerField(default=1, null=False)
    introduce = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=200)
    status = models.IntegerField(default=0)
    remark = models.CharField(max_length=200)
    amountStart = models.DecimalField(db_column='amount_start', null=False, default=0, decimal_places=2, max_digits=10)
    amountEnd = models.DecimalField(db_column='amount_end', null=False, default=0, decimal_places=2, max_digits=10)
    url = models.CharField(max_length=200, blank=True)
    rateStart = models.DecimalField(db_column='rate_start', max_digits=5, decimal_places=2, default=0)
    rateEnd = models.DecimalField(db_column='rate_end', max_digits=5, decimal_places=2, default=0)
    sort = models.IntegerField(default=1)
    isConfig = models.IntegerField(db_column='is_config', default=0)
    token = models.CharField(null=True, max_length=200)
    pushName = models.CharField(null=True, max_length=200, db_column='push_name')
    belongName = models.CharField(null=True, max_length=200, db_column='belong_name')
    createAt = models.BigIntegerField(db_column='create_at', null=False)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 媒介统计表
class Medium_Statistics(models.Model):
    id = models.AutoField(primary_key=True)
    mediumName = models.CharField(db_column='medium_name', max_length=50)
    mediumId = models.BigIntegerField(db_column='medium_id', null=False)
    linkId = models.BigIntegerField(db_column='link_id', null=False)
    link = models.CharField(max_length=200)
    newCount = models.IntegerField(db_column='new_count', default=0)
    newIds = models.TextField(db_column='new_ids')
    oldCount = models.IntegerField(db_column='old_count', default=0)
    oldIds = models.TextField(db_column='old_ids')
    updateAt = models.BigIntegerField(db_column='update_at')
    createAt = models.BigIntegerField(db_column='create_at')

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 分单统计表
class Product_Statistics(models.Model):
    id = models.AutoField(primary_key=True)
    productId = models.BigIntegerField(db_column='product_id', null=False)
    productName = models.CharField(db_column='product_name', max_length=20)
    orderCount = models.IntegerField(db_column='order_count', default=0)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    createAt = models.BigIntegerField(db_column='create_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 客户用户分单关系表
class Product_User_Relation(models.Model):
    id = models.AutoField(primary_key=True)
    productName = models.CharField(db_column='product_name', max_length=50)
    productId = models.BigIntegerField(db_column='product_id', null=False)
    userId = models.BigIntegerField(db_column='user_id', null=False)
    updateAt = models.BigIntegerField(db_column='update_at')
    createAt = models.BigIntegerField(db_column='create_at')

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 常量表，目前仅存储N值
class Contents(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    value = models.CharField(max_length=50, null=False)
    key = models.CharField(max_length=50, null=False)
    updateAt = models.BigIntegerField(db_column='update_at')
    createAt = models.BigIntegerField(db_column='create_at')

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 图片上传配置相关表
class Img(models.Model):
    # 如果上传文件可以将ImageField换为FileField
    image = models.ImageField(upload_to='img/%Y/%m/%d', storage=ImageStorage())


# 账号表
class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    role = models.BigIntegerField(default=1, null=False)
    pwd = models.CharField(max_length=200)
    permission = models.CharField(max_length=500, default="{}")
    createAt = models.BigIntegerField(db_column='create_at')
    updateAt = models.BigIntegerField(db_column='update_at')
    createBy = models.CharField(db_column='create_by', max_length=50, null=True)
    updateBy = models.CharField(db_column='update_by', max_length=50, null=True)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 角色表
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    modules = models.CharField(max_length=200, null=False)
    permissions = models.CharField(max_length=50, null=False, default='rw')
    updateAt = models.BigIntegerField(db_column='update_at')
    createAt = models.BigIntegerField(db_column='create_at')
    createBy = models.CharField(db_column='create_by', max_length=50, null=True)
    updateBy = models.CharField(db_column='update_by', max_length=50, null=True)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 模块表
class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    url = models.CharField(max_length=200, null=True)
    parentId = models.BigIntegerField(db_column='parent_id', null=True)
    permissions = models.CharField(max_length=50, null=True, default='rw')
    level = models.CharField(max_length=50, null=True, default='rw')
    updateAt = models.BigIntegerField(db_column='update_at')
    createAt = models.BigIntegerField(db_column='create_at')

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 推荐pv/uv统计表
class Recommend_Statistics(models.Model):
    id = models.AutoField(primary_key=True)
    mediumId = models.BigIntegerField(db_column='medium_id', null=False)
    mediumName = models.CharField(db_column='medium_name', max_length=20)
    productId = models.BigIntegerField(db_column='product_id', null=False)
    productName = models.CharField(db_column='product_name', null=True, max_length=50)
    linkId = models.IntegerField(default=0,db_column="link_id")
    uv = models.IntegerField(default=0)
    pv = models.IntegerField(default=0)
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    createAt = models.BigIntegerField(db_column='create_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data


# 访问记录表
class Record(models.Model):
    id = models.AutoField(primary_key=True)
    mediumId = models.BigIntegerField(db_column='medium_id', null=True)
    productId = models.BigIntegerField(db_column='product_id', null=True)
    linkId = models.IntegerField(db_column="link_id", default=0, null=True)
    userId = models.IntegerField(db_column="user_id")
    updateAt = models.BigIntegerField(db_column='update_at', null=False)
    createAt = models.BigIntegerField(db_column='create_at', null=False)

    # 用于之后预处理为json
    def to_dire(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data
