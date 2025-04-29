import json
from celery import shared_task
from datetime import date, datetime, time

import requests
from malitra_service.utils.update_vectorstore_from_postgres import update_vectorstore_from_db
from malitra_service.utils.export_data import export_data
from .models import Employee, EmployeeAttendance
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os, json, subprocess
from pathlib import Path
from malitra_service.models import Invoice, Employee, Product
from django.db import transaction

# inisialisasi sekali
EMB = OpenAIEmbeddings()
VDB = Chroma(
    persist_directory=os.getenv('CHROMA_DB_DIR'),
    embedding_function=EMB,
)

# @shared_task
# def run_update_scripts_task():
#     try:
#         subprocess.run(["python3 manage.py export data"], check=True)
#         subprocess.run(["python3 langchain_setup.py"], check=True)
#         return "✅ Update completed successfully"
#     except subprocess.CalledProcessError as e:
#         return f"❌ Error running update scripts: {str(e)}"

# @shared_task
# def export_and_rebuild_task():
#     try:
#         print("⏳ Waiting 5 seconds to ensure database commit...")
#         time.sleep(5)  # Delay 5 detik
#         export_data()
#         rebuild_vectorstore()
#         response = requests.post("http://localhost:3000/reload-vectorstore/")
#         if response.status_code == 200:
#             print("✅ Reload vectorstore API called successfully.")
#         else:
#             print(f"⚠️ Failed to reload vectorstore via API: {response.status_code}")
#         return "✅ Export and rebuild completed."
#     except Exception as e:
#         print(f"❌ Error during export and rebuild: {e}")
#         return f"❌ Error: {e}"


# def json_serial(obj):
#     """JSON serializer for objects not serializable by default"""
#     if isinstance(obj, (datetime.datetime, datetime.date)):
#         return obj.isoformat()
#     raise TypeError(f"Type {type(obj)} not serializable")


@shared_task
def refresh_vectorstore_task():
    print("🔁 Running vectorstore refresh task...")
    update_vectorstore_from_db()
    

@shared_task
def generate_daily_attendance():
    today = date.today()
    default_clock_in = time(9, 0)
    default_clock_out = time(17, 0)

    employees = Employee.objects.all()

    for employee in employees:
        try:
            with transaction.atomic():
                if not EmployeeAttendance.objects.select_for_update().filter(employee=employee, date=today).exists():
                    EmployeeAttendance.objects.create(
                        employee=employee,
                        date=today,
                        clock_in=default_clock_in,
                        clock_out=default_clock_out,
                        day_count=1,
                        absence_status='Present',
                        notes='-'
                    )
        except Exception as e:
            print(f"⚠️ Failed to create attendance for {employee}: {e}")