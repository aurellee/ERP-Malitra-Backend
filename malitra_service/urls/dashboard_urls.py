from django.urls import path
from malitra_service.views.dashboard_views import *

urlpatterns = [
    path("dashboard/", DashboardOverviewView.as_view(), name="dashboard-overview"),
]