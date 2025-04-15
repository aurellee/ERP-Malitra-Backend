from django.urls import path
from malitra_service.views.employee_views import *
from malitra_service.views.employee_attendance_views import *

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
]