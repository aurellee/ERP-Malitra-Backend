# Generated by Django 5.2 on 2025-04-07 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('malitra_service', '0002_invoice_invoice_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
