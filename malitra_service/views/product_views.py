from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from malitra_service.serializers.product_serializers import ProductSerializer
from rest_framework.permissions import AllowAny
from malitra_service.models import Product, EkspedisiMasuk
from rest_framework.response import Response

class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response({"status": 200, "data": serializer.data}, status=200)
        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)

class ProductCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({"status": 201, "data": ProductSerializer(product).data}, status=201)
        else:
            return Response({"status": 400, "error": serializer.errors}, status=400)

class ProductDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"status": 400, "error": "Product ID is required."}, status=400)

        try:
            product = Product.objects.get(product_id=product_id)
            product.delete()
            return Response({"status": 200, "message": "Product deleted successfully."}, status=200)
        except Product.DoesNotExist:
            return Response({"status": 404, "error": "Product not found."}, status=404)

class ProductUpdate(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] 

    def get_object(self):
        product_id = self.request.data.get('product_id')

        if not product_id:
            raise serializers.ValidationError({"status": 400, "error": {"product_id": "This field is required."}})

        try:
            return Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"status": 404, "error": {"product_id": "Product not found."}})

class ProductExist(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"status": 400, "error": "Product ID is required."}, status=400)

        exists = Product.objects.filter(product_id=product_id).exists()
        return Response({"status": 200, "data": {"exists": exists}}, status=200)

class ProductListWithLatestPrices(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.all()
            result = []

            for product in products:
                latest_ekspedisi = EkspedisiMasuk.objects.filter(product_id=product).order_by("-date").first()
                product_data = ProductSerializer(product).data

                if latest_ekspedisi:
                    product_data['purchase_price'] = latest_ekspedisi.purchase_price
                    product_data['sale_price'] = latest_ekspedisi.sale_price
                    product_data['ekspedisi_date'] = latest_ekspedisi.date
                else:
                    product_data['purchase_price'] = None
                    product_data['sale_price'] = None
                    product_data['ekspedisi_date'] = None

                result.append(product_data)

            return Response({"status": 200, "data": result}, status=200)

        except Exception as e:
            return Response({"status": 500, "error": str(e)}, status=500)
