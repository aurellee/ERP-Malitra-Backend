from django.urls import path
from malitra_service.views.ekspedisi_masuk_views import *

urlpatterns = [
    path("ekspedisi/", EkspedisiMasukListView.as_view(), name="ekspedisi-list"),
    path("ekspedisi/create/", EkspedisiMasukCreate.as_view(), name="create-ekspedisi"),
    path("ekspedisi/firstCreate/", EkspedisiMasukFirstCreate.as_view(), name="create-first-ekspedisi"),
    path("ekspedisi/delete/", EkspedisiMasukDelete.as_view(), name="delete-ekspedisi"),
    path("ekspedisi/update/", EkspedisiMasukUpdate.as_view(), name="update-ekspedisi"),
]