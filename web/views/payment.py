import json
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response

from django_redis import get_redis_connection
from django.conf import settings

from web.utils.response import BaseResponse
from web.auth.auth import LuffyAuth
from web import models

CACHE = get_redis_connection()


class PaymentView(APIView):
    authentication_classes = [LuffyAuth,]

    def get(self, request, *args, **kwargs):
        ret = BaseResponse()
        # luffy_payment_1_*
        redis_payment_key = settings.PAYMENT_KEY % (request.auth.user_id, "*",)

        # luffy_payment_coupon_1
        redis_global_coupon_key = settings.PAYMENT_GLOBAL_KEY % (request.auth.user_id,)
        course_list = []
        for key in CACHE.scan_iter(redis_payment_key, count=10):
            info = {}
            data = CACHE.hgetall(key)
            for k, v in data.items():
                kk = k.decode('utf-8')
                if kk == "coupon":
                    info[kk] = json.loads(v.decode('utf-8'))
                else:
                    info[kk] = v.decode('utf-8')
            course_list.append(info)
        global_coupon_dict = {
            'coupon': json.loads(CACHE.hget(redis_global_coupon_key, 'coupon').decode('utf-8')),
            'default_coupon': CACHE.hget(redis_global_coupon_key, 'default_coupon').decode('utf-8')
        }

        ret.data = {
            "course_list": course_list,
            "global_coupon_dict": global_coupon_dict
        }

        return Response(ret.dict)

    def post(self, request, *args, **kwargs):
        ret = BaseResponse()
        ret.course_coupon = {}
        # 删除结算中心
        key_list = CACHE.keys(settings.PAYMENT_KEY % (request.auth.user_id, "*",))
        key_list.append(settings.PAYMENT_GLOBAL_KEY % (request.auth.user_id,))
        CACHE.delete(*key_list)

        payment_dict = {}
        global_coupon_dict = {
            "coupon": {},
            "default_coupon": 0
        }

        course_id_list = request.data.get('course_ids')
        for couse_id in course_id_list:
            car_key = settings.SHOP_CAR_KEY %(request.auth.user_id, couse_id)
            if not CACHE.exists(car_key):
                ret.data = "购物车不存在此课程"
                ret.key = car_key
                ret.code = 1002
                return Response(ret.dict)
            # 获取客户选择的价格策略
            policy = json.loads(CACHE.hget(car_key, 'policy').decode('utf-8'))
            default_policy = CACHE.hget(car_key, 'default_policy').decode('utf-8')
            policy_info = policy[default_policy]

            # 构建结算中心字典
            payment_course_dict = {
                'course_id': str(couse_id),
                'title': CACHE.hget(car_key, 'title').decode('utf-8'),
                'img': CACHE.hget(car_key, 'img').decode('utf-8'),
                'coupon': {},
                'default_policy': default_policy,
                'default_coupon': 0
            }
            payment_course_dict.update(policy_info)
            payment_dict[str(couse_id)] = payment_course_dict

        # 获取优惠券
        ctime = datetime.date.today()
        coupon_list = models.CouponRecord.objects.filter(
            account=request.auth.user,
            status=0,
            coupon__valid_begin_date__lte=ctime,
            coupon__valid_end_date__gte=ctime,
        )
        for item in coupon_list:
            coupon_id = item.id
            coupon_type = item.coupon.coupon_type
            info = {}
            info['coupon_type'] = coupon_type
            info['coupon_display'] = item.coupon.get_coupon_type_display()
            if coupon_type == 0:
                info['money_equivalent_value'] = item.coupon.money_equivalent_value
            elif coupon_type == 1:
                info['money_equivalent_value'] = item.coupon.money_equivalent_value
                info['minimum_consume'] = item.coupon.minimum_consume
            else:
                info['off_percent'] = item.coupon.off_percent
            if not item.coupon.object_id:
                # 没有绑定课程ID的
                global_coupon_dict['coupon'][coupon_id] = info
                continue
            coupon_course_id = str(item.coupon.object_id)

            if coupon_course_id not in payment_dict:
                continue
            payment_dict[coupon_course_id]['coupon'][coupon_id] = info

        # 这里需要再次研究
        for cid, cinfo in payment_dict.items():
            pay_key = settings.PAYMENT_KEY % (request.auth.user_id, cid,)
            cinfo['coupon'] = json.dumps(cinfo['coupon'])
            CACHE.hmset(pay_key, cinfo)
        # 3.2 将全站优惠券写入redis
        gcoupon_key = settings.PAYMENT_GLOBAL_KEY % (request.auth.user_id,)
        global_coupon_dict['coupon'] = json.dumps(global_coupon_dict['coupon'], ensure_ascii=False)
        CACHE.hmset(gcoupon_key, global_coupon_dict)

        # except Exception as e:
        #     ret.code = 1001
        #     ret.data = "报错啦"
        return Response(ret.dict)

    def patch(self, request, *args, **kwargs):
        # 待写   直接复制粘贴
        ret = BaseResponse()
        try:
            # 1. 用户提交要修改的优惠券
            course = request.data.get('courseid')
            course_id = str(course) if course else course

            coupon_id = str(request.data.get('couponid'))

            # payment_global_coupon_1
            redis_global_coupon_key = settings.PAYMENT_GLOBAL_KEY % (request.auth.user_id,)

            # 修改全站优惠券
            if not course_id:
                if coupon_id == "0":
                    # 不使用优惠券,请求数据：{"couponid":0}
                    CACHE.hset(redis_global_coupon_key, 'default_coupon', coupon_id)
                    ret.data = "修改成功"
                    return Response(ret.dict)
                # 使用优惠券,请求数据：{"couponid":2}
                coupon_dict = json.loads(CACHE.hget(redis_global_coupon_key, 'coupon').decode('utf-8'))

                # 判断用户选择得优惠券是否合法
                if coupon_id not in coupon_dict:
                    ret.code = 1001
                    ret.error = "全站优惠券不存在"
                    return Response(ret.dict)

                # 选择的优惠券合法
                CACHE.hset(redis_global_coupon_key, 'default_coupon', coupon_id)
                ret.data = "修改成功"
                return Response(ret.dict)

            # 修改课程优惠券
            # luffy_payment_1_1
            redis_payment_key = settings.PAYMENT_KEY % (request.auth.user_id, course_id,)
            # 不使用优惠券
            if coupon_id == "0":
                CACHE.hset(redis_payment_key, 'default_coupon', coupon_id)
                ret.data = "修改成功"
                return Response(ret.dict)

            # 使用优惠券
            coupon_dict = json.loads(CACHE.hget(redis_payment_key, 'coupon').decode('utf-8'))
            if coupon_id not in coupon_dict:
                ret.code = 1010
                ret.error = "课程优惠券不存在"
                return Response(ret.dict)

            CACHE.hset(redis_payment_key, 'default_coupon', coupon_id)

        except Exception as e:
            ret.code = 1111
            ret.error = "修改失败"

        return Response(ret.dict)

