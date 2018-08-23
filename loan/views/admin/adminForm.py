# 登录参数校验
from django import forms

from loan.models import Banner, Contents
from loan.models import Medium
from loan.models import MediumLink
from loan.models import Product


class ProductForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': '名字不能为空'})
    type = forms.IntegerField(required=True, error_messages={'required': '类型不能为空'})
    icon = forms.CharField(required=True, error_messages={'required': 'icon不能为空'})
    amountStart = forms.DecimalField(required=True, error_messages={'required': '额度不能为空'})
    amountEnd = forms.DecimalField(required=True, error_messages={'required': '额度不能为空'})
    remark = forms.CharField(required=False)
    sort = forms.IntegerField(required=False)
    rateStart = forms.DecimalField(required=False)
    rateEnd = forms.DecimalField(required=False)
    introduce = forms.CharField(required=False)
    isConfig = forms.IntegerField(required=False)
    token = forms.CharField(required=False)
    pushName = forms.CharField(required=False)
    belongName = forms.CharField(required=False)

    class Meta:
        model = Product
        exclude = ['createAt', 'updateAt', 'status', 'sort']


class BannerForm(forms.ModelForm):
    img = forms.CharField(required=True, error_messages={'required': '图片链接不能为空'})
    url = forms.CharField(required=False)

    class Meta:
        model = Banner
        exclude = ['createAt', 'updateAt', 'status', 'content', 'title', 'source']


class MediumForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': '媒介名称不能为空'})

    class Meta:
        model = Medium
        exclude = ['createAt', 'updateAt', 'status', 'sort', 'type', 'linkCount','productSort1','productSort2']


class Medium_Link(forms.ModelForm):
    mediumId = forms.IntegerField(required=True, error_messages={'required': '媒介id不能为空'})

    class Meta:
        model = MediumLink
        exclude = ['createAt', 'updateAt', 'link', 'sort', 'type', 'productSort1', 'productSort2']


class ContentsForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages={'required': 'name不能为空'})
    value = forms.CharField(required=True, error_messages={'required': 'value不能为空'})
    key = forms.CharField(required=True, error_messages={'required': 'key不能为空'})

    class Meta:
        model = Contents
        exclude = ['createAt', 'updateAt']
