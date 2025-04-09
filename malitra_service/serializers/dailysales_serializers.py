from malitra_service.models import DailySales
from rest_framework import serializers

class DailySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySales
        fields = ['employee_id', 'total_sales_omzer', 'salary_status']