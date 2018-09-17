from django.conf.urls import url
from web.views import (
    course,
    account,
    shop_car,
    payment,
    order
)
urlpatterns = [
    url(r'^auth/$', account.AuthView.as_view(), name='auth'),
    # 课程相关
    # 课程
    url(r'^course/$', course.CourseView.as_view({'get': 'list'}), name='course'),
    url(r'^course/(?P<pk>\d+)/$', course.CourseView.as_view({'get': 'retrieve'}), name='course_detail'),
    url(r'^degreecourse/$', course.DegreeCourse.as_view(), name='degree_course'),
    url(r'^oftenaskedquestion/$', course.OftenAskedQuestion.as_view(), name='often_asked_question'),
    url(r'^courseoutline/$', course.CourseOutLine.as_view(), name='course_outline'),
    url(r'^coursechapter/$', course.CourseChapter.as_view(), name='course_chapter'),
    # 导师和讲师
    url(r'^teacher/$', course.TeacherView.as_view({'get': 'list'}), name='teacher'),

    # 深科技相关

    # url(r'^mentor/(?P<pk>\d+)/$', course.MentorDetailView.as_view({'get': 'list'}), name='course'),
    # 奖学金相关
    url(r'^scholarship/$', course.ScholarshipView.as_view(), name='scholarship'),

    # 购物车
    url(r'^shopcar/$', shop_car.ShopCar.as_view(), name='shop_car'),
    url(r'^shopcar/(?P<course_id>\d+)/$', shop_car.ShopCarDetail.as_view(), name='shop_car_detail'),
    # 结算中心
    url(r'^payment/$', payment.PaymentView.as_view(), name='payment'),
    url(r'^order/$', order.OrderView.as_view(), name='order'),
]

