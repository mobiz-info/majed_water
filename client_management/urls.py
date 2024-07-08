from django.urls import path
from .views import *
from django.urls import reverse

from django.urls import path,re_path
from . views import *

urlpatterns = [
        path('customer_custody_item/<str:customer_id>', customer_custody_item, name='customer_custody_item'),
        path('get_custody_items', get_custody_items, name='get_custody_items'),

        #vacation
        path('vacation_list', vacation_list, name="vacation_list"),
        path('vacation_add', Vacation_Add.as_view(), name="vacation_add"),
        path('vacation_edit/<uuid:vacation_id>', Vacation_Edit.as_view(), name='vacation_edit'),
        path('vacation_delete/<uuid:vacation_id>',  Vacation_Delete.as_view(), name="vacation_delete"),
        path('vacation_route',  RouteSelection.as_view(), name="vacation_route"),

        path('', vacation_list, name="vacation_list"),

        # path('create_custody_item/<uuid:pk>', CreateCustodyItemView.as_view(), name='create_custody_item'),
        path('customer_custody_list', CustomerCustodyList.as_view(), name='customer_custody_list'),
        path('add_custody_items', AddCustodyItems.as_view(), name='add_custody_items'),
        path('add_custody_list',AddCustodyList.as_view(),name='add_custody_list'),
        path('edit_custody_item',EditCustodyItem.as_view(),name='add_custody_list'),
        # path('edit_custody_item',DeleteCustodyItem.as_view(),name='add_custody_list'),
        # path('pullout_list<str:pk>', PulloutListView.as_view(), name='pullout_list'),

        # path('count_coupen', CountCoupen, name="count_coupen"),
        
        re_path(r'customer-supply-list/$', customer_supply_list, name='customer_supply_list'),
        re_path(r'supply-customers/$', customer_supply_customers, name='customer_supply_customers'),
        re_path(r'create-customer-suppply/(?P<pk>.*)/$', create_customer_supply, name='create_customer_supply'),
        re_path(r'^info-customer-suppply/(?P<pk>.*)/$', customer_supply_info, name='customer_supply_info'),
        re_path(r'^edit-customer-suppply/(?P<pk>.*)/$', edit_customer_supply, name='edit_customer_supply'),
        re_path(r'^delete-customer-suppply/(?P<pk>.*)/$', delete_customer_supply, name='delete_customer_supply'),

#------------------------------Report-------------------------

        path('client_report', client_report, name='client_report'),
        path('clientdownload_pdf/<uuid:customer_id>/', clientdownload_pdf, name='clientdownload_pdf'),
        path('clientexport_to_csv/<uuid:customer_id>/', clientexport_to_csv, name='clientexport_to_csv'),
        path('custody_items_list_report', custody_items_list_report, name='custody_items_list_report'),
        path('custody_issue', custody_issue, name='custody_issue'),
        path('customer_custody_items/<uuid:customer_id>/', get_customercustody, name='customer_custody_items'),
        path('custody_report', custody_report, name='custody_report'),
   
        path('coupon_count/<uuid:pk>/', CouponCountList.as_view(), name='coupon_count_list'),

        # path('edit-coupon-count/<uuid:pk>/', edit_coupon_count, name='edit_coupon_count'),
        path('new-coupon-count/<uuid:pk>/', new_coupon_count, name='new_coupon_count'),
        path('delete-coupon-count/<uuid:pk>/', delete_count, name='delete_count'),
        
         #customer outstanding
        re_path(r'^customer-outstanding/$', customer_outstanding_list, name='customer_outstanding_list'),
        re_path(r'^create-customer-outstanding/$', create_customer_outstanding, name='create_customer_outstanding'),

        # Customer count
        path('customer_count', customer_count, name="customer_count"),

        path('bottle_count', bottle_count, name="bottle_count"),
        path('bottle-count-route-wise/<uuid:route_id>', bottle_count_route_wise, name='bottle_count_route_wise'),

        path('customer-orders-list', customer_orders, name="customer_orders_list"),
        path('customer-orders-status-acknowledge/<uuid:pk>', customer_order_status_acknowledge, name="customer_order_status_acknowledge"),
        
        path('nonvisitreason_List', nonvisitreason_List, name="nonvisitreason_List"),
        path('create_nonvisitreason', create_nonvisitreason, name="create_nonvisitreason"),
        path('delete_nonvisitreason/<uuid:id>/', delete_nonvisitreason, name='delete_nonvisitreason'),



]
