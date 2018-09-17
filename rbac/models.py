from django.db import models

# Create your models here.


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name="标题", max_length=32)
    url = models.CharField(verbose_name="URL", max_length=128)

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色
    """
    title = models.CharField(verbose_name="角色名称", max_length=32)
    permissions = models.ManyToManyField(verbose_name="角色所拥有的去权限", to="Permission", blank=True)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户", max_length=32)
    pwd = models.CharField(verbose_name="密码", max_length=32)
    email = models.CharField(verbose_name="邮箱", max_length=32)
    roles = models.ManyToManyField(verbose_name="拥有的角色",to="Role", blank=True)

    def __str__(self):
        return self.name





