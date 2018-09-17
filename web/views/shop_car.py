import json

from rest_framework.views import APIView
from rest_framework.response import Response

from django_redis import get_redis_connection
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from web.utils.response import BaseResponse
from web.utils.exceptions import PricePolicyInvalid
from web import models
from web.auth.auth import LuffyAuth


CACHE = get_redis_connection()


class ShopCar(APIView):
    authentication_classes = [LuffyAuth,]

    def get(self, request, *args, **kwargs):
        """
        获取购物车的所有内容
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # ret = BaseResponse()
        # # course_id = request.data.get("course_id")
        # # policy_id = int(request.data.get("policy_id"))
        # key = settings.SHOP_CAR_KEY % (request.auth.user_id, '*')
        # return Response(ret.dict)
        ret = BaseResponse()

        key_match = settings.SHOP_CAR_KEY %(request.auth.user_id, "*")

        course_list = []

        for key in CACHE.scan_iter(key_match, count=10):
            info = {
                "title": CACHE.hget(key,'title').decode('utf-8'),
                "img": CACHE.hget(key,'img').decode('utf-8'),
                "policy": json.loads(CACHE.hget(key,'policy').decode('utf-8')),
                "default_policy":CACHE.hget(key,'default_policy').decode('utf-8')
            }
            course_list.append(info)
        ret.data = course_list


        try:
            pass
        except Exception as e:
            ret.code = 1002
            ret.error = "获取失败"
        return Response(ret.dict)

    def post(self, request, *args, **kwargs):

        """
        获取课程ID和价格策略，并存入redis
        redis 存储
        key:luffy_shop_car_%s_%s %(course_id, policy_id)
        value: {
            title: course.name
            img: course.course_img
            valid_period_id: 1
            valid_period_name: 1个月
            price: {
                1:{period: 399, }
            }

        }
        """

        ret = BaseResponse()
        course_id = request.data.get("course_id")
        policy_id = int(request.data.get("policy_id"))
        try:
            # 获取课程名称
            course = models.Course.objects.get(id=course_id)
            policy_list = course.price_policy.all()
            # 创造一个价格策略的字典
            policy_dict = {}
            for item in policy_list:
                policy_dict[item.id] ={
                    'price': item.price,
                    'valid_period': item.valid_period,
                    'valid_period_name': item.get_valid_period_display(),
                }
            if policy_id not in policy_dict:
                raise PricePolicyInvalid('价格策略不合法')

            # 设置一个   key：value的  redis

            key = settings.SHOP_CAR_KEY % (request.auth.user_id, course_id)
            car_dict = {
                'title': course.name,
                'img': course.course_img,
                'default_policy': policy_id,
                'policy': json.dumps(policy_dict)
            }
            CACHE.hmset(key, car_dict)
            ret.data = {key: car_dict}
        except ObjectDoesNotExist as e:
            ret.error = '课程不存在'
        except PricePolicyInvalid as e:
            ret.error = '价格策略不合法'
        except Exception as e:
            ret.code = 1001
            ret.error = '设置错误'
        return Response(ret.dict)

    def patch(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            course_id = request.data.get("course_id")
            policy_id = str(request.data.get("policy_id"))
            # 拼接key  并判断是否存在 redis中
            key = settings.SHOP_CAR_KEY % (request.auth.user_id, course_id)
            if not CACHE.exists(key):
                ret.code = 1002
                ret.error = "课程不存在"
                return Response(ret.dict)
            policy_dict = json.loads(CACHE.hget(key, 'policy'), encoding='utf8')
            if policy_id not in policy_dict:
                ret.code = 1003
                ret.error = '价格策略不存在'
                return Response(ret.dict)
            CACHE.hset(key, 'default_policy', policy_id)
            ret.data = "更改成功"
        except Exception as e:
            ret.code = 1001
            ret.error = "发生错误"
        return Response(ret.data)

    def delete(self, request, *args, **kwargs):
        """
        从购物车删除掉课程
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        ret = BaseResponse()
        try:
            course_ids = request.data.get("course_ids")
            key_list = [settings.SHOP_CAR_KEY % (request.auth.user_id, course_id) for course_id in course_ids]
            CACHE.delete(*key_list)

        except Exception as e:
            ret.code = 1001
            ret.data = "删除失败"

        return Response(ret.dict)


class ShopCarDetail(APIView):
    authentication_classes = [LuffyAuth,]

    def get(self, request, *args, **kwargs):
        ret = BaseResponse()
        try:
            course_id = kwargs.get('course_id')
            policy_id = request.data.get('policy_id')
            car_key = settings.SHOP_CAR_KEY % (request.auth.user_id, course_id)
            if not CACHE.exists(car_key):
                ret.data = '课程不存在购物车'
                ret.code = 1001
                return Response(ret.dict)

            info = {
                "title": CACHE.hget(car_key, 'title').decode('utf-8'),
                "img": CACHE.hget(car_key, 'img').decode('utf-8'),
                "policy": json.loads(CACHE.hget(car_key, 'policy').decode('utf-8')),
                "default_policy": CACHE.hget(car_key, 'default_policy').decode('utf-8')
            }
            ret.data = info
        except Exception as e:
            ret.code = 1002
            ret.error = "有错"
        return Response(ret.dict)

    def put(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass






