from django.urls import path
from .views.read_all_city import ReadAllCityAPIView

urlpatterns = [
    path("cities", ReadAllCityAPIView.as_view())
]
