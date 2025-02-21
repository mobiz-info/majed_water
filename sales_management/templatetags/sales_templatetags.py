import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django import template
from django.db.models import Q, Sum,F,Avg

from client_management.models import CustomerCoupon, CustomerCouponItems, CustomerSupply,CustomerSupplyItems, CustodyCustomItems, CustomerReturnItems
from invoice_management.models import SuspenseCollection
from sales_management.models import CollectionPayment
from van_management.models import Expense, Van_Routes, Van, VanProductStock
from product.models import *

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
        
    supplies = CustomerSupply.objects.filter(customer__routes_id=route_id,created_date__range=(start_date, end_date))
    
    sales_quantity = supplies.aggregate(total_qty=Sum(F('customersupplyitems__quantity')))['total_qty'] or 0
    avg_price = supplies.aggregate(average_rate=Avg('customer__rate'))['average_rate'] or 0
    
    cash_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies,
        customer_supply__customer__sales_type="CASH"
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    credit_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies
    ).exclude(customer_supply__customer__sales_type__in=["FOC", "CASH COUPON"]).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    coupon_sales_qnty = CustomerSupplyItems.objects.filter(
        customer_supply__in=supplies,
        customer_supply__customer__sales_type="CASH COUPON"
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    cash_sales = supplies.filter(amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON").aggregate(total=Sum('amount_recieved'))['total'] or 0
    credit_sales = supplies.filter(amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"]).aggregate(total=Sum('net_payable'))['total'] or 0
    
    foc_sales = CustomerSupplyItems.objects.filter(customer_supply__in=supplies,customer_supply__customer__sales_type='FOC').aggregate(total=Sum('quantity'))['total'] or 0
    foc_sales = foc_sales + (supplies.aggregate(total=Sum('allocate_bottle_to_free'))['total'] or 0)
    
    coupon_sales = CustomerCoupon.objects.filter(created_date__range=(start_date, end_date),customer__routes_id=route_id).aggregate(total=Sum('amount_recieved'))['total'] or 0

    collections = CollectionPayment.objects.filter(
        customer__routes_id=route_id,
        created_date__range=(start_date, end_date)
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
        "foc_sales": foc_sales,
        "credit_collection": credit_collection,
        "total_expense": total_expense,
        "net_paid": net_paid,
    }

@register.simple_tag
def get_route_sales_report(route, start_date):
       
    if start_date is None:
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1)

    # Ensure start_date is timezone-aware if needed
    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date)

    start_date = start_date.replace(day=1)
    next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_date = next_month - timedelta(days=1)

    sales_report = []

    current_date = start_date
    # print("current_date",current_date)
    while current_date <= end_date:
        customer_supplies = CustomerSupply.objects.filter(
            created_date__date=current_date,
            customer__routes=route
        ).prefetch_related(
            'customer', 'customer__sales_staff',
            'customer__routes', 'customer__location', 'customer__emirate'
        )

        # Initialize daily totals
        daily_sale_qty = 0
        daily_cash_sales = 0
        daily_credit_sales = 0
        daily_coupon_10_leaf = 0
        daily_coupon_20_leaf = 0
        daily_credit_collections = 0
        daily_expenses = 0
        daily_foc = 0
        daily_net_cash_in_hand = 0
        
        van_route = Van_Routes.objects.filter(routes=route).first()
        salesman = van_route.van.salesman
        products = ProdutItemMaster.objects.filter()
        van_instances = Van.objects.get(salesman=salesman)
        van_product_stock = VanProductStock.objects.filter(created_date=current_date,van=van_instances,product__product_name="5 Gallon")
        for v in van_product_stock:
            foc_sales=v.foc
        five_gallon_supply = CustomerSupplyItems.objects.filter(customer_supply__created_date__date=current_date,customer_supply__customer__routes=route,product__product_name="5 Gallon").values_list('customer_supply__pk', flat=True)
        five_gallon_cash_sales = CustomerSupply.objects.filter(pk__in=five_gallon_supply,created_date__date=current_date,amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON")
        five_gallon_cash_total_received = five_gallon_cash_sales.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
        
        
        five_gallon_credit_sales = CustomerSupply.objects.filter(pk__in=five_gallon_supply,created_date__date=current_date,amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"])
        five_gallon_credit_total_received = five_gallon_credit_sales.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
        
        
        expenses_instanses = Expense.objects.filter(expense_date=current_date,van=van_route.van,route=route)
        expenses = expenses_instanses.aggregate(total_expense=Sum('amount'))['total_expense'] or 0
        
        for supply in customer_supplies:
            # Calculate sales data
            total_qty = supply.get_total_supply_qty()
            total_coupon = supply.total_coupon_recieved()
            coupon_10_leaf = total_coupon["manual_coupon"]
            coupon_20_leaf = total_coupon["digital_coupon"]

            # Get credit collection
            collection = CollectionPayment.objects.filter(
                customer=supply.customer,
                created_date__date=current_date
            ).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0


            
            net_cash_in_hand = (five_gallon_cash_total_received + five_gallon_credit_total_received + collection) - expenses

            # Accumulate daily totals
            daily_sale_qty += total_qty
            daily_cash_sales = five_gallon_cash_total_received
            daily_credit_sales = five_gallon_credit_total_received
            daily_coupon_10_leaf += coupon_10_leaf
            daily_coupon_20_leaf += coupon_20_leaf
            daily_credit_collections += collection
            daily_expenses = expenses
            daily_foc = foc_sales
            daily_net_cash_in_hand = net_cash_in_hand
            
            

        # Append daily totals to the sales report
        sales_report.append({
            'date': current_date,
            'sale_qty': daily_sale_qty,
            'cash_sale': daily_cash_sales,
            'credit_sale': daily_credit_sales,
            'coupon_10_leaf': daily_coupon_10_leaf,
            'coupon_20_leaf': daily_coupon_20_leaf,
            'coupon_received': daily_coupon_10_leaf + daily_coupon_20_leaf,
            'foc': daily_foc,
            'credit_collection': daily_credit_collections,
            'expense': daily_expenses,
            'net_cash_in_hand': daily_net_cash_in_hand,
        })

        # Move to the next day
        current_date += timedelta(days=1)

    return sales_report

@register.simple_tag
def get_supply_coupon_qty(route, date, coupon_id):
    return CustomerCoupon.objects.filter(
        created_date__date=date,
        customer__routes__pk=route,
        customercouponitems__coupon__coupon_type__pk=coupon_id
    ).aggregate(total_collected=Sum('amount_recieved'))['total_collected'] or 0