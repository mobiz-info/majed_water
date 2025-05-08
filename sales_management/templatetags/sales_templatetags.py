import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django import template
from django.db.models import Q, Sum,F,Avg,Count

from client_management.models import CustomerCoupon, CustomerCouponItems, CustomerSupply, CustomerSupplyCoupon,CustomerSupplyItems, CustodyCustomItems, CustomerReturnItems, CustomerCustodyStock
from invoice_management.models import SuspenseCollection
from sales_management.models import CollectionPayment
from van_management.models import Expense, Van_Routes, Van, VanProductStock
from product.models import *
from master.models import *

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



@register.simple_tag
def get_total_issued_quantity(date, van):
        total_return = 0
        van_route = Van_Routes.objects.filter(van__pk=van).first()
        if van_route:
            total_return = CustodyCustomItems.objects.filter(
               custody_custom__customer__routes=van_route.routes,
               custody_custom__created_date__date=date
            ).aggregate(total_return=Sum('quantity'))['total_return'] or 0
        return total_return

@register.simple_tag
def get_total_returned_quantity(date, van):
        total_return = 0
        van_route = Van_Routes.objects.filter(van__pk=van).first()
        if van_route:
            total_return = CustomerReturnItems.objects.filter(
               customer_return__customer__routes=van_route.routes,
               customer_return__created_date__date=date
            ).aggregate(total_return=Sum('quantity'))['total_return'] or 0
        return total_return
    
