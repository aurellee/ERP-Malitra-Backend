from celery import shared_task
from datetime import date, time
from .models import Employee, EmployeeAttendance

@shared_task
def generate_daily_attendance():
    today = date.today()
    default_clock_in = time(9, 0)
    default_clock_out = time(17, 0)

    employees = Employee.objects.all()

    for employee in employees:
        # Cek biar tidak double insert
        if not EmployeeAttendance.objects.filter(employee=employee, date=today).exists():
            EmployeeAttendance.objects.create(
                employee=employee,
                date=today,
                clock_in=default_clock_in,
                clock_out=default_clock_out,
                day_count=1,
                absence_status='Present',
                notes='-'
            )
