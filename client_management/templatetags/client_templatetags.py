import datetime

from django import template
from django.db.models import Q, Sum

from accounts.models import Customers
from client_management.models import *
register = template.Library()

register = template.Library()

@register.simple_tag
def route_wise_bottle_count(route_pk):
    customers = Customers.objects.filter(routes__pk=route_pk)
    
    final_bottle_count = 0 
    
    for customer in customers:
        total_bottle_count = CustomerSupply.objects.filter(customer=customer.customer_id)\
                                                     .aggregate(total_quantity=Sum('allocate_bottle_to_custody'))['total_quantity'] or 0
        
        last_supplied_count = 0
        
        if (supply_items:=CustomerSupplyItems.objects.filter(customer_supply__customer=customer.customer_id)).exists():
            last_supplied_count = supply_items.values_list('quantity', flat=True).latest("customer_supply__created_date") or 0

        pending_count = CustomerSupply.objects.filter(customer=customer.customer_id)\
                                                .aggregate(total_quantity=Sum('allocate_bottle_to_pending'))['total_quantity'] or 0

        customer_bottle_count = total_bottle_count + last_supplied_count + pending_count
        final_bottle_count += customer_bottle_count
    
    return final_bottle_count


@register.simple_tag
def route_wise_customer_bottle_count(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
    custody_count = 0
    outstanding_bottle_count = 0
    
    if (custody_stock:=CustomerCustodyStock.objects.filter(customer=customer,product__product_name="5 Gallon")).exists() :
        custody_count = custody_stock.first().quantity 
    
    if (outstanding_count:=CustomerOutstandingReport.objects.filter(customer=customer,product_type="emptycan")).exists() :
        outstanding_bottle_count = outstanding_count.first().value
    
    last_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).order_by('-customer_supply__created_date').values_list('quantity', flat=True).first() or 0

    total_bottle_count = custody_count + outstanding_bottle_count + last_supplied_count
    
    return {
        'custody_count': custody_count,
        'outstanding_bottle_count': outstanding_bottle_count,
        'last_supplied_count': last_supplied_count,
        'total_bottle_count': total_bottle_count
    }
        
        