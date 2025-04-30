from django.shortcuts import render
from rest_framework import viewsets, permissions
from users.permissions import IsManager
from .serializers import CustomerSerializer
from .models import Customer



class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action in ['destroy']:
            self.permission_classes = [IsManager]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()