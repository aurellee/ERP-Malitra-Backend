from rest_framework import generics, status
from rest_framework.views import APIView
from malitra_service.serializers.invoice_serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import Invoice, ItemInInvoice, DailySales, Employee
from rest_framework.response import Response
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from datetime import datetime

# Create your views here.
class InvoiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            invoices = Invoice.objects.all()
            result = []

            for invoice in invoices:
                items = ItemInInvoice.objects.filter(invoice_id=invoice)

                total_price = sum((item.price - item.discount) * item.quantity for item in items)

                unpaid_amount = total_price - float(invoice.amount_paid)

                invoice_data = {
                    'invoice_id': invoice.invoice_id,
                    'invoice_date': invoice.invoice_date,
                    'total_price': total_price,
                    'amount_paid': float(invoice.amount_paid),
                    'unpaid_amount': unpaid_amount,
                    'payment_status': invoice.payment_status,
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
                total_price = sum((item.price - item.discount_per_item) * item.quantity for item in items)
                unpaid = total_price - float(invoice.amount_paid)
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
    serializer_class = InvoiceSerializer
    permission_classes = [AllowAny] 

    def get_object(self):
        invoice_id = self.request.data.get('invoice_id')

        if not invoice_id:
            raise serializers.ValidationError({"status": 400, "error": {"invoice_id": "This field is required."}})

        try:
            return Invoice.objects.get(invoice_id=invoice_id)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"status": 404, "error": {"invoice_id": "Invoice not found."}})

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
    def post(self, request, *args, **kwargs):
        serializer = InvoiceSerializer(data=request.data)
        
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
                daily_sales = DailySales.objects.filter(invoice_id=invoice).select_related('employee_id')

                employee_info_list = []
                for ds in daily_sales:
                    employee = ds.employee_id
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
    def post(self, request, *args, **kwargs):
        invoice_id = request.data.get('invoice_id')

        if not invoice_id:
            return Response({"status": 400, "error": "Invoice ID is required."}, status=400)

        try:
            invoice = Invoice.objects.get(invoice_id=invoice_id)

            items = ItemInInvoice.objects.filter(invoice_id=invoice)
            item_list = [{
                'product_id': item.product_id.product_id,
                'discount_per_item': float(item.discount_per_item),
                'quantity': item.quantity,
                'price': float(item.price)
            } for item in items]

            sales = DailySales.objects.filter(invoice_id=invoice).select_related('employee_id')
            sales_list = [{
                'employee_id': sale.employee_id.employee_id,
                'employee_name': sale.employee_id.employee_name,
                'role': sale.employee_id.role,
            } for sale in sales]

            return Response({
                "status": 200,
                "data": {
                    'invoice_id': invoice.invoice_id,
                    'invoice_date': invoice.invoice_date,
                    'amount_paid': float(invoice.amount_paid),
                    'payment_status': invoice.payment_status,
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
