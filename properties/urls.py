from django.urls import path
from .views.read_public_property_listing import ReadPublicPropertyListingAPIView

urlpatterns = [
    path("public", ReadPublicPropertyListingAPIView.as_view())
]
