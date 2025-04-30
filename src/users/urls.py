from django.urls import path
from .views import (
    register_user_view,
    login_view,
    logout_view,
    user_detail_view,
    update_profile_view,
    change_password_view,
    user_list_view,
    user_manage_view,
    toggle_user_active_view,
    manager_dashboard,
    receptionist_dashboard,
    technician_dashboard
)

urlpatterns = [
    # Authentication
    path('register/', register_user_view, name='register-user'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Profile management
    path('profile/', user_detail_view, name='user-detail'),
    path('profile/update/', update_profile_view, name='update-profile'),
    path('profile/change-password/', change_password_view, name='change-password'),

    # User management (manager only)
    path('users/', user_list_view, name='user-list'),
    path('users/<int:pk>/', user_manage_view, name='user-manage'),
    path('users/<int:pk>/toggle-active/', toggle_user_active_view, name='toggle-user-active'),

    # Role-specific dashboards
    path('dashboard/manager/', manager_dashboard, name='manager-dashboard'),
    path('dashboard/receptionist/', receptionist_dashboard, name='receptionist-dashboard'),
    path('dashboard/technician/', technician_dashboard, name='technician-dashboard'),
]