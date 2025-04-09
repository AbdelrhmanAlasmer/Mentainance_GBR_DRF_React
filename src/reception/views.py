from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Reception, Call, RepairNote
from .serializers import (
    ReceptionCreateSerializer,
    ReceptionDetailSerializer,
    InspectionSerializer,
    InspectionFeedbackSerializer,
    RefusalSerializer,
    MaintenanceSerializer,
    ReadyForPickupSerializer,
    DeliverySerializer,
    CallSerializer,
    RepairNoteSerializer
)
from django.shortcuts import get_object_or_404

class ReceptionViewSet(viewsets.ModelViewSet):
    queryset = Reception.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReceptionCreateSerializer
        return ReceptionDetailSerializer

    def perform_create(self, serializer):
        serializer.save(receptionist=self.request.user)

    @action(detail=True, methods=['post'])
    def start_inspection(self, request, pk=None):
        reception = self.get_object()
        serializer = InspectionSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        reception = self.get_object()
        serializer = InspectionFeedbackSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refuse_repair(self, request, pk=None):
        reception = self.get_object()
        serializer = RefusalSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_maintenance(self, request, pk=None):
        reception = self.get_object()
        serializer = MaintenanceSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def ready_for_pickup(self, request, pk=None):
        reception = self.get_object()
        serializer = ReadyForPickupSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete_delivery(self, request, pk=None):
        reception = self.get_object()
        serializer = DeliverySerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(reception, serializer.validated_data)
            return Response(
                ReceptionDetailSerializer(reception).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        reception = self.get_object()
        # Implement status history logic if needed
        return Response({}, status=status.HTTP_200_OK)


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        reception_id = self.request.query_params.get('reception_id')
        if reception_id:
            return self.queryset.filter(reception_id=reception_id)
        return self.queryset.none()

    def perform_create(self, serializer):
        reception_id = self.request.data.get('reception')
        reception = get_object_or_404(Reception, pk=reception_id)
        serializer.save(caller=self.request.user, reception=reception)


class RepairNoteViewSet(viewsets.ModelViewSet):
    queryset = RepairNote.objects.all()
    serializer_class = RepairNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        reception_id = self.request.query_params.get('reception_id')
        if reception_id:
            return self.queryset.filter(reception_id=reception_id)
        return self.queryset.none()

    def perform_create(self, serializer):
        reception_id = self.request.data.get('reception')
        reception = get_object_or_404(Reception, pk=reception_id)
        serializer.save(author=self.request.user, reception=reception)