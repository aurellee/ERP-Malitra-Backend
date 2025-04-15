from django.apps import AppConfig

class MalitraServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'malitra_service'

    def ready(self):  
        import malitra_service.signals
        
