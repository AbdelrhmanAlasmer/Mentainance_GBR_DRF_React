from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsManager, IsReceptionist
from .serializers import (
    UserSerializer,
    RegisterManagerSerializer,
    RegisterReceptionistSerializer,
    LoginSerializer
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout


def create_user_response(user):
    token, created = Token.objects.get_or_create(user=user)
    return {
        'user': UserSerializer(user).data,
        'token': token.key
    }


@api_view(['POST'])
@permission_classes([IsManager])
def register_manager_view(request):
    serializer = RegisterManagerSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            create_user_response(user),
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])  # Changed to uppercase 'POST'
@permission_classes([IsManager])
def register_receptionist_view(request):
    serializer = RegisterReceptionistSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            create_user_response(user),
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data
    login(request, user)
    return Response(
        create_user_response(user),
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.auth.delete()  # Delete the token
    logout(request)
    return Response(
        {'message': 'Successfully logged out'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsManager])
def manager_dashboard(request):
    return Response({
        'message': 'Welcome Manager',
        'data': {
            'stats': {
                'total_receptionists': request.user.receptionists.count(),
                'active_bookings': 42  # Example data
            },
            'actions': [
                'manage_staff',
                'view_reports',
                'configure_system'
            ]
        }
    })


@api_view(['GET'])
@permission_classes([IsReceptionist])
def receptionist_dashboard(request):  # Renamed from employee_dashboard for consistency
    return Response({
        'message': 'Welcome Receptionist',
        'data': {
            'todays_schedule': {
                'check_ins': 15,
                'check_outs': 10,
                'reservations': 8
            },
            'tasks': [
                'process_check_ins',
                'handle_guest_requests',
                'manage_room_assignments'
            ]
        }
    })