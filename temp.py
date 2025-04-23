# class InvoiceUpdate(generics.UpdateAPIView):
#     serializer_class = InvoiceSerializer
#     permission_classes = [AllowAny] 

#     def get_object(self):
#         invoice_id = self.request.data.get('invoice_id')

#         if not invoice_id:
#             raise serializers.ValidationError({"status": 400, "error": {"invoice_id": "This field is required."}})

#         try:
#             return Invoice.objects.get(invoice_id=invoice_id)
#         except Invoice.DoesNotExist:
#             raise serializers.ValidationError({"status": 404, "error": {"invoice_id": "Invoice not found."}})
    
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)  # ✅ partial update
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer, request.data)  # Pass the request data to the custom update logic
        
#         return Response(serializer.data)
    
#     def perform_update(self, serializer, request_data):
#         instance = serializer.save()

#         # Update 'amount_paid'
#         new_amount_paid = request_data.get('amount_paid', instance.amount_paid)
#         instance.amount_paid = new_amount_paid
        
#         # Update items if provided in the request
#         items_data = request_data.get('items', [])
#         if items_data:
#             self.update_items(instance, items_data)
        
#         # Calculate total price after discount for the new items and update the invoice status
#         self.calculate_total_and_update_status(instance)

#         # Update daily sales omzet
#         DailySales.objects.filter(invoice_id=instance).update(total_sales_omzet=instance.amount_paid)

#     def update_items(self, invoice_instance, items_data):
#         total_price = 0
#         # Dapatkan daftar item yang sudah ada
#         existing_items = {item.product.product_id: item for item in ItemInInvoice.objects.filter(invoice_id=invoice_instance)}
        
#         for item in items_data:
#             try:
#                 product = Product.objects.get(product_id=item.get('product'))  # Ganti dengan metode pencarian sesuai dengan format data
#             except Product.DoesNotExist:
#                 raise serializers.ValidationError({
#                     "error": f"Produk dengan ID '{item.get('product')}' tidak ditemukan."
#                 })
#             quantity = item.get('quantity')
#             price = Decimal(item.get('price'))
#             discount_per_item = Decimal(item.get('discount_per_item'))

#             # Jika produk sudah ada di invoice, update quantity
#             if product.product_id in existing_items:
#                 existing_item = existing_items[product.product_id]
#                 old_quantity = existing_item.quantity
#                 quantity_difference = quantity - old_quantity
                
#                 # Update stok produk berdasarkan perbedaan quantity
#                 product.product_quantity -= quantity_difference
#                 product.save()

#                 # Update item di invoice
#                 existing_item.quantity = quantity
#                 existing_item.price = price
#                 existing_item.discount_per_item = discount_per_item
#                 existing_item.save()
#             else:
#                 # Jika produk baru ditambahkan, kurangi stok produk
#                 if product.product_quantity < quantity:
#                     raise serializers.ValidationError({
#                         "error": f"Stok produk '{product.product_name}' tidak cukup (tersisa {product.product_quantity})"
#                     })
                
#                 product.product_quantity -= quantity
#                 product.save()

#                 # Tambahkan item baru ke invoice
#                 ItemInInvoice.objects.create(
#                     invoice=invoice_instance,
#                     product=product,
#                     quantity=quantity,
#                     price=price,
#                     discount_per_item=discount_per_item
#                 )

#             # Hitung subtotal harga item setelah diskon
#             total_price += (price - discount_per_item) * quantity

#         # Update total price setelah diskon
#         discount = invoice_instance.discount
#         invoice_instance.save()

#     def calculate_total_and_update_status(self, invoice_instance):
#         # Hitung total harga produk setelah diskon
#         items = ItemInInvoice.objects.filter(invoice_id=invoice_instance)
#         total = sum(
#             (item.price - item.discount_per_item) * item.quantity
#             for item in items
#         )

#         # Cek apakah amount_paid sudah mencukupi untuk full payment
#         if invoice_instance.amount_paid >= total:
#             invoice_instance.invoice_status = "Full Payment"
#         else:
#             invoice_instance.invoice_status = "Partial Payment" if invoice_instance.amount_paid > 0 else "Pending"

#         invoice_instance.save()




# class InvoiceSerializer(serializers.ModelSerializer):
#     items = ItemInInvoiceSerializer(many=True, required=False)
#     sales = DailySalesSerializer(many=True, required=False)

