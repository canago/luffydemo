from django.conf.urls import url
from management.views import account

urlpatterns = [

    url(r'^$', account.index, name='index'),
    url(r'^login/$', account.Login.as_view(), name='login'),
    url(r'^logout/$', account.logout, name='logout'),

]
