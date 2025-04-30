# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReceptionViewSet, CallViewSet, RepairNoteViewSet

router = DefaultRouter()
router.register(r'receptions', ReceptionViewSet, basename='reception')
router.register(r'calls', CallViewSet, basename='call')
router.register(r'repair-notes', RepairNoteViewSet, basename='repair-note')

urlpatterns = [
    path('', include(router.urls)),
]