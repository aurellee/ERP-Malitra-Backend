# Generated by Django 5.2 on 2025-04-07 09:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('malitra_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
