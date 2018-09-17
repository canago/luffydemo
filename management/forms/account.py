from django import forms
from django.forms import widgets
from web import models


# class LoginForm(forms.ModelForm):
#     class Meta:
#         model = models.UserInfo
#         fields = ['username', 'password']
#         error_messages = {
#             "username": {"required": '用户名不能为空'},
#             "password": {"required": "密码不能为空", "max_length": "章节名不能大于128位"}
#         }
#         labels = {
#             "username": "用户名",
#             "password": "密码",
#         }
#         widgets = {
#             'username': forms.widgets.Input(attrs={'class': 'form-control', 'placeholder': 'Username'}),
#             'password': forms.widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
#         }
