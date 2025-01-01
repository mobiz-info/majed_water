import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from master.functions import get_next_visit_date
from client_management.models import *
register = template.Library()

@register.simple_tag
def get_next_visit_day(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
    if not customer.visit_schedule is None:
        next_visit_date = get_next_visit_date(customer.visit_schedule)
        # customer.next_visit_date = next_visit_date
        return next_visit_date
    else:
      return "-"

@register.simple_tag
def bottle_stock(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
   
    custody_count = 0
    outstanding_bottle_count = 0

    if (custody_stock:=CustomerCustodyStock.objects.filter(customer=customer,product__product_name="5 Gallon")).exists() :
        custody_count = custody_stock.first().quantity 

    if (outstanding_count:=CustomerOutstandingReport.objects.filter(customer=customer,product_type="emptycan")).exists() :
        outstanding_bottle_count = outstanding_count.first().value

    last_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).order_by('-customer_supply__created_date').values_list('quantity', flat=True).first() or 0

    total_bottle_count = custody_count + outstanding_bottle_count + last_supplied_count

    return total_bottle_count


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def other_product_rate(customer_pk,product_id):
    rate = ProdutItemMaster.objects.get(pk=product_id).rate
    if (rate_change_instances:=CustomerOtherProductCharges.objects.filter(product_item__pk=product_id,customer__pk=customer_pk)).exists():
        rate = rate_change_instances.first().current_rate
    return rate


