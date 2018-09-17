from django.views.generic.base import TemplateView
from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from web import models

from management.forms import account


class AuthView(TemplateView, ):
    """认证基类, 如果要为其它的视图添加权限之类的, 可继续累加装饰器

    FormView,

    ...

    """

    @method_decorator(login_required(login_url=settings.LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def logout(request):
    auth.logout(request)
    return redirect(settings.LOGIN_REDIRECT_URL)


@login_required(login_url="/manage/login/")
def index(request):

    return render(request, 'management/container.html')


class Login(View):

    def get(self, request):

        return render(request, 'management/login.html')

    def post(self, request):
        error = ''
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = auth.authenticate(username=username, password=password)
        if not user:
            error = "Wrong username or password!"
            return render(request, 'management/login.html', {'error': error})
        auth.login(request, user)
        return redirect(request.GET.get('next') or settings.LOGIN_REDIRECT_URL)