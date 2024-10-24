import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from client_management.models import *
from coupon_management.models import CouponStock
from sales_management.models import *
from van_management.models import VanCouponStock

register = template.Library()

@register.simple_tag
def available_valuable_coupons(coupon_pk):
    return CouponLeaflet.objects.filter(coupon__pk=coupon_pk)

@register.simple_tag
def available_free_coupons(coupon_pk):
    return FreeLeaflet.objects.filter(coupon__pk=coupon_pk)

@register.simple_tag
def get_coupon_designation(pk):
    instance = NewCoupon.objects.get(pk=pk)
    coupon_status = CouponStock.objects.get(couponbook=instance).coupon_stock
    
    if coupon_status == "customer":
        customer_instance = CustomerCouponItems.objects.get(coupon=instance).customer_coupon.customer
        
        context = {
            "pk": customer_instance.pk,
            "name": f"{customer_instance.custom_id} - {customer_instance.customer_name}",
        }
    
    elif coupon_status == "van":
        van_instance = VanCouponStock.objects.filter(coupon=instance).latest("created_date").van
        
        context = {
            "pk": van_instance.pk,
            "name": f"{van_instance.plate} - {van_instance.get_van_route()}",
        }
    
    elif coupon_status == "company":
        context = {
            "pk": "",
            "name": f"{instance.branch_id.name}",
        }
        
    elif coupon_status == "used":
        
        context = {
            "pk": "",
            "name": f"Used",
        }
    return context


