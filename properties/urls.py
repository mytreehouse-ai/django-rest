from django.urls import path
from .views.read_all_public_property_listing import ReadAllPublicPropertyListingAPIView
from .views.read_one_public_property_listing import ReadOnePublicPropertyListingAPIView

urlpatterns = [
    path("public", ReadAllPublicPropertyListingAPIView.as_view()),
    path("public/<str:listing_url>", ReadOnePublicPropertyListingAPIView.as_view())
]
