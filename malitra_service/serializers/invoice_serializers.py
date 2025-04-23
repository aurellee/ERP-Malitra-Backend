from malitra_service.models import Invoice, ItemInInvoice, DailySales
from .dailysales_serializers import DailySalesSerializer
from .itemininvoice_serializers import ItemInInvoiceSerializer
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction

class InvoiceSerializer(serializers.ModelSerializer):
    items = ItemInInvoiceSerializer(many=True, required=False)
    sales = DailySalesSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'invoice_id', 'invoice_date',
            'amount_paid', 'payment_method','car_number',
            'discount', 'invoice_status', 'items', 'sales'
        ]
        read_only_fields = ['invoice_date']

    def validate(self, data):
        # If status is pending, skip amount_paid check
        if data.get('invoice_status', '').lower() == 'pending':
            return data

        items = data.get('items')
        discount = data.get('discount', 0)
        amount_paid = data.get('amount_paid', 0)

        if items:
            total = sum(
                (it['price'] - it['discount_per_item']) * it['quantity']
                for it in items
            ) - discount
            if amount_paid > total:
                raise serializers.ValidationError({
                    "amount_paid": f"cannot exceed total due ({total})."
                })
        return data

    def _recalculate_totals(self, invoice):
        """Recompute total_price, invoice_status, and return total_due."""
        items = ItemInInvoice.objects.filter(invoice=invoice)
        total_price = sum(
            (i.price - i.discount_per_item) * i.quantity for i in items
        )
        total_due = total_price - invoice.discount
        invoice.invoice_status = (
            "Full Payment" if invoice.amount_paid >= total_due
            else "Partially Paid" if invoice.amount_paid > 0
            else "Pending"
        )
        invoice.save()
        return total_due

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        sales_data = validated_data.pop('sales', [])
        invoice = super().create(validated_data)

        # Items
        for it in items_data:
            prod = it['product']
            qty  = it['quantity']
            if prod.product_quantity < qty:
                raise serializers.ValidationError(
                    {"items": f"Not enough stock for {prod.product_name}."}
                )
            prod.product_quantity -= qty
            prod.save()
            ItemInInvoice.objects.create(invoice=invoice, **it)

        # Sales
        for sale in sales_data:
            ds = DailySales.objects.create(invoice=invoice, **sale)
            # dummy logic; adjust as needed
            ds.total_sales_omzet = invoice.amount_paid if invoice.invoice_status!='pending' else 0
            amount_paid = ds.total_sales_omzet * Decimal('0.1') if invoice.invoice_status!='pending' else 0
            ds.salary_status = "Paid" if ds.salary_paid == amount_paid else "Unpaid"
            ds.save()

        # Finalize status
        self._recalculate_totals(invoice)
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        sales_data = validated_data.pop('sales', None)

        # 1) Update simple fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # 2) Replace items if provided
        if items_data is not None:
            # restore stock from old items
            for old in ItemInInvoice.objects.filter(invoice=instance):
                p = old.product
                p.product_quantity += old.quantity
                p.save()
            ItemInInvoice.objects.filter(invoice=instance).delete()

            # create new items
            for it in items_data:
                prod = it['product']
                qty  = it['quantity']
                if prod.product_quantity < qty:
                    raise serializers.ValidationError(
                        {"items": f"Not enough stock for {prod.product_name}."}
                    )
                prod.product_quantity -= qty
                prod.save()
                ItemInInvoice.objects.create(invoice=instance, **it)

        # 3) Replace sales if provided
        if sales_data is not None:
            for sale in sales_data:
                # find the existing row (assumes one per employee/invoice)
                ds = DailySales.objects.get(
                    invoice=instance,
                    employee_id=sale['employee']
                )

                # 1) overwrite the omzet
                ds.total_sales_omzet = Decimal(sale['total_sales_omzet'])

                # 2) recompute expected & remaining
                expected   = (ds.total_sales_omzet * Decimal("0.10")) \
                                 .quantize(Decimal("0.01"))
                paid_old   = ds.salary_paid or Decimal("0")
                remaining  = expected - paid_old

                ds.salary_status = "Fully Paid" if ds.salary_paid >= expected else "Unpaid"
                ds.save()

        # 4) Recalc invoice status & totals
        self._recalculate_totals(instance)
        return instance
