import json
from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from malitra_service.models import (
    Product, User, Employee,
    EkspedisiMasuk, Invoice, ItemInInvoice,
    DailySales, EmployeeBenefits,
    EmployeeAttendance, EmployeePayroll,
)

class Command(BaseCommand):
    help = 'Export all model data (with FK details) to JSON'

    def handle(self, *args, **kwargs):
        output = {
            "products": [],
            "users": [],
            "employees": [],
            "ekspedisi": [],
            "invoices": [],
            "daily_sales": [],
            "employee_benefits": [],
            "attendance": [],
            "payroll": [],
        }

        # Products
        for p in Product.objects.all():
            output["products"].append({
                "product_id": p.product_id,
                "name": p.product_name,
                "category": p.category,
                "brand": p.brand_name,
                "quantity": p.product_quantity,
            })

        # Users
        for u in User.objects.all():
            output["users"].append({
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
            })

        # Employees
        for e in Employee.objects.all():
            output["employees"].append({
                "employee_id": e.employee_id,
                "name": e.employee_name,
                "role": e.role,
                "hired_date": str(e.hired_date),
                "notes": e.notes,
            })
        emp_lookup = {e['employee_id']: e for e in output['employees']}

        # EkspedisiMasuk
        for ex in EkspedisiMasuk.objects.select_related("product").all():
            output["ekspedisi"].append({
                "ekspedisi_id": ex.ekspedisi_id,
                "product": {
                    "product_id": ex.product.product_id,
                    "name": ex.product.product_name,
                    "category": ex.product.category,
                    "brand": ex.product.brand_name,
                    "quantity": ex.product.product_quantity,
                },
                "qty": ex.quantity,
                "purchase_price": float(ex.purchase_price),
                "sale_price": float(ex.sale_price),
                "in_or_out": ex.in_or_out,
                "date": ex.date.isoformat(),
            })

        # Invoices + Items
        for inv in Invoice.objects.prefetch_related(
                Prefetch("items", queryset=ItemInInvoice.objects.select_related("product"))
            ).all():
            inv_dict = {
                "invoice_id": inv.invoice_id,
                "date": str(inv.invoice_date),
                "amount_paid": float(inv.amount_paid),
                "payment_method": inv.payment_method,
                "car_number": inv.car_number,
                "discount": float(inv.discount),
                "status": inv.invoice_status,
                "items": [],
            }
            for item in inv.items.all():
                inv_dict["items"].append({
                    "detail_id": item.invoice_detail_id,
                    "product": {
                        "product_id": item.product.product_id,
                        "name": item.product.product_name,
                        "category": item.product.category,
                        "brand": item.product.brand_name,
                        "quantity": item.product.product_quantity,
                    },
                    "price": float(item.price),
                    "quantity": item.quantity,
                    "discount_per_item": float(item.discount_per_item),
                })
            output["invoices"].append(inv_dict)

        # DailySales
        for ds in DailySales.objects.select_related("invoice", "employee").all():
            output["daily_sales"].append({
                "daily_sales_id": ds.daily_sales_id,
                "invoice": {
                    "invoice_id": ds.invoice.invoice_id,
                    "amount_paid": float(ds.invoice.amount_paid),
                    "status": ds.invoice.invoice_status,
                },
                "employee": emp_lookup.get(ds.employee.employee_id),
                "date": str(ds.date),
                "omzet": float(ds.total_sales_omzet),
                "paid": float(ds.salary_paid),
                "status": ds.salary_status,
            })

        # EmployeeBenefits
        for eb in EmployeeBenefits.objects.select_related("employee").all():
            output["employee_benefits"].append({
                "bonus_id": eb.employee_bonus_id,
                "employee": emp_lookup.get(eb.employee.employee_id),
                "date": str(eb.date),
                "type": eb.bonus_type,
                "amount": float(eb.amount),
                "status": eb.status,
                "notes": eb.notes,
            })

        # Attendance
        for ea in EmployeeAttendance.objects.select_related("employee").all():
            output["attendance"].append({
                "absence_id": ea.employee_absence_id,
                "employee": emp_lookup.get(ea.employee.employee_id),
                "date": str(ea.date),
                "clock_in": ea.clock_in.isoformat() if ea.clock_in else None,
                "clock_out": ea.clock_out.isoformat() if ea.clock_out else None,
                "day_count": float(ea.day_count),
                "status": ea.absence_status,
                "notes": ea.notes,
            })

        # Payroll
        for ep in EmployeePayroll.objects.select_related("employee").all():
            output["payroll"].append({
                "payroll_id": ep.employee_payroll_id,
                "employee": emp_lookup.get(ep.employee.employee_id),
                "payment_date": ep.payment_date.isoformat(),
                "sales_omzet": float(ep.sales_omzet_amount),
                "salary_amount": float(ep.salary_amount),
            })

        # Write JSON file
        with open("data_export.json", "w") as f:
            json.dump(output, f, indent=2)
        self.stdout.write(self.style.SUCCESS("✅ data_export.json generated"))
