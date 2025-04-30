# tv_management/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TvTypeViewSet, TvModelViewSet, TvViewSet

router = DefaultRouter()
router.register(r'tv-types', TvTypeViewSet, basename='tvtype')
router.register(r'tv-models', TvModelViewSet, basename='tvmodel')
router.register(r'tvs', TvViewSet, basename='tv')

urlpatterns = [
    path('', include(router.urls)),
]


