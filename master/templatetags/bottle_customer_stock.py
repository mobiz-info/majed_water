from django import template

from client_management.models import CustomerCoupon, CustomerOutstanding, CustomerSupply
from invoice_management.models import Invoice
from sales_management.models import CollectionPayment

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_supply(customer_id, created_date):
    # Replace this with your actual logic for fetching supplies
    return CustomerSupply.objects.filter(customer__pk=customer_id, created_date__date=created_date)

@register.simple_tag
def get_coupon(customer_id, created_date):
    # Replace this with your actual logic for fetching supplies
    return CustomerCoupon.objects.filter(customer__pk=customer_id, created_date__date=created_date)

@register.simple_tag
def get_outstanding(customer_id, created_date):
    # Replace this with your actual logic for fetching supplies
    return CustomerOutstanding.objects.filter(customer__pk=customer_id, created_date__date=created_date,product_type="amount")

@register.simple_tag
def get_invoice(customer_id, created_date):
    # Replace this with your actual logic for fetching supplies
    return Invoice.objects.filter(customer__pk=customer_id, created_date__date=created_date,is_deleted=False)

@register.simple_tag
def get_collected(customer_id, created_date):
    # Replace this with your actual logic for fetching supplies
    return CollectionPayment.objects.filter(customer__pk=customer_id, created_date__date=created_date)


