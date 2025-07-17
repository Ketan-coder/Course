from django.apps import AppConfig


class CourseappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Courseapp'

    def ready(self):
        from . import signals