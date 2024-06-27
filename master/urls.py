from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='dashboard'),
    path('branch', Branch_List.as_view(), name='branch'),
    path('branch_create', Branch_Create.as_view(), name='branch_create'),
    path('branch_edit/<str:pk>', Branch_Edit.as_view(), name='branch_edit'),
    path('branch_details/<str:pk>', Branch_Details.as_view(), name='branch_details'),
    path('delete_branch/<str:pk>/',Branch_Delete.as_view(), name='delete_branch'),

    # path('route', Route_List.as_view(), name='route'),
    # path('route_create', Route_Create.as_view(), name='route_create'),
    # path('route_edit/<str:pk>', Route_Edit.as_view(), name='route_edit'),
    # path('route_details/<str:pk>', Route_Details.as_view(), name='route_details'),
    # path('route/delete/<uuid:pk>/', Route_Delete.as_view(), name='route_delete'),

    path('route/', Route_List.as_view(), name='route'),
    path('route_create/', Route_Create.as_view(), name='route_create'),
    path('route_edit/<str:pk>/', Route_Edit.as_view(), name='route_edit'),
    path('route_details/<str:pk>/', Route_Details.as_view(), name='route_details'),
    path('route/delete/<uuid:pk>/', Route_Delete.as_view(), name='route_delete'),


    path('designation', Designation_List.as_view(), name='designation'),
    path('designation_create',Designation_Create.as_view(), name='designation_create'),
    path('designation_edit/<str:pk>', Designation_Edit.as_view(), name='designation_edit'),
    path('designation_details/<str:pk>', Designation_Details.as_view(), name='designation_details'),
    path('designation_delete/<str:pk>', Designation_Delete.as_view(), name='designation_delete'),

    path('branch', branch, name='branch'),
    path('locations_list', Location_List.as_view(), name="locations_list"),
    path('location_add', Location_Adding.as_view(), name="location_add"),
    path('location_edit/<uuid:pk>', Location_Edit.as_view(), name='location_edit'),
    path('location_delete/<uuid:pk>/', Location_Delete.as_view(), name='location_delete'),

    path('category', Category_List.as_view(), name='category'),
    path('category_create',Category_Create.as_view(), name='category_create'),
    path('category_edit/<str:pk>', Category_Edit.as_view(), name='category_edit'),
    path('category_details/<str:pk>', Category_Details.as_view(), name='category_details'),
    
    
   ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

