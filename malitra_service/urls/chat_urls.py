from django.urls import path
from malitra_service.views.chat_views import *

urlpatterns = [
    path("chat/sendQuestion/", ChatView.as_view(), name="send-question"),
    path("chat/listAllChat/", ChatListView.as_view(), name="list-all-chat"),
]