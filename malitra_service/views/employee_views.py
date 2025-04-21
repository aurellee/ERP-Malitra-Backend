from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from malitra_service.models import DailySales, Employee, EmployeeBenefits
from django.db.models import ExpressionWrapper, F, FloatField, Sum
from datetime import datetime
from malitra_service.serializers.employee_serializers import EmployeeSerializer

class EmployeeCreate(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({"employee": 201, "data": EmployeeSerializer(employee).data}, status=200)
        else:
            return Response({"status": 400, "error": serializers.errors}, status=400)

class EmployeeListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            employees = Employee.objects.all()
            data = []
            for employee in employees:
                total_salary = DailySales.objects.filter(
                    employee_id=employee,
                    salary_status="Unpaid"
                ).aggregate(total=Sum('total_sales_omzet'))['total'] or 0
                
                total_bonus = EmployeeBenefits.objects.filter(
                    employee_id=employee,
                    status="Unpaid"
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                serialized_employee = EmployeeSerializer(employee).data
                serialized_employee['total_salary'] = float(total_salary)
                serialized_employee['total_benefit'] = float(total_bonus)
                
                data.append(serialized_employee)
            
            return Response({"status": 200, "data": data}, status=200)
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
    
    def put(self, request, *args, **kwargs):
        employee = self.get_object(request)
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "data": serializer.data})
        return Response({"status": 400, "errors": serializer.errors})

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
            
class GetEmployeeNameView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')

        if not employee_id:
            return Response({
                "status": 400,
                "error": {"employee_id": "This field is required."}
            }, status=400)

        try:
            employee = Employee.objects.get(employee_id=employee_id)
            return Response({
                "status": 200,
                "data": {"employee_name": employee.employee_name}
            }, status=200)
        except Employee.DoesNotExist:
            return Response({
                "status": 404,
                "error": {"employee_id": "Employee not found."}
            }, status=404)