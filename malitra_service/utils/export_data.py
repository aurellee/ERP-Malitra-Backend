# yourapp/utils/export_data.py

import os
import datetime
import json
from pathlib import Path
from malitra_service.models import Invoice, Employee, Product, EkspedisiMasuk, User, DailySales, EmployeeAttendance, EmployeeBenefits, EmployeePayroll, Chatbot, Permission, ItemInInvoice
from django.forms.models import model_to_dict

def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_data():
    base_path = Path(__file__).resolve().parent.parent
    json_path = base_path / "data_export.json"

    if json_path.exists():
        json_path.unlink()
        print("🧹 Old data_export.json deleted.")

    # Manual serialize
    products = list(Product.objects.values('product_id', 'product_name', 'category', 'brand_name', 'product_quantity'))
    users = list(User.objects.values('id', 'email', 'username', 'first_name', 'last_name'))
    employees = list(Employee.objects.values('employee_id', 'employee_name', 'role', 'hired_date', 'notes'))

    ekspedisi = []
    for e in EkspedisiMasuk.objects.all():
        ekspedisi.append({
            "ekspedisi_id": e.ekspedisi_id,
            "product": {
                "product_id": e.product.product_id,
                "name": e.product.product_name,
                "category": e.product.category,
                "brand": e.product.brand_name,
                "quantity": e.product.product_quantity
            },
            "qty": e.qty,
            "purchase_price": e.purchase_price,
            "sale_price": e.sale_price,
            "in_or_out": e.in_or_out,
            "date": e.date
        })

    invoices = []
    for inv in Invoice.objects.all():
        invoices.append({
            "invoice_id": inv.invoice_id,
            "date": inv.invoice_date,
            "amount_paid": inv.amount_paid,
            "payment_method": inv.payment_method,
            "car_number": inv.car_number,
            "discount": inv.discount,
            "status": inv.invoice_status,
            "items": [
                {
                    "detail_id": item.detail_id,
                    "product": {
                        "product_id": item.product.product_id,
                        "name": item.product.product_name,
                        "category": item.product.category,
                        "brand": item.product.brand_name,
                        "quantity": item.product.product_quantity
                    },
                    "price": item.price,
                    "quantity": item.quantity,
                    "discount_per_item": item.discount_per_item
                } for item in inv.items.all()
            ]
        })

    daily_sales = []
    for ds in DailySales.objects.all():
        daily_sales.append({
            "daily_sales_id": ds.daily_sales_id,
            "invoice": {
                "invoice_id": ds.invoice.invoice_id,
                "amount_paid": ds.invoice.amount_paid,
                "status": ds.invoice.invoice_status
            },
            "employee": {
                "employee_id": ds.employee.employee_id,
                "name": ds.employee.name,
                "role": ds.employee.role,
                "hired_date": ds.employee.hired_date,
                "notes": ds.employee.notes
            },
            "date": ds.date,
            "omzet": ds.omzet,
            "paid": ds.paid,
            "status": ds.status
        })

    employee_benefits = []
    for eb in EmployeeBenefits.objects.all():
        employee_benefits.append({
            "bonus_id": eb.bonus_id,
            "employee": {
                "employee_id": eb.employee.employee_id,
                "name": eb.employee.name,
                "role": eb.employee.role,
                "hired_date": eb.employee.hired_date,
                "notes": eb.employee.notes
            },
            "date": eb.date,
            "type": eb.type,
            "amount": eb.amount,
            "status": eb.status,
            "notes": eb.notes
        })

    attendance = []
    for att in EmployeeAttendance.objects.all():
        attendance.append({
            "absence_id": att.absence_id,
            "employee": {
                "employee_id": att.employee.employee_id,
                "name": att.employee.name,
                "role": att.employee.role,
                "hired_date": att.employee.hired_date,
                "notes": att.employee.notes
            },
            "date": att.date,
            "clock_in": str(att.clock_in),
            "clock_out": str(att.clock_out),
            "day_count": att.day_count,
            "status": att.status,
            "notes": att.notes
        })

    payroll = []
    for pay in EmployeePayroll.objects.all():
        payroll.append({
            "payroll_id": pay.payroll_id,
            "employee": {
                "employee_id": pay.employee.employee_id,
                "name": pay.employee.name,
                "role": pay.employee.role,
                "hired_date": pay.employee.hired_date,
                "notes": pay.employee.notes
            },
            "payment_date": pay.payment_date,
            "sales_omzet": pay.sales_omzet,
            "salary_amount": pay.salary_amount
        })

    final_data = {
        "products": products,
        "users": users,
        "employees": employees,
        "ekspedisi": ekspedisi,
        "invoices": invoices,
        "daily_sales": daily_sales,
        "employee_benefits": employee_benefits,
        "attendance": attendance,
        "payroll": payroll
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4, default=json_serial)

    print(f"✅ Exported clean nested data to {json_path}")