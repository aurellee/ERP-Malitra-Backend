# malitra_service/signals.py

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

@receiver(post_migrate)
def setup_daily_attendance_task(sender, **kwargs):
    schedule, _ = CrontabSchedule.objects.get_or_create(minute="0", hour="0")  # tiap hari jam 00:00
    if not PeriodicTask.objects.filter(name="Generate Daily Attendance").exists():
        PeriodicTask.objects.create(
            crontab=schedule,
            name="Generate Daily Attendance",
            task="malitra_service.tasks.generate_daily_attendance",
            args=json.dumps([]),
        )
