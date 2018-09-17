from django.contrib.auth import authenticate
from rest_framework.viewsets import GenericViewSet,ViewSetMixin
from rest_framework.response import Response
from rest_framework.views import APIView
import uuid


from web import models


class AuthView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        ret = {'code':1000,'user_token':None}
        username = request.data.get('username')
        pwd = request.data.get('pwd')
        user = authenticate(username=username, password=pwd)
        if not user:
            ret['code'] = 1001
            ret['error'] = '认证错误'
        else:
            token = str(uuid.uuid4())
            models.UserToken.objects.update_or_create(user_token=token,user=user, defaults={'user_token': token})
            ret['user_token'] = token
        return Response(ret)
