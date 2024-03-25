from django.urls import path
from .views.read_filtered_city import ReadFilteredCityAPIView
from .views.read_all_city import ReadAllCityAPIView

urlpatterns = [
    path("cities", ReadFilteredCityAPIView.as_view()),
    path("all-citiess", ReadAllCityAPIView.as_view())
]
