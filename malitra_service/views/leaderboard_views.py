from rest_framework.views import APIView
from rest_framework.response import Response
from malitra_service.models import DailySales
from django.db.models import Sum

class SalesLeaderboardView(APIView):
    def get(self, request):
        sales_data = DailySales.objects.filter(
            employee__role="Sales"
        ).values(
            "employee__employee_name"
        ).annotate(
            total_omzet=Sum("total_sales_omzet")
        ).order_by("-total_omzet")[:5]  # Top 5

        result = [
            {
                "salesperson": entry["employee__employee_name"],
                "total_omzet": float(entry["total_omzet"] or 0)
            }
            for entry in sales_data
        ]

        return Response({
            "status": 200,
            "data": result
        })