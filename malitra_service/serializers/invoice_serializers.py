from malitra_service.models import Invoice, ItemInInvoice, DailySales
from .dailysales_serializers import DailySalesSerializer
from .itemininvoice_serializers import ItemInInvoiceSerializer
from rest_framework import serializers

class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemInInvoiceSerializer(many=True)
    sales = DailySalesSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'invoice_date', 'amount_paid', 'payment_status', 'payment_method', 'car_number', 'discount', 'invoice_status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sales_data = validated_data.pop('sales')

        invoice = Invoice.objects.create(**validated_data)

        for item in items_data:
            ItemInInvoice.objects.create(**validated_data)
        
        for sale in sales_data:
            DailySales.objects.create(**validated_data)
        
        return invoice
