from django.urls import path, include
from rest_framework import routers
from .views import CustomerViewSet


routers=routers.DefaultRouter()
routers.register(r'customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('', include(routers.urls)),  
]
