from malitra_service.models import ItemInInvoice
from rest_framework import serializers

class ItemInInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemInInvoice
        fields = ['product', 'discount_per_item', 'quantity', 'price']