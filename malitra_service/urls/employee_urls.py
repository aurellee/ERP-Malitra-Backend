from django.urls import path
from malitra_service.views.employee_views import *
from malitra_service.views.employee_attendance_views import *
from malitra_service.views.employee_benefits_views import *
from malitra_service.views.employee_payroll_views import *

urlpatterns = [
    # Employee
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("employees/create/", EmployeeCreate.as_view(), name="create-employee"),
    path("employees/delete/", EmployeeDelete.as_view(), name="delete-employee"),
    path("employees/update/", EmployeeUpdate.as_view(), name="update-employee"),
    path('employees/monthlyEmployeePerformance/', MonthlyEmployeeSalesView.as_view(), name='employee-monthly-performance'),

    # Employee Attendance
    path("employees/attendance/", EmployeeAttendanceListView.as_view(), name="employee-attendance-list"),
    path("employees/attendance/update/", EmployeeAttendanceUpdate.as_view(), name="delete-attendance-employee"),
    path("employees/attendance/detail/", EmployeeAttendanceDetailSummaryView.as_view(), name="detail-attendance-employee"),
    path("employees/attendance/summaryView/", EmployeeAttendanceSummaryView.as_view(), name="summary-attendance-employee"),

    # Employee Benefits
    path("employees/benefits/", EmployeeBenefitsListView.as_view(), name="employee-benefits-list"),
    path("employees/benefits/create/", EmployeeBenefitsCreate.as_view(), name="create-benefits-employee"),
    path("employees/benefits/delete/", EmployeeBenefitsDelete.as_view(), name="delete-benefits-employee"),
    path("employees/benefits/update/", EmployeeBenefitsUpdate.as_view(), name="update-benefits-employee"),
    path('employees/benefits/summaryView/', EmployeeBenefitsSummaryView.as_view(), name='employee-benefits-summary'),

    # Employee Payroll
    path("employees/payroll/", EmployeePayrollListView.as_view(), name="employee-payroll-list"),
    path("employees/payroll/create/", EmployeePayrollCreate.as_view(), name="create-payroll-employee"),
    path("employees/payroll/delete/", EmployeePayrollDelete.as_view(), name="delete-payroll-employee"),
    path("employees/payroll/update/", EmployeePayrollUpdate.as_view(), name="update-payroll-employee"),
]