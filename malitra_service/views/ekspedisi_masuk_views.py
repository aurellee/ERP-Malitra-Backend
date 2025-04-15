from rest_framework import generics
from rest_framework.views import APIView
from malitra_service.serializers.ekspedisi_masuk_serializers import EkspedisiMasukSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from malitra_service.models import EkspedisiMasuk, Product
from rest_framework.response import Response
from rest_framework import serializers

# Create your views here.
class EkspedisiMasukListView(generics.ListAPIView):
    serializer_class = EkspedisiMasukSerializer
    permission_classes = [AllowAny]
    queryset = EkspedisiMasuk.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": 200,
            "data": serializer.data
        })

class EkspedisiMasukCreate(generics.ListCreateAPIView):
    serializer_class = EkspedisiMasukSerializer
    permission_classes = [AllowAny]
    queryset = EkspedisiMasuk.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ekspedisi = serializer.save()
            try:
                product = Product.objects.get(product_id=ekspedisi.product.product_id)  # product_id untuk objek Product
            except Product.DoesNotExist:
                return Response({
                    "status": 400,
                    "error": "Product not found"
                }, status=400)

            if ekspedisi.in_or_out:
                product.product_quantity += ekspedisi.quantity
            else:
                product.product_quantity -= ekspedisi.quantity

            product.save()
            return Response({
                "status": 201,
                "data": serializer.data
            }, status=201)
        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)

class EkspedisiMasukFirstCreate(generics.ListCreateAPIView):
    serializer_class = EkspedisiMasukSerializer
    permission_classes = [AllowAny]
    queryset = EkspedisiMasuk.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": 201,
                "data": serializer.data
            }, status=201)
        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)

class EkspedisiMasukDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        ekspedisi_id = request.data.get('ekspedisi_id')

        if not ekspedisi_id:
            return Response({"status": 400, "error": "Ekspedisi ID is required."}, status=400)

        try:
            ekspedisi = EkspedisiMasuk.objects.get(ekspedisi_id=ekspedisi_id)
            ekspedisi.delete()
            return Response({"status": 200, "message": "Ekspedisi Masuk deleted successfully."}, status=200)
        except EkspedisiMasuk.DoesNotExist:
            return Response({"status": 404, "error": "Ekspedisi Masuk not found."}, status=404)

class EkspedisiMasukUpdate(generics.UpdateAPIView):
    serializer_class = EkspedisiMasukSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        ekspedisi_id = self.request.data.get('ekspedisi_id')

        if not ekspedisi_id:
            raise serializers.ValidationError({"ekspedisi_id": "This field is required."})

        try:
            return EkspedisiMasuk.objects.get(ekspedisi_id=ekspedisi_id)
        except EkspedisiMasuk.DoesNotExist:
            raise serializers.ValidationError({"ekspedisi_id": "Ekspedisi Masuk not found."})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": 200,
                "data": serializer.data
            })
        return Response({
            "status": 400,
            "errors": serializer.errors
        }, status=400)
