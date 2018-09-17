from rbac.service.stark import site
from web import models
from rbac.service.stark import StarkConfig


class CouponConfig(StarkConfig):
    list_display = [StarkConfig.display_checkbox, 'id', 'name', StarkConfig.display_edit_btn]


site.register(models.UserInfo)
site.register(models.Course)
site.register(models.Coupon, CouponConfig)