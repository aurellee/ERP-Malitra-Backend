from rest_framework import serializers
from malitra_service.models import EkspedisiMasuk

class EkspedisiMasukSerializer(serializers.ModelSerializer):
    def validate_ekspedisi_id(self, value):
        if self.instance is None and EkspedisiMasuk.objects.filter(ekspedisi_id=value).exists():
            raise serializers.ValidationError("Ekspedisi ID already exists.")
        return value

    class Meta:
        model = EkspedisiMasuk
        fields = ['ekspedisi_id', 'product', 'date', 'quantity', 'purchase_price', 'sale_price', 'in_or_out']