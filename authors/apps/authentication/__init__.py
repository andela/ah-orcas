from django.apps import AppConfig


class AuthenticationAppConfig(AppConfig):
    name = 'authors.apps.authentication'
    label = 'authentication'

    def ready(self):
        """
        Registers our custom app config with django
        """
        import authors.apps.authentication.signals


default_app_config = 'authors.apps.authentication.AuthenticationAppConfig'
