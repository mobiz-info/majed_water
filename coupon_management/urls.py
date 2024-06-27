from django.urls import path
from .views import *



urlpatterns = [
    path('couponType',couponType, name='couponType'),
    path('create_couponType/',create_couponType, name='create_couponType'),
    path('view_couponType/<uuid:coupon_type_id>/', view_couponType, name="view_couponType"),
    path('edit_CouponType/<uuid:coupon_type_id>/', edit_CouponType, name="edit_CouponType"),
    path('delete_couponType/<uuid:coupon_type_id>/', delete_couponType, name='delete_couponType'),


    path('coupon',coupon, name='coupon'),
    path('create_coupon/',create_coupon, name='create_coupon'),
    path('view_coupon/<uuid:coupon_id>/', view_coupon, name="view_coupon"),
    path('edit_Coupon/<uuid:coupon_id>/', edit_Coupon, name="edit_Coupon"),
    path('delete_coupon/<uuid:coupon_id>/', delete_coupon, name='delete_coupon'),

    path('couponrequest',couponrequest, name='couponrequest'),
    path('create_couponRequest/',create_couponRequest, name='create_couponRequest'),
    path('view_couponRequest/<uuid:coupon_request_id>/', view_couponRequest, name="view_couponRequest"),

    path('assignStaffCoupon',assignStaffCoupon, name='assignStaffCoupon'),
    path('assign_to_staff/<uuid:coupon_request_id>/',assign_to_staff, name='assign_to_staff'),
    path('assign_to_customer/<uuid:assign_id>/',AssignToCustomerView.as_view(), name='assign_to_customer'),
    path('coupons_details_view/',AssignStaffCouponDetailsListView.as_view(), name='coupons_details_view'),
#----------------------------------New Coupon-------------------------------------------------------------------

    path('new_coupon',new_coupon, name='new_coupon'),
    path('create_Newcoupon/',create_Newcoupon, name='create_Newcoupon'),
    path('generate_leaflets/<uuid:coupon_id>/', generate_leaflets, name='generate_leaflets'),

    path('get_leaflet_serial_numbers/', get_leaflet_serial_numbers, name='get_leaflet_serial_numbers'),
    path('save_coupon_data/', save_coupon_data, name='save_coupon_data'),
    path('view_Newcoupon/<uuid:coupon_id>/', view_Newcoupon, name="view_Newcoupon"),
    path('edit_NewCoupon/<uuid:coupon_id>/', edit_NewCoupon, name="edit_NewCoupon"),

    path('delete_Newcoupon/<uuid:coupon_id>/', delete_Newcoupon, name='delete_Newcoupon'),
    path('customer_stock/', customer_stock, name='customer_stock'),
    path('generate_excel/', generate_excel, name='generate_excel'),
    path('customer_stock_pdf/', customer_stock_pdf, name='customer_stock_pdf'),

    path('redeemed_history/', redeemed_history, name='redeemed_history')




 ]
