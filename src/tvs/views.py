from rest_framework import viewsets
from .models import TVType, TVModel, TV
from .serializers import TvTypeSerializer, TvModelSerializer, TvSerializer
from users.permissions import IsManager, IsReceptionist, IsTechnician, IsManagerOrSelf
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response  # Add this import

class TvTypeViewSet(viewsets.ModelViewSet):
    queryset = TVType.objects.all()
    serializer_class = TvTypeSerializer
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsAuthenticated(), IsManager()]
        else:
            permission_classes = [IsAuthenticated()]
        return permission_classes

class TvModelViewSet(viewsets.ModelViewSet):
    queryset = TVModel.objects.all()
    serializer_class = TvModelSerializer
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsAuthenticated(), IsManager()]
        else:
            permission_classes = [IsAuthenticated()]
        return permission_classes

    def get_queryset(self):
        queryset = TVModel.objects.all()
        type_id = self.request.query_params.get('type_id')
        if type_id is not None:
            queryset = queryset.filter(type__id=type_id)
        return queryset

class TvViewSet(viewsets.ModelViewSet): 
    queryset = TV.objects.all()
    serializer_class = TvSerializer
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsAuthenticated(), IsManager()]
        else:
            permission_classes = [IsAuthenticated()]
        return permission_classes

    def get_queryset(self):
        queryset = TV.objects.all()
        type_id = self.request.query_params.get('type_id')
        model_id = self.request.query_params.get('model_id')
        if type_id is not None:
            queryset = queryset.filter(type_id=type_id)
        if model_id is not None:
            queryset = queryset.filter(model_id=model_id)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTechnician])
    def mark_for_repair(self, request, pk=None):
        tv = self.get_object()
        tv.status = 'REPAIR'
        tv.save()
        return Response({'status': 'TV marked for repair'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsReceptionist])
    def check_in(self, request, pk=None):
        tv = self.get_object()
        tv.status = 'IN_STOCK'
        tv.save()
        return Response({'status': 'TV checked in'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsReceptionist])
    def check_out(self, request, pk=None):
        tv = self.get_object()
        tv.status = 'OUT'
        tv.save()
        return Response({'status': 'TV checked out'})