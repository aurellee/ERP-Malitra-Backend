from malitra_service.models import EmployeeBenefits
from rest_framework import serializers

class EmployeeBenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBenefits
        fields = ['employee_bonus_id', 'employee', 'date', 'bonus_type', 'amount', 'status', 'notes']