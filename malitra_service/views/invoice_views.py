from rest_framework import generics, status
from rest_framework.views import APIView
from malitra_service.serializers.invoice_serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import Invoice, ItemInInvoice, DailySales, Employee, Product
from rest_framework.response import Response
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import datetime
from decimal import Decimal

# Create your views here.
class InvoiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            invoices = Invoice.objects.exclude(invoice_status="Pending")
            result = []

            for invoice in invoices:
                items = ItemInInvoice.objects.filter(invoice=invoice)
                
                print(f"Invoice {invoice.invoice_id} has {items.count()} items")

                for item in items:
                    print(f"  - Product: {item.product.product_name}, Price: {item.price}, Discount/item: {item.discount_per_item}, Qty: {item.quantity}")

                total_price = sum((item.price * item.quantity) - item.discount_per_item for item in items) - invoice.discount
                unpaid_amount = total_price - Decimal(invoice.amount_paid)
                
                related_daily_sales = DailySales.objects.filter(invoice=invoice).select_related('employee')

                sales = None
                mechanic = None
                
                for ds in related_daily_sales:
                    role = ds.employee.role
                    name = ds.employee.employee_name
                    
                    if role == "Sales" and sales is None:
                        sales = name
                    elif role == "Mechanic" and mechanic is None:
                        mechanic = name
                    
                    if sales and mechanic:
                        break

                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'invoice_date': invoice.invoice_date,
                    'sales': sales,
                    'mechanic': mechanic,
                    'total_price': total_price,
                    'amount_paid': float(invoice.amount_paid),
                    'unpaid_amount': float(unpaid_amount),
                    'payment_method': invoice.payment_method,
                    'car_number': invoice.car_number,
                    'discount': float(invoice.discount),
                    'invoice_status': invoice.invoice_status,
                }

                result.append(invoice_data)
            
            return Response({"status": 200, "data": result}, status=200)
        
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class InvoiceSummaryFilter(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')

            if not start_date_str or not end_date_str:
                return Response({"status": 400, "error": "start_date and end_date fields are required in JSON body."}, status=400)

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            invoices = Invoice.objects.filter(invoice_date__range=(start_date, end_date))

            total_paid = invoices.aggregate(total=Sum('amount_paid'))['total'] or 0
            total_paid_cash = invoices.filter(payment_method="Cash").aggregate(total=Sum('amount_paid'))['total'] or 0
            total_paid_transfer = invoices.filter(payment_method="Transfer Bank").aggregate(total=Sum('amount_paid'))['total'] or 0

            total_unpaid = 0
            for invoice in invoices:
                items = ItemInInvoice.objects.filter(invoice_id=invoice)
                total_price = sum((item.price * item.quantity) - item.discount_per_item for item in items)
                unpaid = total_price - Decimal(invoice.amount_paid)
                total_unpaid += unpaid if unpaid > 0 else 0

            return Response({
                "status": 200,
                "data": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_amount_paid": float(total_paid),
                    "total_paid_cash": float(total_paid_cash),
                    "total_paid_transfer": float(total_paid_transfer),
                    "total_unpaid": float(total_unpaid)
                }
            })

        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class InvoiceUpdate(generics.UpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        inv_id = self.request.data.get('invoice_id')
        if not inv_id:
            raise serializers.ValidationError({"invoice_id":"Required"})
        return generics.get_object_or_404(Invoice, invoice_id=inv_id)

class InvoiceDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        invoice_id = request.data.get('invoice_id')

        if not invoice_id:
            return Response({"status": 400, "error": "Invoice ID is required."}, status=400)

        try:
            invoice = Invoice.objects.get(invoice_id=invoice_id)
            invoice.delete()
            return Response({"status": 200, "message": "Invoice deleted successfully."}, status=200)
        except Invoice.DoesNotExist:
            return Response({"status": 404, "error": "Invoice not found."}, status=404)

class InvoiceCreate(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = InvoiceSerializer(data=request.data)
        print(request.data)
        # update inventory table based on invoice product id
        # product_in_inventory = Product.objects.get(product_id='Pending')
        # product_in_inventory.product_quantity = product_in_inventory.product_quantity - 1
        # product_in_inventory.save()
        if serializer.is_valid():
            invoice = serializer.save()
            return Response({"status": 201, "data": InvoiceSerializer(invoice).data}, status=201)
        return Response({"status": 400, "error": serializer.errors}, status=400)

class PendingInvoiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            pending_invoices = Invoice.objects.filter(invoice_status='Pending')
            result = []

            for invoice in pending_invoices:
                daily_sales = DailySales.objects.filter(invoice_id=invoice).select_related('employee')

                employee_info_list = []
                for ds in daily_sales:
                    employee = ds.employee
                    employee_info_list.append({
                        'employee_id': employee.employee_id,
                        'employee_name': employee.employee_name,
                        'role': employee.role,
                    })

                total_quantity = ItemInInvoice.objects.filter(invoice_id=invoice).aggregate(
                    total_qty=Sum('quantity')
                )['total_qty'] or 0

                result.append({
                    'invoice_id': invoice.invoice_id,
                    'car_number': invoice.car_number,
                    'employees': employee_info_list,
                    'total_quantity': total_quantity
                })

            return Response({"status": 200, "data": result}, status=200)
        
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class InvoiceDetailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        invoice_id = request.data.get('invoice_id')

        if not invoice_id:
            return Response({"status": 400, "error": "Invoice ID is required."}, status=400)

        try:
            invoice = Invoice.objects.get(invoice_id=invoice_id)

            items = ItemInInvoice.objects.filter(invoice_id=invoice)
            item_list = [{
                'product_id': item.product_id,
                'discount_per_item': float(item.discount_per_item),
                'quantity': item.quantity,
                'price': float(item.price)
            } for item in items]

            sales = DailySales.objects.filter(invoice_id=invoice).select_related('employee')
            sales_list = [{
                'employee_id': sale.employee.employee_id,
                'employee_name': sale.employee.employee_name,
                'role': sale.employee.role,
            } for sale in sales]

            return Response({
                "status": 200,
                "data": {
                    'invoice_id': invoice.invoice_id,
                    'invoice_date': invoice.invoice_date,
                    'amount_paid': float(invoice.amount_paid),
                    'payment_method': invoice.payment_method,
                    'car_number': invoice.car_number,
                    'discount': float(invoice.discount),
                    'invoice_status': invoice.invoice_status,
                    'items': item_list,
                    'sales': sales_list
                }
            })

        except Invoice.DoesNotExist:
            return Response({"status": 404, "error": "Invoice not found."}, status=404)
