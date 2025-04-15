from rest_framework import generics
from rest_framework.views import APIView
from malitra_service.serializers.employeeattendance_serializers import EmployeeAttendanceSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import Employee, EmployeeAttendance
from rest_framework.response import Response
from rest_framework import serializers
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class EmployeeAttendanceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            date_str = request.data.get('date') 
            
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"status": 400, "error": "Format tanggal harus YYYY-MM-DD"}, status=400)
                
                employee_attendances = EmployeeAttendance.objects.select_related('employee').filter(date=date_obj)
            else:
                employee_attendances = EmployeeAttendance.objects.select_related('employee').all()
                
            data = []
            for ea in employee_attendances:
                # Default values
                clock_in = ea.clock_in
                clock_out = ea.clock_out
                day_status = '-'

                if ea.absence_status in ['Absent', 'On Leave']:
                    # Kosongkan clock-in & clock-out
                    clock_in = '-'
                    clock_out = '-'
                    day_status = '-'
                else:
                    if clock_in and clock_out:
                        if clock_in == clock_out:
                            day_status = '-'
                        else:
                            duration = datetime.combine(datetime.today(), clock_out) - datetime.combine(datetime.today(), clock_in)
                            duration_hours = duration.total_seconds() / 3600

                            if 0 < duration_hours <= 5:
                                day_status = 'Half Day'
                            elif duration_hours > 5:
                                day_status = 'Full Day'
                    else:
                        day_status = '-'

                data.append({
                    "employee_absence_id": ea.employee_absence_id,
                    "employee_id": ea.employee.employee_id,
                    "employee_name": ea.employee.employee_name,
                    "role": ea.employee.role,
                    "date": ea.date,
                    "clock_in": clock_in,
                    "clock_out": clock_out,
                    "day_count": ea.day_count,
                    "absence_status": ea.absence_status,
                    "day_status": day_status,
                    "notes": ea.notes
                })
            
            return Response({"status": 200, "data": data}, status=200)
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class EmployeeAttendanceUpdate(generics.UpdateAPIView):
    serializer_class = EmployeeAttendanceSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        employee_absence_id = self.request.data.get('employee_absence_id')
        if not employee_absence_id:
            raise serializers.ValidationError({"employee_absence_id": "This field is required."})

        try:
            return EmployeeAttendance.objects.get(employee_absence_id=employee_absence_id)
        except EmployeeAttendance.DoesNotExist:
            raise serializers.ValidationError({"employee_absence_id": "Employee Attendance not found."})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        absence_status = data.get('absence_status', instance.absence_status).lower()

        if absence_status in ['absent', 'on leave']:
            data['day_count'] = 0
            data['clock_in'] = None
            data['clock_out'] = None
        else:
            clock_in = data.get('clock_in', instance.clock_in)
            clock_out = data.get('clock_out', instance.clock_out)

            if isinstance(clock_in, str):
                clock_in = datetime.strptime(clock_in, "%H:%M:%S").time()
            if isinstance(clock_out, str):
                clock_out = datetime.strptime(clock_out, "%H:%M:%S").time()

            if clock_in and clock_out:
                start_dt = datetime.combine(datetime.today(), clock_in)
                end_dt = datetime.combine(datetime.today(), clock_out)
                duration = end_dt - start_dt

                duration_hours = duration.total_seconds() / 3600

                if 0 < duration_hours <= 5:
                    data['day_count'] = 0.5
                elif duration_hours == 0:
                    data['day_count'] = 0
                else:
                    data['day_count'] = 1
            else:
                data['day_count'] = 0

        serializer = self.get_serializer(instance, data=data, partial=partial)
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
        
class EmployeeAttendanceDetailSummaryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")
            if not employee_id:
                return Response({"status": 400, "error": "employee_id harus disertakan dalam body"}, status=400)

            attendances = EmployeeAttendance.objects.filter(employee_id=employee_id).order_by('-date')
            data = []

            for ea in attendances:
                clock_in = ea.clock_in
                clock_out = ea.clock_out
                day_status = '-'

                if ea.absence_status in ['Absent', 'On Leave']:
                    clock_in = '-'
                    clock_out = '-'
                else:
                    if clock_in and clock_out and clock_in != clock_out:
                        duration = datetime.combine(datetime.today(), clock_out) - datetime.combine(datetime.today(), clock_in)
                        duration_hours = duration.total_seconds() / 3600
                        if 0 < duration_hours <= 5:
                            day_status = 'Half Day'
                        elif duration_hours > 5:
                            day_status = 'Full Day'

                data.append({
                    "employee_absence_id": ea.employee_absence_id,
                    "date": ea.date,
                    "clock_in": clock_in,
                    "clock_out": clock_out,
                    "day_status": day_status,
                    "absence_status": ea.absence_status,
                    "notes": ea.notes
                })

            return Response({"status": 200, "data": data}, status=200)

        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class EmployeeAttendanceSummaryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get('employee_id')
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')

            if not employee_id:
                return Response({"status": 400, "error": "employee_id is required"}, status=400)

            # Jika tanggal tidak dikirim, gunakan bulan ini sebagai default
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"status": 400, "error": "Format tanggal salah. Gunakan YYYY-MM-DD"}, status=400)
            else:
                today = date.today()
                start_date = today.replace(day=1)
                end_date = today

            attendances = EmployeeAttendance.objects.filter(
                employee_id=employee_id,
                date__range=[start_date, end_date]
            )

            summary = {
                "present_full_day": 0,
                "present_half_day": 0,
                "absent": 0,
                "on_leave": 0,
                "on_sick": 0
            }

            for ea in attendances:
                if ea.absence_status == "Absent":
                    summary["absent"] += 1
                elif ea.absence_status == "On Leave":
                    summary["on_leave"] += 1
                elif ea.absence_status == "On Sick":
                    summary["on_sick"] += 1
                elif ea.absence_status == "Present":
                    if ea.clock_in and ea.clock_out:
                        duration = datetime.combine(date.today(), ea.clock_out) - datetime.combine(date.today(), ea.clock_in)
                        hours = duration.total_seconds() / 3600
                        if hours > 5:
                            summary["present_full_day"] += 1
                        elif 0 < hours <= 5:
                            summary["present_half_day"] += 1

            return Response({
                "status": 200,
                "employee_id": employee_id,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": summary
            }, status=200)

        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)