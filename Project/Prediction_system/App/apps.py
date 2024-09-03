from django.apps import AppConfig

# Изменения для корректного отображения имени системы

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'
    verbose_name = 'Система прогнозирования'