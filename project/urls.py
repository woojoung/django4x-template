"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from rest_framework import routers
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from library import sql, aws
from api.views import AppleLoginView, GoogleLoginView, SignupView
from api.viewsets import UserViewSet, FamilyViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'family', FamilyViewSet, basename='family')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('aws/pre_signed_url/', aws.S3View.as_view(), name='aws_pre_signed_url'),

    path('v1/api/', include(router.urls)),
    path('v1/sql/', sql.View.as_view(), name='sql'),

    path('v1/api/signup/', SignupView.as_view(), name='api_signup'),

    path('v1/api/apple/login/', AppleLoginView.as_view(), name='api_apple_login'),
    path('v1/api/google/login/', GoogleLoginView.as_view(), name='api_google_login'),

    path('v1/api/token/verify/', TokenVerifyView.as_view(), name='api_token_verify'),
    path('v1/api/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
]
