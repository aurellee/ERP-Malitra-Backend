# from django.core.management.base import BaseCommand
# from erp_malitra_service.malitra_service.rag.utlis import rebuild_vectorstore_from_documents
# from malitra_service.models import Invoice, ItemInInvoice, DailySales
# from langchain_core.documents import Document

# class Command(BaseCommand):
#     help = "Rebuild vector database from all invoices."

#     def handle(self, *args, **kwargs):
#         documents = []
#         for invoice in Invoice.objects.all():
#             # Fetch Items
#             items = ItemInInvoice.objects.filter(invoice=invoice)
#             items_detail = "\n".join(
#                 f"- {item.product.product_name} (Qty: {item.quantity}, Price: {item.price}, Discount: {item.discount_per_item})"
#                 for item in items
#             ) or "No items"

#             # Fetch Sales
#             sales = DailySales.objects.filter(invoice=invoice)
#             sales_detail = "\n".join(
#                 f"- {s.employee.employee_name} ({s.employee.role})"
#                 for s in sales
#             ) or "No sales"

#             doc = Document(
#                 page_content=f"""
#                 Invoice ID: {invoice.invoice_id}
#                 Car Number: {invoice.car_number}
#                 Invoice Date: {invoice.invoice_date}
#                 Payment Method: {invoice.payment_method}
#                 Amount Paid: {invoice.amount_paid}
#                 Discount: {invoice.discount}
#                 Invoice Status: {invoice.invoice_status}

#                 Items Purchased:
#                 {items_detail}

#                 Handled By:
#                 {sales_detail}
#                 """.strip(),
#                 metadata={"type": "invoice", "invoice_id": str(invoice.invoice_id)}
#             )
#             documents.append(doc)
        
#         rebuild_vectorstore_from_documents(documents)
#         self.stdout.write(self.style.SUCCESS('Successfully rebuilt the vector database!'))