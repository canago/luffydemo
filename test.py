# import redis
# conn = redis.Redis(host='10.10.10.122', port=6379)
#  1
# # conn.flushall()
#
# print(conn.keys("*"))
# print(conn.hgetall('luffy_payment_1_1'))
# for i in conn.scan_iter("luffy_payment_1_*"):
#     print(conn.hgetall(i))
# # print(conn.hget("*", 'title'))
# # print(conn.hgetall("*"))
# # print(conn.hgetall("luffy_shop_car_1_1"))
# # if not {}:
# #     print(1)

#
# import importlib
# s = "test02.Foo"
#
# k, v = s.rsplit('.')
# m = importlib.import_module(k)
# print(m, v)
# cls = getattr(m, v)
# for i in dir(cls):
#     if i.isupper():
#         print(i, getattr(cls, i))

# s = '123a'
# int(s)



