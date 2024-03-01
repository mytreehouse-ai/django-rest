"""
URL configuration for mytreehouse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
import os
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Mytreehouse API",
        default_version='v1.0.0',
        description="Comprehensive ERP API for seamless integration and AI adoption",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="gelo.sulit@kmcmaggroup.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=os.environ.get('DJANGO_API_URL'),
)

admin.site.site_header = "Mytreehouse Admin"
admin.site.site_title = "Mytreehouse Admin Portal"
admin.site.index_title = "Welcome to Mytreehouse Admin Portal"

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    re_path(
        r'^swagger/$',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0
        ),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui(
            'redoc',
            cache_timeout=0
        ),
        name='schema-redoc'
    ),
    path(
        'token',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'scrapy-jobs/',
        include('scraper_api.urls')
    ),
    # path('ml/', include("open_ai.urls"))
]
