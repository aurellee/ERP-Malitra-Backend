from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from datetime import date

# Create your models here.
class Product(models.Model):
    sparePartsMobil = 'SPML'
    sparePartsMotor = 'SPMR'
    oli = 'Oli'
    ban = 'Ban'
    aki = 'Aki'
    campuran = 'Campuran'
    PRODUCT_CATEGORY = (
        (sparePartsMobil, 'Spare Parts Mobil'),
        (sparePartsMotor, 'Spare Parts Motor'),
        (oli, 'Oli'),
        (ban, 'Ban'),
        (aki, 'Aki'),
        (campuran, 'Campuran'),
    )
    product_id = models.CharField(
        max_length=50, 
        primary_key=True 
    )
    product_name = models.CharField(max_length=255)
    product_quantity = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=PRODUCT_CATEGORY, default=sparePartsMobil)
    brand_name = models.CharField(max_length=255)

    def __str__(self):
        return self.product_name
    
    class Meta:
        db_table = 'Product'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=100)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'User'

class Employee(models.Model):
    sales = 'Sales'
    mechanic = 'Mechanic'
    EMPLOYEE_ROLE = (
        (sales, 'Sales'),
        (mechanic, 'Mechanic')
    )
    employee_id = models.AutoField(primary_key=True)
    employee_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=EMPLOYEE_ROLE, default=sales)
    hired_date = models.DateField()
    notes = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.employee_name
    
    class Meta:
        db_table = 'Employee'

class EkspedisiMasuk(models.Model):
    ekspedisi_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    in_or_out = models.IntegerField()
    keterangan = models.CharField(max_length=255)

    def __str__(self):
        return self.ekspedisi_id

    class Meta:
        db_table = 'EkspedisiMasuk'

class Chatbot(models.Model):
    chatbot_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.chatbot_id
    
    class Meta:
        db_table = 'Chatbot'

class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    invoice_date = models.DateField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255)
    car_number = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_status = models.CharField(max_length=255)

    def __str__(self):
        return self.invoice_id

    class Meta:
        db_table = 'Invoice'

class ItemInInvoice(models.Model):
    invoice_detail_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    discount_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.invoice_detail_id

    class Meta:
        db_table = 'ItemInInvoice'

class DailySales(models.Model):
    daily_sales_id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='sales')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_sales_omzet = models.DecimalField(max_digits=10, decimal_places=2)
    salary_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_status = models.CharField(max_length=255, default="Unpaid")

    def __str__(self):
        return self.daily_sales_id

    class Meta:
        db_table = 'DailySales'

class EmployeeBenefits(models.Model):
    employee_bonus_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    bonus_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)

    def __str__(self):
        return self.employee_bonus_id

    class Meta:
        db_table = 'EmployeeBenefits'

class EmployeeAttendance(models.Model):
    employee_absence_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    day_count = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    absence_status = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)

    def __str__(self):
        return self.employee_absence_id

    class Meta:
        db_table = 'EmployeeAttendance'

class EmployeePayroll(models.Model):
    employee_payroll_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    payment_date = models.DateTimeField()
    sales_omzet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.employee_payroll_id

    class Meta:
        db_table = 'EmployeePayroll'