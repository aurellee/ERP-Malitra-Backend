from malitra_service.models import EmployeeAttendance
from rest_framework import serializers

class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    clock_in = serializers.TimeField(required=False, allow_null=True)
    clock_out = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = EmployeeAttendance
        fields = '__all__'