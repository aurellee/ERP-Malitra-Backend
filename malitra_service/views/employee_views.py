from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from malitra_service.models import DailySales, Employee, EmployeeBenefits
from django.db.models import Sum
from datetime import datetime
from malitra_service.serializers import EmployeeSerializer

class EmployeeCreate(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({"employee": 201, "data": EmployeeSerializer(employee).data}, status=200)
        else:
            return Response({"status": 400, "error": serializers.errors}, status=400)

class EmployeeList(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            employees = Employee.objects.all()
            serializer = EmployeeSerializer(employees, many=True)
            return Response({"status": 200, "data": serializer.data}, status=200)
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class EmployeeUpdate(APIView):
    permission_classes = [AllowAny]
    
    def get_object(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
            
        if not employee_id:
            raise serializers.ValidationError({"status": 400, "error": {"employee_id": "This field is required."}})
        
        try:
            return Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"status": 404, "error": {"employee_id": "Employee not found."}})

class EmployeeDelete(APIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            raise serializers.ValidationError({"status": 400, "error": {"employee_id": "This field is required."}})
        
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.delete()
            return Response({"status": 200, "message": "Employee deleted successfully."}, status=200)
        except Employee.DoesNotExist:
            return Response({"status": 404, "error": "Employee not found."}, status=404)

class MonthlyEmployeeSalesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            today = datetime.today()
            current_year = today.year
            current_month = today.month

            monthly_sales = DailySales.objects.filter(date__year=current_year, date__month=current_month)

            summary = monthly_sales.values(
                'employee_id', 
                'employee_id__employee_name', 
                'employee_id__role').annotate(
                    total_omzet=Sum('total_sales_omzet')
            )

            result = [{
                'employee_id': s['employee_id'],
                'employee_name': s['employee_id__employee_name'],
                'role': s['employee_id__role'],
                'total_omzet': s['total_omzet']
            } for s in summary]

            return Response({
                "status": 200,
                "data": result 
            }, status=200)

        except Exception as e:
            return Response({
                "status": 500,
                "error": str(e)
            }, status=500)

class EmployeeSummaryView(APIView):
    permission_classes = [AllowAny]a

    def get(self, request, *args, **kwargs):
        try:
            today = datetime.today()
            current_year = today.year
            current_month = today.month

            # Total Salaries
            monthly_sales = DailySales.objects.filter(date__year=current_year, date__month=current_month)

            total_omzet = monthly_sales.aggregate(
                total_omzet=Sum('total_sales_omzet')
            )['total_omzet'] or 0.0

            total_salaries = total_omzet * 10 / 100
            
            # Total Unpaid Salary
            total_unpaid_salary = monthly_sales.filter(
                salary_status='Unpaid'
            ).aggregate(
                total_unpaid_salary=Sum('total_sales_omzet')
            )['total_unpaid_salary'] or 0.0

            # Total Bonus
            bonus = EmployeeBenefits.objects.filter(date__year=current_year, date__month=current_month)
            
            total_bonus = bonus.aggregate(
                total_bonus=Sum('amount')
            )['total_bonus'] or 0.0
            
            # Total Unpaid Bonus
            total_unpaid_bonus = bonus.filter(
                status='Unpaid'
            ).aggregate(
                total_unpaid_bonus=Sum('amount')
            )['total_unpaid_bonus'] or 0.0
            
            return Response({
                "status": 200,
                "total_salaries": total_salaries,
                "total_unpaid_salary": total_unpaid_salary,
                "total_bonus": total_bonus,
                "total_unpaid_bonus": total_unpaid_bonus
            }, status=200)
        
        except Exception as e:
            return Response({
                "status": 500,
                "error": str(e)
            }, status=500)

