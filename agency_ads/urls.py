from django.urls import path
from .views import AddImpressionAPIView

urlpatterns = [
    path("record-impression/", AddImpressionAPIView.as_view(), name="add_impression"),
]
