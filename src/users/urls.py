from django.urls import path
from .views import (
    login_view, 
    user_detail_view,
    logout_view,
    manager_dashboard,
    receptionist_dashboard,  
    register_manager_view,
    register_receptionist_view
)

urlpatterns = [
    # Authentication endpoints
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/', user_detail_view, name='user-detail'),
    
    # Registration endpoints (manager-only access)
    path('managers/register/', register_manager_view, name='register-manager'),
    path('receptionists/register/', register_receptionist_view, name='register-receptionist'),
    
    # Role-specific dashboards
    path('dashboard/manager/', manager_dashboard, name='manager-dashboard'),
    path('dashboard/receptionist/', receptionist_dashboard, name='receptionist-dashboard'),  # Updated
]