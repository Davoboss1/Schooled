from django.apps import AppConfig


class AdminsConfig(AppConfig):
    name = 'admins'
    def ready(self):
        from . import signals
