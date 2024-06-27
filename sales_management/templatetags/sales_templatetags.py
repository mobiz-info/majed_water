import datetime

from django import template
from django.db.models import Q, Sum

from client_management.models import CustomerCoupon, CustomerCouponItems, CustomerSupply
from invoice_management.models import SuspenseCollection
from sales_management.models import CollectionPayment
from van_management.models import Expense

register = template.Library()

@register.simple_tag
def get_suspense_collection(date,salesman):
    
    cash_sales = CustomerSupply.objects.filter(created_date__date=date,salesman=salesman,amount_recieved__gt=0).aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
    recharge_cash_sales = CustomerCoupon.objects.filter(created_date__date=date,amount_recieved__gt=0).aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
    dialy_collections = CollectionPayment.objects.filter(created_date__date=date,salesman_id=salesman,amount_received__gt=0).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    
    expenses_instanses = Expense.objects.filter(date_created=date,van__salesman__pk=salesman)
    today_expense = expenses_instanses.aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    
    amount_paid = SuspenseCollection.objects.filter(date=date,salesman=salesman).aggregate(total_amount=Sum('amount_paid'))['total_amount'] or 0
    # # cash sales amount collected
    # supply_amount_collected = CustomerSupply.objects.filter(created_date__date=date,salesman__pk=salesman,customer__sales_type="CASH").aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
    # coupon_amount_collected = CustomerCoupon.objects.filter(created_date__date=date,salesman__pk=salesman,customer__sales_type="CASH").aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
    # cash_sales_amount_collected = supply_amount_collected + coupon_amount_collected
    
    # # collection details
    # dialy_collections = CollectionPayment.objects.filter(created_date__date=date,salesman_id=salesman,amount_received__gt=0)
    
    # credit_sales_amount_collected = dialy_collections.aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    # total_sales_amount_collected = cash_sales_amount_collected + credit_sales_amount_collected
    
    net_payble = cash_sales + recharge_cash_sales + dialy_collections - today_expense
    
    amount_balance = net_payble - amount_paid
    
    return {
        'opening_balance': net_payble,
        'amount_paid': amount_paid,
        'amount_balance': amount_balance,
    }
    
@register.simple_tag
def get_customer_coupon_details(pk):
    instances = CustomerCouponItems.objects.filter(customer_coupon=pk)
    return instances


