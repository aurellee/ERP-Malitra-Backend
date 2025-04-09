from rest_framework import serializers
from malitra_service.models import Product

class ProductSerializer(serializers.ModelSerializer):
    def validate_product_id(self, value):
        if self.instance is None and Product.objects.filter(product_id=value).exists():
            raise serializers.ValidationError("Product ID already exists.")
        return value

    class Meta:
        model = Product
        fields = ['product_id', 'product_name', 'product_quantity', 'category', 'brand_name']