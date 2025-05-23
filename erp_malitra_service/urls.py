"""
URL configuration for erp_malitra_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from malitra_service.views.user_views import CreateUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin & Auth
    path('admin/', admin.site.urls),
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    
    # Include modular URLs
    path("", include("malitra_service.urls.dashboard_urls")),
    path("", include("malitra_service.urls.ekspedisi_masuk_urls")),
    path("", include("malitra_service.urls.employee_urls")),
    path("", include("malitra_service.urls.invoice_urls")),
    path("", include("malitra_service.urls.product_urls")),
]