#     class Meta:
#         model = Invoice
#         fields = ['invoice_id', 'invoice_date', 'amount_paid', 'payment_method', 'car_number', 'discount', 'invoice_status', 'items', 'sales']
    
#     def validate(self, data):
#         # Skip validasi amount_paid jika status Pending
#         if data.get('invoice_status', '').lower() == 'pending':
#             return data

#         items_data = data.get('items', None)
#         discount = data.get('discount', 0)

#         if items_data is None:
#             return data

#         total_price = sum(
#             (item['price'] - item['discount_per_item']) * item['quantity']
#             for item in items_data
#         )
#         total_amount_due = total_price - discount
#         amount_paid = data.get('amount_paid', 0)

#         if amount_paid > total_amount_due:
#             raise serializers.ValidationError({
#                 "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
#             })

#         return data

#     def create(self, validated_data):
#         from malitra_service.models import Product

#         items_data = validated_data.pop('items')
#         sales_data = validated_data.pop('sales')
#         invoice_status = validated_data.get('invoice_status', '').lower()

#         invoice = Invoice.objects.create(**validated_data)

#         total_price = 0
#         for item in items_data:
#             product = item['product']
#             quantity = item['quantity']
#             price = item['price']
#             discount_per_item = item['discount_per_item']

#             if product.product_quantity < quantity:
#                 raise serializers.ValidationError({
#                     "error": f"Stok produk '{product.product_name}' tidak cukup (tersisa {product.product_quantity})"
#                 })

#             subtotal = (price - discount_per_item) * quantity
#             total_price += subtotal

#             ItemInInvoice.objects.create(
#                 invoice=invoice,
#                 product=product,
#                 discount_per_item=discount_per_item,
#                 quantity=quantity,
#                 price=price,
#             )

#             product.product_quantity -= quantity
#             product.save()

#         discount = validated_data.get('discount', 0)
#         total_amount_due = total_price - discount
#         amount_paid = validated_data.get('amount_paid', 0)

#         if invoice_status != 'pending' and amount_paid > total_amount_due:
#             raise serializers.ValidationError({
#                 "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
#             })

#         for sale in sales_data:
#             ds = DailySales.objects.create(invoice=invoice, **sale)

#             if invoice_status == 'pending':
#                 ds.total_sales_omzet = 0
#                 ds.amount_paid = 0
#                 ds.salary_status = "Unpaid"
#             else:
#                 ds.total_sales_omzet = amount_paid
#                 salary_paid = amount_paid * Decimal(0.5)  # Logika dummy
#                 ds.amount_paid = salary_paid

#             ds.save()

#         return invoice

#     def update(self, instance, validated_data):
#         from malitra_service.models import Product

#         items_data = validated_data.pop('items', '__not_provided__')
#         discount = validated_data.pop('discount', '__not_provided__')
#         invoice_status = validated_data.get('invoice_status', instance.invoice_status).lower()

#         new_amount_paid = validated_data.get('amount_paid', instance.amount_paid)
#         total_price = 0

#         if items_data != '__not_provided__':
#             for item in items_data:
#                 subtotal = (item['price'] - item['discount_per_item']) * item['quantity']
#                 total_price += subtotal
#         else:
#             for item in ItemInInvoice.objects.filter(invoice=instance):
#                 subtotal = (item.price - item.discount_per_item) * item.quantity
#                 total_price += subtotal

#         if discount == '__not_provided__':
#             discount = instance.discount

#         total_amount_due = total_price - discount

#         if invoice_status != 'pending' and new_amount_paid > total_amount_due:
#             raise serializers.ValidationError({
#                 "error": f"Jumlah yang dibayar (amount_paid) tidak boleh lebih besar dari total harga yang harus dibayar ({total_amount_due})."
#             })

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         # Update semua DailySales terkait
#         related_sales = DailySales.objects.filter(invoice=instance)

#         for sale in related_sales:
#             if invoice_status == 'pending':
#                 sale.total_sales_omzet = 0
#                 sale.amount_paid = 0
#                 sale.salary_status = "Unpaid"
#             else:
#                 sale.total_sales_omzet = new_amount_paid
#                 salary_paid = new_amount_paid * Decimal(0.5)  # Atur sesuai kebijakan
#                 sale.amount_paid = salary_paid
#             sale.save()

#         return instance