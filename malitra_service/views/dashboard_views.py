from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from django.db.models import Sum, F
from datetime import datetime
from malitra_service.models import Invoice, Product, ItemInInvoice, Employee

class DashboardOverviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = datetime.now().date()

        # 1. Total Transaction Today (exclude pending)
        total_transaction = Invoice.objects.filter(
            invoice_date=today
        ).exclude(invoice_status="Pending").aggregate(
            total=Sum("amount_paid")
        )['total'] or 0

        # 2. Low Stock Items
        low_stock_count = Product.objects.filter(product_quantity__lt=30, product_quantity__gt=0).count()

        # 3. Out of Stock Items
        out_of_stock_count = Product.objects.filter(product_quantity=0).count()

        # 4. Month's Sales Income per Category
        current_month = today.month
        current_year = today.year

        categories = ["Sparepart Mobil", "Sparepart Motor", "Oli", "Aki", "Ban", "Campuran"]
        category_data = {}

        for category in categories:
            total_sales = ItemInInvoice.objects.filter(
                invoice_id__invoice_date__month=current_month,
                invoice_id__invoice_date__year=current_year,
                product_id__category=category
            ).annotate(
                total_price=(F('price') - F('discount_per_item')) * F('quantity')
            ).aggregate(total=Sum('total_price'))['total'] or 0

            category_data[category] = round(total_sales, 2)

        # 5. Employees Count by Role
        sales_count = Employee.objects.filter(role__iexact="Sales").count()
        mechanic_count = Employee.objects.filter(role__iexact="Mechanic").count()

        data = {
            "total_transaction_today": total_transaction,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "monthly_sales_by_category": category_data,
            "sales_employee_count": sales_count,
            "mechanic_employee_count": mechanic_count,
        }

        return Response({
            "status": 200,
            "data": data
        }, status=200)
