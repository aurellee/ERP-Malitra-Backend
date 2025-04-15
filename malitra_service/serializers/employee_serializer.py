from rest_framework import serializers
from malitra_service.models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    def validate_employee_id(self, value):
        if self.instance is None and Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value
    class Meta:
        model = Employee
        fields = ['employee_id', 'employee_name', 'role', 'hired_date', 'notes']