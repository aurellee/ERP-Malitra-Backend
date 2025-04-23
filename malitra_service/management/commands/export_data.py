from django.core.management.base import BaseCommand
from malitra_service.models import (
    Product,
    User,
    Employee,
    EkspedisiMasuk,
    Invoice,
    ItemInInvoice,
    DailySales,
    EmployeeBenefits,
    EmployeeAttendance,
    EmployeePayroll,
)

class Command(BaseCommand):
    help = 'Export all model data to a text file'
    
    def handle(self, *args, **kwargs):
        with open('data_export.txt', 'w') as f:
            # Exporting Product Details
            for product in Product.objects.all():
                f.write(
                    f"Product ID: {product.product_id}, "
                    f"Name: {product.product_name}, "
                    f"Category: {product.category}, "
                    f"Brand: {product.brand_name}, "
                    f"Quantity: {product.product_quantity}\n"
                )

            # Exporting User Details
            for user in User.objects.all():
                f.write(
                    f"User Email: {user.email}, "
                    f"Username: {user.username}\n"
                )
            
            # Exporting Employee Details
            for emp in Employee.objects.all():
                f.write(
                    f"Employee ID: {emp.employee_id}, "
                    f"Name: {emp.employee_name}, "
                    f"Role: {emp.role}, "
                    f"Hired Date: {emp.hired_date}, "
                    f"Notes: {emp.notes}\n"
                )
    
            # Exporting EkspedisiMasuk Details
            for ekspedisi in EkspedisiMasuk.objects.all():
                product = ekspedisi.product  # Get the related product object

                # You can now access the full details of the product
                f.write(
                    f"Ekspedisi ID: {ekspedisi.ekspedisi_id}, "
                    f"Product ID: {product.product_id}, "
                    f"Product Name: {product.product_name}, "
                    f"Product Quantity: {product.product_quantity}, "  # The quantity of the product
                    f"Qty: {ekspedisi.quantity}, "
                    f"Purchase Price: {ekspedisi.purchase_price}, "
                    f"Sale Price: {ekspedisi.sale_price}, "
                    f"In/Out: {ekspedisi.in_or_out}, "
                    f"Date: {ekspedisi.date}, "
                )
    
            # Exporting Invoice Details
            for inv in Invoice.objects.all():
                f.write(
                    f"Invoice ID: {inv.invoice_id}, "
                    f"Date: {inv.invoice_date}, "
                    f"Amount Paid: {inv.amount_paid}, "
                    f"Payment Method: {inv.payment_method}, "
                    f"Car Number: {inv.car_number}, "
                    f"Discount: {inv.discount}, "
                    f"Status: {inv.invoice_status}\n"
                )
            
                for item in inv.items.all():
                    product = item.product  # Fetch the related product
                    f.write(
                        f"  - Item Detail ID: {item.invoice_detail_id}, "
                        f"Product ID: {product.product_id}, "
                        f"Product Name: {product.product_name}, "
                        f"Category: {product.category}, "
                        f"Brand: {product.brand_name}, "
                        f"Price: {item.price}, "
                        f"Quantity: {item.quantity}, "
                        f"Discount Per Item: {item.discount_per_item}\n"
                    )
                    
            # Exporting DailySales Details
            for ds in DailySales.objects.all():
                f.write(
                    f"Daily Sales ID: {ds.daily_sales_id}, "
                    f"Invoice ID: {ds.invoice.invoice_id}, "
                    f"Employee: {ds.employee.employee_name}, "
                    f"Date: {ds.date}, "
                    f"Omzet: {ds.total_sales_omzet}, "
                    f"Paid: {ds.salary_paid}, "
                    f"Status: {ds.salary_status}\n"
                )
            
            # Exporting EmployeeBenefits Details
            for eb in EmployeeBenefits.objects.all():
                f.write(
                    f"Bonus ID: {eb.employee_bonus_id}, "
                    f"Employee: {eb.employee.employee_name}, "
                    f"Date: {eb.date}, "
                    f"Type: {eb.bonus_type}, "
                    f"Amount: {eb.amount}, "
                    f"Status: {eb.status}, "
                    f"Notes: {eb.notes}\n"
                )
            
            # Exporting EmployeeAttendance Details
            for ea in EmployeeAttendance.objects.all():
                f.write(
                    f"Attendance ID: {ea.employee_absence_id}, "
                    f"Employee: {ea.employee.employee_name}, "
                    f"Date: {ea.date}, "
                    f"Clock In: {ea.clock_in}, "
                    f"Clock Out: {ea.clock_out}, "
                    f"Day Count: {ea.day_count}, "
                    f"Status: {ea.absence_status}, "
                    f"Notes: {ea.notes}\n"
                )
            
            # Exporting EmployeePayroll Details
            for ep in EmployeePayroll.objects.all():
                f.write(
                    f"Payroll ID: {ep.employee_payroll_id}, "
                    f"Employee: {ep.employee.employee_name}, "
                    f"Payment Date: {ep.payment_date}, "
                    f"Sales Omzet: {ep.sales_omzet_amount}, "
                    f"Salary Paid: {ep.salary_amount}\n"
                )
