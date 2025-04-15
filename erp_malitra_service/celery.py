import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_malitra_service.settings')

import django
django.setup()

app = Celery('erp_malitra_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()