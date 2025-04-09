from malitra_service.models import ItemInInvoice
from rest_framework import serializers

class ItemInInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemInInvoice
        fields = ['product_id', 'discount_per_item', 'quantity', 'price']