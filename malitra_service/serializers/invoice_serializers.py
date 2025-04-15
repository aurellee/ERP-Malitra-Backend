from malitra_service.models import Invoice, ItemInInvoice, DailySales
from .dailysales_serializers import DailySalesSerializer
from .itemininvoice_serializers import ItemInInvoiceSerializer
from rest_framework import serializers
from decimal import Decimal

class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemInInvoiceSerializer(many=True, required=False)
    sales = DailySalesSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'invoice_date', 'amount_paid', 'payment_method', 'car_number', 'discount', 'invoice_status', 'items', 'sales']
    
    def validate(self, data):
        # Skip validasi amount_paid jika status Pending
        if data.get('invoice_status', '').lower() == 'pending':
            return data

        items_data = data.get('items', None)
        discount = data.get('discount', 0)

        if items_data is None:
            return data

        total_price = sum(
            (item['price'] - item['discount_per_item']) * item['quantity']
            for item in items_data
        )
        total_amount_due = total_price - discount
        amount_paid = data.get('amount_paid', 0)

        if amount_paid > total_amount_due:
            raise serializers.ValidationError({
                "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
            })

        return data

    def create(self, validated_data):
        from malitra_service.models import Product

        items_data = validated_data.pop('items')
        sales_data = validated_data.pop('sales')
        invoice_status = validated_data.get('invoice_status', '').lower()

        invoice = Invoice.objects.create(**validated_data)

        total_price = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            price = item['price']
            discount_per_item = item['discount_per_item']

            if product.product_quantity < quantity:
                raise serializers.ValidationError({
                    "error": f"Stok produk '{product.product_name}' tidak cukup (tersisa {product.product_quantity})"
                })

            subtotal = (price - discount_per_item) * quantity
            total_price += subtotal

            ItemInInvoice.objects.create(
                invoice=invoice,
                product=product,
                discount_per_item=discount_per_item,
                quantity=quantity,
                price=price,
            )

            product.product_quantity -= quantity
            product.save()

        discount = validated_data.get('discount', 0)
        total_amount_due = total_price - discount
        amount_paid = validated_data.get('amount_paid', 0)

        if invoice_status != 'pending' and amount_paid > total_amount_due:
            raise serializers.ValidationError({
                "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
            })

        for sale in sales_data:
            ds = DailySales.objects.create(invoice=invoice, **sale)

            if invoice_status == 'pending':
                ds.total_sales_omzet = 0
                ds.amount_paid = 0
                ds.salary_status = "Unpaid"
            else:
                ds.total_sales_omzet = amount_paid
                salary_paid = amount_paid * Decimal(0.5)  # Logika dummy
                ds.amount_paid = salary_paid

            ds.save()

        return invoice

    def update(self, instance, validated_data):
        from malitra_service.models import Product

        items_data = validated_data.pop('items', '__not_provided__')
        discount = validated_data.pop('discount', '__not_provided__')
        invoice_status = validated_data.get('invoice_status', instance.invoice_status).lower()

        new_amount_paid = validated_data.get('amount_paid', instance.amount_paid)
        total_price = 0

        if items_data != '__not_provided__':
            for item in items_data:
                subtotal = (item['price'] - item['discount_per_item']) * item['quantity']
                total_price += subtotal
        else:
            for item in ItemInInvoice.objects.filter(invoice=instance):
                subtotal = (item.price - item.discount_per_item) * item.quantity
                total_price += subtotal

        if discount == '__not_provided__':
            discount = instance.discount

        total_amount_due = total_price - discount

        if invoice_status != 'pending' and new_amount_paid > total_amount_due:
            raise serializers.ValidationError({
                "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
            })

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update semua DailySales terkait
        related_sales = DailySales.objects.filter(invoice=instance)

        for sale in related_sales:
            if invoice_status == 'pending':
                sale.total_sales_omzet = 0
                sale.amount_paid = 0
                sale.salary_status = "Unpaid"
            else:
                sale.total_sales_omzet = new_amount_paid
                salary_paid = new_amount_paid * Decimal(0.5)  # Atur sesuai kebijakan
                sale.amount_paid = salary_paid
            sale.save()

        return instance
