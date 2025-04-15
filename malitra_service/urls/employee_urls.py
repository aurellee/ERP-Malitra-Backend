from django.urls import path
from malitra_service.views.employee_views import *

urlpatterns = [
    # Employee
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("employees/create/", EmployeeCreate.as_view(), name="create-employee"),
    path("employees/delete/", EmployeeDelete.as_view(), name="delete-employee"),
    path("employees/update/", EmployeeUpdate.as_view(), name="update-employee"),
    path('employees/monthlyEmployeePerformance/', MonthlyEmployeeSalesView.as_view(), name='employee-monthly-performance'),
]