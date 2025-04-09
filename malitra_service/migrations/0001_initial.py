# Generated by Django 5.2 on 2025-04-09 15:38

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employee_id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_name', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('Sales', 'Sales'), ('Mechanic', 'Mechanic')], default='Sales', max_length=20)),
                ('hired_date', models.DateField()),
                ('notes', models.CharField(default='', max_length=255)),
            ],
            options={
                'db_table': 'Employee',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('invoice_id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice_date', models.DateField(auto_now_add=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(max_length=255)),
                ('payment_method', models.CharField(max_length=255)),
                ('car_number', models.CharField(max_length=255)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice_status', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'Invoice',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('product_quantity', models.IntegerField(default=0)),
                ('category', models.CharField(choices=[('SPML', 'Spare Parts Mobil'), ('SPMR', 'Spare Parts Motor'), ('Oli', 'Oli'), ('Ban', 'Ban'), ('Aki', 'Aki'), ('Campuran', 'Campuran')], default='SPML', max_length=20)),
                ('brand_name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'Product',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('username', models.CharField(max_length=100)),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'db_table': 'User',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Chatbot',
            fields=[
                ('chatbot_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('text', models.CharField(max_length=255)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Chatbot',
            },
        ),
        migrations.CreateModel(
            name='EmployeeAttendance',
            fields=[
                ('employee_absence_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('clock_in', models.TimeField()),
                ('clock_out', models.TimeField()),
                ('day_count', models.IntegerField()),
                ('absence_status', models.CharField(max_length=255)),
                ('notes', models.CharField(max_length=255)),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.employee')),
            ],
            options={
                'db_table': 'EmployeeAttendance',
            },
        ),
        migrations.CreateModel(
            name='EmployeeBenefits',
            fields=[
                ('employee_bonus_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('bonus_type', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=255)),
                ('notes', models.CharField(max_length=255)),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.employee')),
            ],
            options={
                'db_table': 'EmployeeBenefits',
            },
        ),
        migrations.CreateModel(
            name='DailySales',
            fields=[
                ('daily_sales_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('total_sales_omzet', models.DecimalField(decimal_places=2, max_digits=10)),
                ('salary_status', models.CharField(max_length=255)),
                ('employee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.employee')),
                ('invoice_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.invoice')),
            ],
            options={
                'db_table': 'DailySales',
            },
        ),
        migrations.CreateModel(
            name='ItemInInvoice',
            fields=[
                ('invoice_detail_id', models.AutoField(primary_key=True, serialize=False)),
                ('discount_per_item', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.invoice')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.product')),
            ],
            options={
                'db_table': 'ItemInInvoice',
            },
        ),
        migrations.CreateModel(
            name='EkspedisiMasuk',
            fields=[
                ('ekspedisi_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.IntegerField()),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('in_or_out', models.IntegerField()),
                ('keterangan', models.CharField(max_length=255)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='malitra_service.product')),
            ],
            options={
                'db_table': 'EkspedisiMasuk',
            },
        ),
    ]
