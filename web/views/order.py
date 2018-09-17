"""
{
    "data": {
        "course_list": [
            {
                "default_policy": "1",
                "valid_period": "30",
                "course_id": "1",
                "title": "Linux基础",
                "default_coupon": "0",
                "img": "Linux01.png",
                "price": "33.0",
                "coupon": {
                    "3": {
                        "coupon_type": 2,
                        "coupon_display": "折扣券",
                        "off_percent": 70
                    },
                    "4": {
                        "coupon_type": 1,
                        "coupon_display": "满减券",
                        "money_equivalent_value": 100,
                        "minimum_consume": 200
                    }
                },
                "valid_period_name": "1个月"
            }
        ],
        "global_coupon_dict": {
            "coupon": {
                "1": {
                    "coupon_type": 0,
                    "coupon_display": "立减券",
                    "money_equivalent_value": 200
                },
                "2": {
                    "coupon_type": 2,
                    "coupon_display": "折扣券",
                    "off_percent": 70
                }
            },
            "default_coupon": "0"
        }
    },
    "code": 1000,
    "error": null
}
"""

"""
       立即支付
       :param request:
       :param args:
       :param kwargs:
       :return:
       """

"""
1. 获取用户提交数据
        {
            balance:1000,
            money:900
        }
   balance = request.data.get("balance")
   money = request.data.get("money")

2. 数据验证
    - 大于等于0
    - 个人账户是否有1000贝里

    if user.auth.user.balance < balance:
        账户贝里余额不足

优惠券ID_LIST = [1,3,4]
总价
实际支付
3. 去结算中获取课程信息
    for course_dict in redis的结算中获取：
        # 获取课程ID
        # 根据course_id去数据库检查状态

        # 获取价格策略
        # 根据policy_id去数据库检查是否还依然存在

        # 获取使用优惠券ID
        # 根据优惠券ID检查优惠券是否过期

        # 获取原价+获取优惠券类型
            - 立减
                0 = 获取原价 - 优惠券金额
                或
                折后价格 = 获取原价 - 优惠券金额
            - 满减：是否满足限制
                折后价格 = 获取原价 - 优惠券金额
            - 折扣：
                折后价格 = 获取原价 * 80 / 100

4. 全站优惠券
    - 去数据库校验全站优惠券的合法性
    - 应用优惠券：
        - 立减
            0 = 实际支付 - 优惠券金额
            或
            折后价格 =实际支付 - 优惠券金额
        - 满减：是否满足限制
            折后价格 = 实际支付 - 优惠券金额
        - 折扣：
            折后价格 = 实际支付 * 80 / 100
    - 实际支付
5. 贝里抵扣

6. 总金额校验
    实际支付 - 贝里 = money:900

7. 为当前课程生成订单

        - 订单表创建一条数据 Order
            - 订单详细表创建一条数据 OrderDetail   EnrolledCourse
            - 订单详细表创建一条数据 OrderDetail   EnrolledCourse
            - 订单详细表创建一条数据 OrderDetail   EnrolledCourse

        - 如果有贝里支付
            - 贝里金额扣除  Account
            - 交易记录     TransactionRecord

        - 优惠券状态更新   CouponRecord

        注意：
            如果支付宝支付金额0，  表示订单状态：已支付
            如果支付宝支付金额110，表示订单状态：未支付
                - 生成URL（含订单号）
                - 回调函数：更新订单状态

"""
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,mixins,generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet,ViewSetMixin

from django.conf import settings
from django_redis import get_redis_connection
from django.db import transaction
from django.db.models import F, Q

from web import models
from web.auth import auth
from web.utils.response import BaseResponse
from web.serializers import course_serializers

CACHE = get_redis_connection()


