from django.apps import AppConfig


class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clients'
    verbose_name = 'کلاینت‌ها'

    def ready(self):
        import clients.signals  # noqa