@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0 
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_sales_report(route_id, start_date, end_date):
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    # print(start_date)
    # print(end_date)
    supplies = CustomerSupply.objects.filter(customer__routes_id=route_id,created_date__date__range=(start_date, end_date))
    
    sales_quantity = supplies.aggregate(total_qty=Sum(F('customersupplyitems__quantity')))['total_qty'] or 0
    avg_price = supplies.aggregate(average_rate=Avg('customer__rate'))['average_rate'] or 0
    
    cash_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies,
        customer_supply__amount_recieved__gt=0
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    credit_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies,
        customer_supply__amount_recieved=0
    ).exclude(customer_supply__customer__sales_type__in=["FOC", "CASH COUPON"]).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    coupon_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies,
        customer_supply__customer__sales_type="CASH COUPON"
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    cash_sales = supplies.filter(amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON").aggregate(total=Sum('amount_recieved'))['total'] or 0
    credit_sales = supplies.filter(amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"]).aggregate(total=Sum('net_payable'))['total'] or 0
    
    foc_sales = CustomerSupplyItems.objects.filter(customer_supply__in=supplies,customer_supply__customer__sales_type='FOC').aggregate(total=Sum('quantity'))['total'] or 0
    foc_sales = foc_sales + (supplies.aggregate(total=Sum('allocate_bottle_to_free'))['total'] or 0)
    
    coupon_sales = CustomerCoupon.objects.filter(created_date__date__range=(start_date, end_date),customer__routes_id=route_id).aggregate(total=Sum('amount_recieved'))['total'] or 0
    coupon_sale_qty = CustomerCouponItems.objects.filter(customer_coupon__customer__routes_id=route_id,customer_coupon__created_date__date__range=(start_date, end_date)).count()
    

    collections = CollectionPayment.objects.filter(
        customer__routes_id=route_id,
        created_date__date__range=(start_date, end_date)
    )
    credit_collection = collections.aggregate(total=Sum('amount_received'))['total'] or 0

    expenses = Expense.objects.filter(
        route_id=route_id,
        date_created__range=(start_date, end_date)
    )
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    net_paid = cash_sales + credit_sales + coupon_sales + credit_collection - total_expense

    return {
        "sales_quantity": sales_quantity,
        "avg_price": avg_price,
        "cash_sales_qnty":cash_sales_qnty,
        "cash_sales": cash_sales,
        "credit_sales_qnty":credit_sales_qnty,
        "credit_sales": credit_sales,
        "coupon_sales_qnty":coupon_sales_qnty,
        "coupon_sales": coupon_sales,
        "coupon_sale_qty": coupon_sale_qty,
        "foc_sales": foc_sales,
        "credit_collection": credit_collection,
        "total_expense": total_expense,
        "net_paid": net_paid,
    }

@register.simple_tag
def get_route_sales_report(route, date):
    current_date = date
    
    customer_supply_item_instances = CustomerSupplyItems.objects.filter(customer_supply__created_date__date=current_date,customer_supply__customer__routes__pk=route)
    
    coupon_leaf_recieved = CustomerSupplyCoupon.objects.filter(customer_supply__created_date__date=current_date,customer_supply__customer__routes__pk=route).aggregate(Count('leaf'))['leaf__count']
    coupon_leaf_recieved += CustomerSupplyCoupon.objects.filter(customer_supply__created_date__date=current_date,customer_supply__customer__routes__pk=route).aggregate(Count('free_leaf'))['free_leaf__count']
    
    foc_qty = customer_supply_item_instances.filter(customer_supply__customer__sales_type__in=["FOC"]).aggregate(total=Sum('quantity'))['total'] or 0
    foc_qty += CustomerSupply.objects.filter(created_date__date=current_date,customer__routes__pk=route).aggregate(total=Sum('allocate_bottle_to_free'))['total'] or 0
    
    
    total_cash_qty = customer_supply_item_instances.filter(customer_supply__amount_recieved__gt=0).aggregate(total=Sum('quantity'))['total'] or 0,
    total_cash_amount = customer_supply_item_instances.filter(customer_supply__amount_recieved__gt=0).aggregate(total=Sum('customer_supply__subtotal'))['total'] or 0,
    total_credit_qty = customer_supply_item_instances.filter(customer_supply__amount_recieved=0).exclude(customer_supply__customer__sales_type__in=["FOC","CASH COUPON"]).aggregate(total=Sum('quantity'))['total'] or 0,
    total_coupon_qty = customer_supply_item_instances.filter(customer_supply__customer__sales_type="CASH COUPON").aggregate(total=Sum('quantity'))['total'] or 0,
    total_credit_amount = customer_supply_item_instances.filter(customer_supply__amount_recieved=0).exclude(customer_supply__customer__sales_type__in=["FOC","CASH COUPON"]).aggregate(total=Sum('customer_supply__subtotal'))['total'] or 0,
    total_qty = customer_supply_item_instances.aggregate(total=Sum('quantity'))['total'] or 0,
    credit_collection = CollectionPayment.objects.filter(created_date__date=current_date,customer__routes__pk=route).aggregate(total=Sum('amount_received'))['total'] or 0,
    expense = Expense.objects.filter(date_created=current_date,route__pk=route).aggregate(total=Sum('amount'))['total'] or 0
    coupon_amount = CustomerCoupon.objects.filter(created_date__date=current_date,customer__routes__pk=route).aggregate(total=Sum('amount_recieved'))['total'] or 0
    
    sales_report = {
        "total_cash_qty": total_cash_qty[0],
        "total_cash_amount": total_cash_amount[0],
        "total_credit_qty": total_credit_qty[0],
        "total_coupon_qty": total_coupon_qty[0],
        "total_credit_amount": total_credit_amount[0],
        "total_qty": total_qty[0],
        "foc_qty": foc_qty,
        "coupon_leaf_recieved": coupon_leaf_recieved,
        "credit_collection": credit_collection[0],
        "expense": expense,
        "net_cash_in_hand": total_cash_amount[0] + coupon_amount + credit_collection[0] - expense,
    }
    return sales_report

@register.simple_tag
def get_supply_coupon_qty(route, date, coupon_id):
    return CustomerCoupon.objects.filter(
        created_date__date=date,
        customer__routes__pk=route,
        customercouponitems__coupon__coupon_type__pk=coupon_id
    ).aggregate(total_collected=Sum('amount_recieved'))['total_collected'] or 0
    
@register.simple_tag
def route_bottle_stock(route_id, key, date=None, end_date=None):
    try:
        custody_count = 0
        total_bottle_count = 0

        # Default to today’s date if no start_date and end_date are provided
        current_date = datetime.today().date()
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else current_date
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else current_date


        # Get route details
        route = RouteMaster.objects.get(pk=route_id)
        customer_ids = Customers.objects.filter(routes=route).values_list('customer_id', flat=True)


        # Calculate custody stock for 5 Gallon
        custody_stock = CustomerCustodyStock.objects.filter(
            customer__customer_id__in=customer_ids,
            product__product_name="5 Gallon"
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        custody_count = custody_stock


        # Total bottles supplied within the date range
        total_supplied_count = CustomerSupplyItems.objects.filter(
            customer_supply__customer__customer_id__in=customer_ids,
            customer_supply__created_date__date__range=[start_date, end_date]
        ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0


        # Total empty bottles collected within the date range
        total_empty_collected = CustomerSupply.objects.filter(
            customer__customer_id__in=customer_ids,
            created_date__date__range=[start_date, end_date]
        ).aggregate(total_quantity=Sum('collected_empty_bottle'))['total_quantity'] or 0


        total_bottle_count += custody_count + total_supplied_count - total_empty_collected

        # Get Van Stock
        van_ids = Van_Routes.objects.filter(routes=route, van__salesman__user_type='Salesman').values_list('van__van_id', flat=True)

        van_stock = VanProductStock.objects.filter(
            created_date__range=[start_date, end_date], 
            van__van_id__in=van_ids, 
            product__product_name="5 Gallon"
        ).aggregate(total_count=Sum('stock'))['total_count'] or 0


        data = {
            'total_bottle_count': total_bottle_count,
            'van_stock': van_stock,
        }

        return data.get(key, 0)

    except RouteMaster.DoesNotExist:
        return 0
    except Exception as e:
        return 0
