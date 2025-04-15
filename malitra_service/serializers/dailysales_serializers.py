from malitra_service.models import DailySales
from rest_framework import serializers

class DailySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySales
        fields = ['employee', 'total_sales_omzet', 'salary_status']
        read_only_fields = ['salary_status']