from rest_framework import generics
from rest_framework.views import APIView
from malitra_service.serializers.employeebenefits_serializers import EmployeeBenefitsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import Employee, EmployeeBenefits
from rest_framework.response import Response
from rest_framework import serializers
from datetime import datetime
from django.db.models import Sum
from django.utils import timezone

class EmployeeBenefitsListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            employee_benefits = EmployeeBenefits.objects.select_related('employee').all()
            data = []
            
            for eb in employee_benefits:
                data.append({
                    "date": eb.date,
                    "employee_id": eb.employee.employee_id,
                    "employee_name": eb.employee.employee_name,
                    "type": eb.bonus_type,
                    "amount": eb.amount,
                    "status": eb.status,
                    "notes": eb.notes,
                })
            
            return Response({"status": 200, "data": data}, status=200)
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)
        
class EmployeeBenefitsSummaryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Ambil tanggal dari request, jika tidak ada, pakai hari ini
            date_str = request.data.get('date')
            if date_str:
                try:
                    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"status": 400, "error": "Format tanggal harus YYYY-MM-DD."}, status=400)
            else:
                selected_date = timezone.localtime(timezone.now()).date()

            # Filter berdasarkan tanggal
            benefits = EmployeeBenefits.objects.filter(date=selected_date)

            total_salaries = benefits.aggregate(
                total=Sum('amount')
            )['total'] or 0.0

            total_paid = benefits.filter(status="Paid").aggregate(
                paid=Sum('amount')
            )['paid'] or 0.0

            total_unpaid = benefits.exclude(status="Paid").aggregate(
                unpaid=Sum('amount')
            )['unpaid'] or 0.0

            return Response({
                "status": 200,
                "selected_date": selected_date.strftime('%Y-%m-%d'),
                "total_salaries": round(total_salaries, 2),
                "total_paid": round(total_paid, 2),
                "total_unpaid": round(total_unpaid, 2)
            }, status=200)

        except Exception as e:
            return Response({
                "status": 500,
                "error": str(e)
            }, status=500)

class EmployeeBenefitsCreate(generics.ListCreateAPIView):
    serializer_class = EmployeeBenefitsSerializer
    permission_classes = [AllowAny]
    queryset = EmployeeBenefits.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee_benefits = serializer.save()

            return Response({
                "status": 201,
                "data": serializer.data
            }, status=201)
            
        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)

class EmployeeBenefitsDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        employee_bonus_id = request.data.get('employee_bonus_id')

        if not employee_bonus_id:
            return Response({"status": 400, "error": "Employee Bonus ID is required."}, status=400)

        try:
            employee_bonus = EmployeeBenefits.objects.get(employee_bonus_id=employee_bonus_id)
            employee_bonus.delete()
            return Response({"status": 200, "message": "Employee Bonus deleted successfully."}, status=200)
        except EmployeeBenefits.DoesNotExist:
            return Response({"status": 404, "error": "Employee Bonus not found."}, status=404)

class EmployeeBenefitsUpdate(generics.UpdateAPIView):
    serializer_class = EmployeeBenefitsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        employee_bonus_id = self.request.data.get('employee_bonus_id')

        if not employee_bonus_id:
            raise serializers.ValidationError({"employee_bonus_id": "This field is required."})

        try:
            return EmployeeBenefits.objects.get(employee_bonus_id=employee_bonus_id)
        except EmployeeBenefits.DoesNotExist:
            raise serializers.ValidationError({"employee_bonus_id": "Employee Benefits not found."})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": 200,
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)