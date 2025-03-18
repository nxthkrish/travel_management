from django.urls import path
from . import views

urlpatterns = [
    path('admin-create/', views.create_admin, name='create_admin'),
    path('login/', views.login, name='login'),
    path('add-user/', views.add_user, name='add_user'),


    path('travel-requests/', views.get_employee_travel_requests, name='get_employee_travel_requests'),
    path('create-travel-request/', views.create_travel_request, name='create_travel_request'),
    path('cancel-travel-request/<int:request_id>/', views.cancel_travel_request, name='cancel_travel_request'),
    path('update-travel-request/<int:request_id>/', views.update_travel_request, name='update_travel_request'),
    
    path('manager/travel-requests/', views.get_managed_employee_travel_requests, name='get_managed_employee_travel_requests'),
    path('manager/employee/<int:employee_id>/travel-requests/', views.manage_employee_travel_requests, name='manage_employee_travel_requests'),
   
    path('admin-update-user-status/<int:user_id>/', views.update_user_status, name='update_user_status'),
    path('admin-travel-requests/', views.admin_manage_travel_requests, name='admin_manage_travel_requests'),
    path('admin-travel-requests/<int:request_id>/', views.admin_manage_travel_requests, name='admin_manage_travel_request'),
    path('admin-request-email/<int:request_id>/', views.admin_request_email, name='admin_request_email'),
]