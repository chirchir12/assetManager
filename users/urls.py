from django.urls import path
from django.urls import re_path
from .views import (
    registerEmployer, 
    createEmployee_view,
    employer_dashboard_view,
    account_activation_sent,
    activate,
    employer_login_view,
    logout_employer_view,
    index_view,
    employee_dashboard_view,
    Employee_Update_pass_view,
    employees_List_view,
    assets_List_view,
    addAndAssignAssetView,
    assigned_assets,
    update_profile_view,
    UpdateRole,
    UserProfileDetailView,
    DeleteEmployee,
    notifications
    

    
    ) 

urlpatterns = [
    
    path('', index_view, name='home'),
    path('users/register/', registerEmployer, name='signup'),
    path('users/register/employee', createEmployee_view, name='createEmployee'),
    path('users/employee/create-password', Employee_Update_pass_view, name='createpassword'),
    path('users/login/', employer_login_view, name='login'),
    path('users/account_activation_sent/', account_activation_sent, name='account_activation_sent'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',activate, name='activate'),
    path('users/employer/dashboard/', employer_dashboard_view, name='employerdashboard'),
    path('users/employee/dashboard/', employee_dashboard_view, name='employeedashboard'),
    path('users/logout/', logout_employer_view, name='logout'),

    path('users/dashboard/employees/', employees_List_view, name='employeeList'),
    path('users/dashboard/assets/', assets_List_view, name='assetsList'),
    path('users/dashboard/add-asset/', addAndAssignAssetView, name='addAsset'),
    path('users/dashboard/<int:pk>/update-role/', UpdateRole.as_view(), name="update_role"),
    path('users/dashboard/<int:pk>/delete-employee/', DeleteEmployee.as_view(), name="delete_employee"),

    path('users/dashboard/my-assets/', assigned_assets, name='myassets'),
    path('users/dashboard/update', update_profile_view, name='update_profile'),
    path('users/dashboard/check_profile', UserProfileDetailView.as_view(), name='check_profile'),



    # notification
    path('users/messages', notifications, name ="message")







    
]