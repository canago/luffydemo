from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class RbacConfig(AppConfig):
    name = 'rbac'

    def ready(self):
        autodiscover_modules("rbac")