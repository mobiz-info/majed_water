import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from client_management.models import *
from sales_management.models import *

register = template.Library()

@register.simple_tag
def available_valuable_coupons(coupon_pk):
    return CouponLeaflet.objects.filter(coupon__pk=coupon_pk)

@register.simple_tag
def available_free_coupons(coupon_pk):
    return FreeLeaflet.objects.filter(coupon__pk=coupon_pk)


