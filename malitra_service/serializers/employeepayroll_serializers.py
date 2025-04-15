from malitra_service.models import EmployeePayroll
from rest_framework import serializers

class EmployeePayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePayroll
        fields = ['employee_payroll_id', 'employee', 'payment_date', 'sales_omzet_amount', 'salary_amount']