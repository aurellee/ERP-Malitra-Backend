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
                (it['price'] * it['quantity']) - it['discount_per_item']
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
            (i.price * i.quantity) - i.discount_per_item for i in items
        )
        total_due = total_price - invoice.discount
        # invoice.invoice_status = (
        #     "Full Payment" if invoice.amount_paid >= total_due
        #     else "Partially Paid" if invoice.amount_paid > 0
        #     else "Pending"
        # )
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

        # 1) update the simple invoice fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        # 2) handle items _only_ if provided
        if items_data is not None:
            # build lookup of existing items: { product_id: ItemInInvoice instance }
            existing = {
                item.product.product_id: item
                for item in ItemInInvoice.objects.filter(invoice=instance)
            }
            # track which ones we see anew
            new_ids = set()

            for it in items_data:
                prod = it['product']           # a Product instance
                new_qty = it['quantity']
                new_ids.add(prod.product_id)

                if prod.product_id in existing:
                    # update case
                    old_item = existing[prod.product_id]
                    old_qty = old_item.quantity
                    diff = new_qty - old_qty

                    # adjust stock only by the difference
                    if diff:
                        if diff > 0 and prod.product_quantity < diff:
                            raise serializers.ValidationError({
                                "items": f"Not enough stock for {prod.product_name} (need {diff})."
                            })
                        prod.product_quantity -= diff
                        prod.save()

                    # update the item record
                    old_item.quantity            = new_qty
                    old_item.price               = it['price']
                    old_item.discount_per_item   = it['discount_per_item']
                    old_item.save()

                else:
                    # brand-new item: subtract full qty
                    if prod.product_quantity < new_qty:
                        raise serializers.ValidationError({
                            "items": f"Not enough stock for {prod.product_name} (only {prod.product_quantity})."
                        })
                    prod.product_quantity -= new_qty
                    prod.save()
                    ItemInInvoice.objects.create(
                        invoice=instance,
                        product=prod,
                        quantity=new_qty,
                        price=it['price'],
                        discount_per_item=it['discount_per_item'],
                    )

            # 3) any existing items *not* in the new list must be removed & stock restored
            for pid, old_item in existing.items():
                if pid not in new_ids:
                    prod = old_item.product
                    prod.product_quantity += old_item.quantity
                    prod.save()
                    old_item.delete()

        # 3) Replace sales if provided
        if sales_data is not None:
            for sale in sales_data:
                # find the existing row (assumes one per employee/invoice)
                ds_qs = DailySales.objects.filter(invoice=instance, employee_id=sale['employee'])

                if ds_qs.count() > 1:
                    raise serializers.ValidationError({
                        "sales": f"Multiple DailySales entries found for employee {sale['employee']} and invoice {instance.invoice_id}."
                    })

                if ds_qs.exists():
                    ds = ds_qs.first()
                else:
                    ds = DailySales(invoice=instance, employee_id=sale['employee'])

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
