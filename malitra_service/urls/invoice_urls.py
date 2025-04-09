from django.urls import path
from malitra_service.views.invoice_views import *

urlpatterns = [
    path("invoice/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoice/summaryFilter/", InvoiceSummaryFilter.as_view(), name="invoice-summary"),
    path("invoice/update/", InvoiceUpdate.as_view(), name="update-invoice"),
    path("invoice/delete/", InvoiceDelete.as_view(), name="delete-invoice"),
    path("invoice/create/", InvoiceCreate.as_view(), name="create-invoice"),
    path("invoice/getPendingInvoiceList/", PendingInvoiceListView.as_view(), name="get-pending-invoice"),
    path("invoice/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
]