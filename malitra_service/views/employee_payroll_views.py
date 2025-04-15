from rest_framework import generics
from rest_framework.views import APIView
from malitra_service.serializers.employeepayroll_serializers import EmployeePayrollSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import Employee, EmployeePayroll, DailySales, ItemInInvoice
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Sum, F
from decimal import Decimal

class EmployeePayrollListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            employee_payrolls = EmployeePayroll.objects.select_related('employee').all()
            data = []
            
            for ep in employee_payrolls:
                data.append({
                    "payment_date": ep.payment_date,
                    "employee_id": ep.employee.employee_id,
                    "employee_name": ep.employee.employee_name,
                    "role": ep.employee.role,
                    "sales_omzet_amount": ep.sales_omzet_amount,
                    "salary_amount": ep.salary_amount
                })
            
            return Response({"status": 200, "data": data}, status=200)
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class EmployeePayrollCreate(generics.ListCreateAPIView):
    serializer_class = EmployeePayrollSerializer
    permission_classes = [AllowAny]
    queryset = EmployeePayroll.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.validated_data.get("employee")
            employee_id = employee.employee_id if employee else None

            # Ambil semua DailySales terkait employee dan status invoice-nya
            daily_sales_qs = DailySales.objects.filter(
                employee_id=employee_id,
                invoice__invoice_status__in=["Unpaid", "Partially Paid", "Full Payment"]
            )

            total_omzet = Decimal("0")
            total_salary_to_pay = Decimal("0")

            for sale in daily_sales_qs:
                invoice_status = sale.invoice.invoice_status
                total_sales_omzet = sale.total_sales_omzet or Decimal("0")
                salary_paid = sale.salary_paid or Decimal("0")
                expected_salary = total_sales_omzet * Decimal("0.1")
                remaining_salary = expected_salary - salary_paid

                if invoice_status == "Full Payment":
                    if sale.salary_status == "Fully Paid":
                        continue  # Sudah dibayar penuh, skip
                    if remaining_salary > 0:
                        sale.salary_paid += remaining_salary
                        sale.salary_status = "Fully Paid"
                        total_salary_to_pay += remaining_salary

                elif invoice_status == "Partially Paid":
                    if remaining_salary > 0:
                        sale.salary_paid += remaining_salary
                        sale.salary_status = "Fully Paid" if sale.salary_paid >= expected_salary else "Partially Paid"
                        total_salary_to_pay += remaining_salary

                # Jika invoice Unpaid, skip (tidak melakukan apapun)

                total_omzet += total_sales_omzet
                sale.save()

            employee_payroll = serializer.save(
                sales_omzet_amount=total_omzet,
                salary_amount=round(total_salary_to_pay, 2)
            )

            return Response({
                "status": 201,
                "data": self.get_serializer(employee_payroll).data,
                "debug": {
                    "daily_sales_found": daily_sales_qs.count(),
                    "employee_id": employee_id,
                }
            }, status=201)

        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)

# Halaman Dashboard Employee List Table
class EmployeeSalarySummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        employees = Employee.objects.all()
        data = []

        for employee in employees:
            # Ambil semua daily sales yang masih unpaid / partially paid
            sales = DailySales.objects.filter(
                employee_id=employee.id,
                invoice_id__invoice_status__in=["Unpaid", "Partially Paid"]
            )

            total_salary_to_be_paid = 0

            for sale in sales:
                omzet = sale.total_sales_omzet or 0
                paid = sale.amount_paid or 0
                remaining = (omzet * 0.10) - paid
                if remaining > 0:
                    total_salary_to_be_paid += remaining

            data.append({
                "employee_id": employee.id,
                "employee_name": employee.name,
                "role": employee.role,
                "hired_date": employee.hired_date,
                "notes": employee.notes,
                "total_salary_to_be_paid": round(total_salary_to_be_paid, 2),
                "total_benefits": employee.benefits if hasattr(employee, "benefits") else 0,
            })

        return Response(data)

class EmployeePayrollDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        employee_payroll_id = request.data.get('employee_payroll_id')

        if not employee_payroll_id:
            return Response({"status": 400, "error": "Employee Payroll ID is required."}, status=400)

        try:
            employee_payroll = EmployeePayroll.objects.get(employee_payroll_id=employee_payroll_id)
            employee_payroll.delete()
            return Response({"status": 200, "message": "Employee Payroll deleted successfully."}, status=200)
        except EmployeeBenefits.DoesNotExist:
            return Response({"status": 404, "error": "Employee Payroll not found."}, status=404)

class EmployeePayrollUpdate(generics.UpdateAPIView):
    serializer_class = EmployeePayrollSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        employee_payroll_id = self.request.data.get('employee_payroll_id')

        if not employee_payroll_id:
            raise serializers.ValidationError({"employee_payroll_id": "This field is required."})

        try:
            return EmployeePayroll.objects.get(employee_payroll_id=employee_payroll_id)
        except EmployeePayroll.DoesNotExist:
            raise serializers.ValidationError({"employee_payroll_id": "Employee Payroll not found."})

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