from django import forms
from django.forms import Form


class ProductForm(forms.Form):
    type = forms.IntegerField(required=True, error_messages={'required': '类型不能为空'})
