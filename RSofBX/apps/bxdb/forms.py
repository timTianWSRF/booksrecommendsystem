from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.models import User
from RSofBX.apps.bxdb import models


class loginForm(forms.Form):
    username = forms.CharField(max_length = 100)
    password = forms.CharField(widget = forms.PasswordInput())

    def clean_message(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get('password')
        if username == 'admin':
            dbadmin = models.admin_info.objects.filter(admin_user=username,admin_pwd=password)
            if dbadmin:
                return 1#管理员登录成功
            else:
                return 2#密码错误
        else:
            dbuser = models.user_info.objects.filter(user_name=username)
            userinfo = models.user_info.objects.get(user_name=username,password=password)

            if not dbuser:
                return 0#用户名不存在
                #raise forms.ValidationError("User does not exist in our db!")
            elif userinfo:
                return userinfo#用户登录成功
            else:
                return 2#密码错误

        return username




class userForm(forms.Form):

    username = forms.CharField(min_length=2, max_length=10,
                               strip=True,  # 是否移除用户输入空白
                               # error_messages 为错误触发的错误信息
                               error_messages={"required": "该字段不能为空",
                                               "min_length": "用户名长度不能小于2",
                                               "max_length": "用户名长度不能大于10"},
                               # 给input添加属性
                               widget=widgets.TextInput(attrs={
                                   "class": "SignFlow-accountInput Input-wrapper",
                                   "placeholder": "手机号或邮箱",
                                   "id": "inputname"}))

    password = forms.CharField(min_length=6, max_length=20,
                               strip=True,
                               error_messages={"required": "该字段不能为空",
                                               "min_length": "密码长度不能小于6位",
                                               "max_length": "密码长度不能大于20位"},
                               widget=widgets.PasswordInput(attrs={
                                   "class": "SignFlow-accountInput Input-wrapper",
                                   "placeholder": "密码",
                                   "id": "inputPassword"}))

    age = forms.CharField(max_length=3,
                          required=True,
                          strip=True,
                          error_messages={"required": "该字段不能为空",
                                          "max_length": "年龄不能大于999"},
                                widget=widgets.TextInput(attrs={
                                    "type" :"number",
                                    "class": "SignFlow-accountInput Input-wrapper",
                                    "placeholder": "年龄",
                                    "id": "inputage"}))

    location = forms.CharField(max_length=20,
                               strip=True,
                               required=True,
                               error_messages={"required": "该字段不能为空",
                                               "max_length": "密码长度不能大于20位"},
                               widget=widgets.EmailInput(attrs={
                                 "class": "SignFlow-accountInput Input-wrapper",
                                 "placeholder": "地址",
                                 "id": "inputlocation"}))