class OrderView(APIView):
    authentication_classes = [auth.LuffyAuth, ]

    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        # 传入不是数字，异常 ValueError
        balance = int(request.data.get('balance'))
        money = float(request.data.get('money'))
        # 判断金额是否大于0
        if money < 0:
            ret.code = 1002
            ret.data = "课程金额小于0，有误"
            return Response(ret.dict)
        # 判断贝里余额是否正确
        if request.auth.user.balance < balance:
            ret.code = 1001
            ret.error = "贝里余额不足"
            return Response(ret.dict)

        # 获取 优惠券列表
        coupon_list = []

        global_coupon_list = []
        # 获取结算中心的redis值
        global_key = settings.PAYMENT_GLOBAL_KEY % (request.auth.user_id,)
        # 获取课程，并获取课程对应的优惠券
        payment_keys = settings.PAYMENT_KEY % (request.auth.user_id, '*')
        course_list = []
        for item in CACHE.scan_iter(payment_keys, count=10):
            info = {}
            data = CACHE.hgetall(item)
            for key, val in data.items():
                key_str = key.decode('utf-8')
                if key_str == 'coupon':
                    info[key_str] = json.loads(val.decode('utf-8'))
                else:
                    info[key_str] = val.decode('utf-8')
            course_list.append(info)
        # default_policy 价格策略选择
        # course_list[0][default_coupon]
        course_price = 0
        for course in course_list:
            course['price'] = float(course['price'])
            course['original_price'] = course['price']
            if int(course['default_coupon']) == 0:
                # 不使用优惠券
                course_price += course['price']
                continue
            coupon_list.append(course['default_coupon'])
            coupon = models.Coupon.objects.get(id=course['default_coupon'])
            coupon_record = coupon.couponrecord_set.first()
            # 判断优惠券是否可用
            if coupon_record.status != 0:
                ret.code = 2001
                ret.error = "%s 优惠券不可用" % coupon.name
                return Response(ret.dict)
            # 判断优惠券类型

            if coupon.coupon_type == 0:
                if course['price'] - coupon.money_equivalent_value < 0:
                    course['price'] = 0
                    course_price = 0
                    continue
                else:
                    course['price'] = course['price'] - coupon.money_equivalent_value
            elif coupon.coupon_type == 1:
                if course['price'] < coupon.minimum_consume:
                    ret.code = 2002
                    ret.error = '%s 课程价格小于最小优惠' % coupon.name
                    return Response(ret.dict)
                course['price'] = course['price'] - coupon.money_equivalent_value
            else:
                course['price'] = course['price'] * coupon.off_percent / 100.0
            course_price += course['price']
            # 获取不绑定课程的优惠券
        global_coupon_dict = {
            'coupon': json.loads(CACHE.hget(global_key, 'coupon').decode('utf-8')),
            'default_coupon': json.loads(CACHE.hget(global_key, 'default_coupon').decode('utf-8'))
        }

        [global_coupon_list.append(i) for i in global_coupon_dict['coupon'].keys()]
        global_coupon_dict['default_coupon'] = int(global_coupon_dict['default_coupon'])
        if global_coupon_dict['default_coupon'] == 0:
            # 不使用全站的通用券
            pass
        else:
            coupon = models.Coupon.objects.get(id=global_coupon_dict['default_coupon'])
            coupon_record = coupon.couponrecord_set.first()
            # 判断优惠券是否可用
            if coupon_record.status != 0:
                ret.code = 2001
                ret.error = "%s 优惠券不可用" % coupon.name
                return Response(ret.dict)
            coupon_list.append(global_coupon_dict['default_coupon'])
            if coupon.coupon_type == 0:
                if course_price - coupon.money_equivalent_value < 0:
                    course_price = 0
                else:
                    course_price = course_price - coupon.money_equivalent_value
            elif coupon.coupon_type == 1:
                if course_price < coupon.minimum_consume:
                    ret.code = 2002
                    ret.error = '%s 课程价格小于最小优惠' % coupon.name
                    return Response(ret.dict)
                course_price = course_price - coupon.money_equivalent_value
            else:
                course_price = course_price * coupon.off_percent / 100.0
        # 计算课程总价格
        # for price in course_list:
        #     course_price += float(price['price'])
        # 优惠后价格计算/贝里余额是否能使用
        # 贝里余额不被选择，点击立即使用全部贝里
        #
        if course_price - balance / 10.0 < 0:
            balance_used = course_price * 10
            course_price = 0
        else:
            course_price = course_price - balance / 10.0
            balance_used = balance / 10.0
        # 判断实际价格和计算后价格是否一致
        print(course_price)
        if money != course_price:
            ret.code = 1003
            ret.data = '价格不正确'
            return Response(ret.dict)
        # 操作写数据库  事务，价格等于0 不走支付宝，价格大于0 走支付宝接口，并且 微信通知

        with transaction.atomic():
            # 贝里余额扣除
            # 优惠券修改状态
            # 删除redis结算中心
            # 交易记录
            # 修改优惠券状态
            # 优化，先创建obj, 然后在进行创建
            for coupon_id in coupon_list:
                coupon_id = int(coupon_id)
                models.Coupon.objects.get(id=coupon_id).couponrecord_set.update(status=1)
            # request.auth.user.update(balance=F('balance')-balance_used)
            request.auth.user.balance -= balance_used
            request.auth.user.save()
            # 此处还需要判断是否是使用优惠券/贝里购买
            if course_price == 0:
                status = 0
                payment_type = 3
            else:
                status = 1
                payment_type = 1
            order = models.Order.objects.create(
                order_number="先手动填写",
                account=request.auth.user,
                actual_amount=course_price,
                status=status,
                payment_type=payment_type
            )
            for course in course_list:
                course_id = course['course_id']
                valid_period = course['valid_period']
                price = course['price']
                original_price = course['original_price']
                valid_period_display = course['valid_period_name']
                order.orderdetail_set.create(
                    content_object=models.Course.objects.get(id=course_id),
                    original_price=original_price,
                    price=price,
                    valid_period_display=valid_period_display,
                    valid_period=valid_period,
                    order=order
                )
        return Response('订单post')

