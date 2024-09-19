from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse
from django.views import View

from apiservices.notification import notification
from .forms import *
import uuid
from accounts.models import *
from .models import *
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from .models import *
from datetime import timedelta
from django.db.models import Sum, Case, When, IntegerField,Count,Q
from . serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication 
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from van_management.models import Van, VanProductStock , VanCouponStock
from van_management.models import Expense,Van_Routes,CustomerProductReturn,CustomerProductReplace

from customer_care.models import DiffBottlesModel
from client_management.models import CustomerSupply, CustomerOutstandingReport, CustomerSupplyCoupon
from client_management.models import CustomerSupplyStock,CustomerCouponStock, Vacation, NonvisitReport,CustomerSupplyItems

from sales_management.models import CollectionItems
from invoice_management.models import Invoice
from coupon_management.models import CouponStock, CouponLeaflet
from product.models import WashedUsedProduct
from apiservices.views import find_customers
import json


# Create your views here.
@login_required(login_url='login')
def home(request):
    template_name = 'master/dashboard/dashboard.html'
    
    today = timezone.now().date()
    # Get the total sales for today filtered by cash and credit
    cash_sales = CustomerSupply.objects.filter(created_date__date=today,customer__sales_type='CASH').count()
    credit_sales = CustomerSupply.objects.filter(created_date__date=today,customer__sales_type='CREDIT').count()
    total_sales = cash_sales + credit_sales
    # Get the total expense for today
    expense = Expense.objects.filter(expense_date=today).aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    
    #Get Today's Collection
    todays_collection = CollectionItems.objects.filter(collection_payment__created_date__date=today,collection_payment__amount_received__gt=0).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0
    print("todays_collection",todays_collection)
    yesterday = today - timedelta(days=1)

    # Old payments (everything before today)
    old_payment = CollectionItems.objects.filter(collection_payment__created_date__date=yesterday).aggregate(total_collected=Sum('amount_received'))['total_collected'] or 0

    # Total collection (sum of today's collection and old payments)
    total_collection = todays_collection + old_payment
    
    

    # Get the total count of all vans
    # total_vans = Van.objects.filter(van_master__created_date=today).distinct()
    # active_vans_count = total_vans.count()
    total_vans = Van.objects.all().count()
#----------Delivery Progress--------------------

    

    
    # -----------Yesterday Missed Customer----------
    # Calculate yesterday's date
    date = datetime.now().date()
    yesterday = date - timedelta(days=1)

    routes = RouteMaster.objects.all()  # Get all RouteMaster instances
    total_missed_customers = 0  # Initialize counter for all routes

    for route in routes:
        route_id = route.route_id  # Use route_id from RouteMaster

        # Get planned customers for yesterday
        planned_visitors_list = find_customers(request, str(yesterday), route_id)
        planned_visitors = len(planned_visitors_list) if planned_visitors_list else 0

        # Get visited customers (supplied) for yesterday
        visited_customers_ids = set(
            CustomerSupply.objects.filter(
                customer__routes__pk=route_id,
                created_date__date=yesterday
            ).values_list('customer_id', flat=True)
        )
        visited_customers_count = len(visited_customers_ids)

        # Calculate missed customers
        if isinstance(planned_visitors_list, list):
            missed_customers = [
                customer for customer in planned_visitors_list
                if customer['customer_id'] not in visited_customers_ids
            ]
            missed_customers_count = len(missed_customers)
        else:
            missed_customers_count = 0

        # Add to total missed customers
        total_missed_customers += missed_customers_count
        
# --------------------Yesterday Missed Customer----------

    # Get the total count of all customers
    total_customers = Customers.objects.count()
    
    # Calculate the date 10 days ago
    ten_days_ago = timezone.now() - timedelta(days=10)
    
    # Get the count of customers created exactly 10 days ago
    new_customers_count = Customers.objects.filter(created_date__date=ten_days_ago.date()).count()
    
#---------- Get the total count of emergency customers-------------
    today = timezone.now().date()
    emergency_customers = DiffBottlesModel.objects.filter(delivery_date=today)
    emergency_customer_ids = {ec.customer_id for ec in emergency_customers}
    total_emergency_customers = Customers.objects.filter(customer_id__in=emergency_customer_ids).count()
    
#-----------Get the total count of Vacation Mode Customers-------------    
    
    # Query all vacations where today is between start_date and end_date
    vacation_customers = Vacation.objects.filter(start_date__lte=today, end_date__gte=today)
    
    # Count the number of vacation customers
    vacation_customers_count = vacation_customers.count()
#-----------Get the total count of Door Lock Mode Customers-------------    

    door_lock_count = NonvisitReport.objects.filter(reason__reason_text="Door Lock").count()
    if door_lock_count is None:
        door_lock_count = 0

    
#-----------Sales type CASH,CREDIT,COUPON Pie Chart Data--------
    # Aggregating the data
    sales_pie_data = Customers.objects.values('sales_type').annotate(count=Count('sales_type'))

    # Creating the data structure for the pie chart
    sales_chart_data = {
        'Cash': 0,
        'Credit': 0,
        'Coupon': 0
    }

    for data in sales_pie_data:
        sales_type = data['sales_type']
        count = data['count']
        
        # Check if sales_type is None before using .upper()
        if sales_type:
            if 'CASH' in sales_type.upper():
                sales_chart_data['Cash'] += count
            elif 'CREDIT' in sales_type.upper():
                sales_chart_data['Credit'] += count
            elif 'COUPON' in sales_type.upper():
                sales_chart_data['Coupon'] += count

# Pass sales_chart_data to your context or return as JSON

#-----New Customers Bar Chart------------------
    ten_days_ago = datetime.now() - timedelta(days=10)
    new_customers = Customers.objects.filter(
            created_date__gte=ten_days_ago
        )
    # Count new customers for each salesman
    salesman_customer_count = new_customers.values('sales_staff__username').annotate(customer_count=Count('customer_id')).order_by('-customer_count')

    salesmen = [entry['sales_staff__username'] for entry in salesman_customer_count]
    customer_counts = [entry['customer_count'] for entry in salesman_customer_count]
    # Pass salesmen and  customer_counts to your context or return as JSON
#-----------5 Gallon Supply Pie Chart-------------
    five_G_supply_data = (
            CustomerSupplyItems.objects
            .filter(product__product_name="5 Gallon")
            .values('customer_supply__salesman__username')  # Group by salesman's username
            .annotate(total_quantity=Sum('quantity'))  # Calculate total quantity for each salesman
        )
    print("five_G_supply_data",five_G_supply_data)
    # Calculate total 5-gallon quantity across all salesmen
    total_quantity = sum([data['total_quantity'] for data in five_G_supply_data])
    print("Total Quantity of 5 Gallon Supplies:", total_quantity)

    # Calculate the percentage contribution of each salesman
    for data in five_G_supply_data:
        data['percentage'] = (data['total_quantity'] / total_quantity) * 100
     # Extract salesmen names and their respective percentage contribution
    salesmen_names = [data['customer_supply__salesman__username'] for data in five_G_supply_data]
    salesmen_percentages = [data['percentage'] for data in five_G_supply_data]

        
    # Pass  salesmen_names and salesmen_percentages to your context or return as JSON

#-------------------End of Overview Tab-----------


#----------Start of Sales Tab--------------------
    sales_return = CustomerProductReturn.objects.filter(product__product_name='5 Gallon',created_date__date=today).aggregate(total=Sum('quantity'))['total']
    if sales_return is None:
        sales_return = 0
        
    product_replacement = CustomerProductReplace.objects.filter(product__product_name='5 Gallon',created_date__date=today).aggregate(total=Sum('quantity'))['total']
    if product_replacement is None:
        product_replacement = 0


#------------ Get the total returns for today filtered by cash and credit
    cash_returns_today = Invoice.objects.filter(
        created_date__date=today,
        customer__sales_type='CASH'
    ).count()

    credit_returns_today = Invoice.objects.filter(
        created_date__date=today,
        customer__sales_type='CASH'
    ).count()

    total_returns_today = cash_returns_today + credit_returns_today
    
    # Get the total collection for today filtered by cash and credit

    cash_collection_today = CollectionItems.objects.filter(
        collection_payment__customer__sales_type='CASH',
        collection_payment__created_date__date=today
    ).count()

    credit_collection_today = CollectionItems.objects.filter(
        collection_payment__customer__sales_type='CREDIT',
         collection_payment__created_date__date=today
    ).count()

    total_collection_today = cash_collection_today + credit_collection_today
    
    # Get the total collection for previous days (excluding today) filtered by cash and credit
    cash_collection_previous = CollectionItems.objects.filter(
        collection_payment__customer__sales_type='CASH',
        collection_payment__created_date__lt=today
    ).count()

    credit_collection_previous = CollectionItems.objects.filter(
        collection_payment__customer__sales_type='CREDIT',
        collection_payment__created_date__lt=today
    ).count()

    total_collection_previous = cash_collection_previous + credit_collection_previous
    
    # Get the total outstanding for today filtered by cash and credit
    cash_outstanding_today = CustomerOutstandingReport.objects.filter(
        customer__sales_type='CASH',
        value__gt=0
    ).count()

    credit_outstanding_today = CustomerOutstandingReport.objects.filter(
        customer__sales_type='CREDIT',
        value__gt=0
    ).count()

    total_outstanding_today = cash_outstanding_today + credit_outstanding_today
    
    # Get today's total issued 5-gallon count from VanProductStock
    total_issued_5gallon_today = VanProductStock.objects.filter(
        product__product_name='5 gallon',
        created_date=datetime.today().date()
        # created_date__date=today
    ).aggregate(total_issued=Sum('stock'))['total_issued'] or 0
    
    # Calculate the pending bottles given today 
    pending_bottles_given_today = VanProductStock.objects.filter(
        product__product_name='5 gallon',
        created_date=datetime.today().date()
    ).aggregate(total_pending=Sum('pending_count'))['total_pending'] or 0
    

    # Get the count of digital and manual coupons sold
    manual_book_sold = CouponStock.objects.filter(
        created_date=datetime.today().date(),
        coupon_stock="van",
        couponbook__coupon_method='MANUAL').count()
    digital_book_sold = CouponStock.objects.filter(
        created_date=datetime.today().date(),
        coupon_stock="van",
        couponbook__coupon_method='DIGITAL').count()
    
    # Calculate the total coupons collected (for both manual and digital)
    customer_supplies_today = CustomerSupply.objects.filter(created_date=datetime.today().date())
    manual_coupons_collected = sum(
        cs.total_coupon_recieved()["manual_coupon"] for cs in customer_supplies_today
    )
    digital_coupons_collected = sum(
        cs.total_coupon_recieved()["digital_coupon"] for cs in customer_supplies_today
    )
    
    # Count of used coupon leaflets for manual method
    manual_leaflets_used_count = CouponLeaflet.objects.filter(
        used=True, coupon__coupon_method='manual'
    ).count()

    # Count of used coupon leaflets for digital method
    digital_leaflets_used_count = CouponLeaflet.objects.filter(
        used=True, coupon__coupon_method='digital'
    ).count()

#-------------Start of Bottle OverView Tab-----------------
# Filter for customers created today and where is_calling_customer is True
    calling_customers_count = Customers.objects.filter(
        created_date__date=today, 
        is_calling_customer=True
    ).aggregate(total=Count('customer_id'))['total']

    # If no customers match the query, total will be None, so ensure it's 0
    if calling_customers_count is None:
        calling_customers_count = 0
    
    # Calculate the scrap bottles collected today 

    scrap_bottle_collected_today = VanProductStock.objects.filter(
        product__product_name='5 gallon',
        created_date=datetime.today().date()
    ).aggregate(total_scrap=Sum('excess_bottle'))['total_scrap'] or 0
    # Calculate the  bottle in Service given today 

    bottle_in_service_today = VanProductStock.objects.filter(
        product__product_name='5 gallon',
        created_date=datetime.today().date()
    ).aggregate(total_service_bottle=Sum('damage_count'))['total_service_bottle'] or 0
    
    # Calculate the company Fresh stock given today 

    company_fresh_stock = VanProductStock.objects.filter(
        product__product_name='5 gallon',
        created_date=datetime.today().date()
    ).aggregate(total_fresh_stock=Sum('opening_count'))['total_fresh_stock'] or 0
    

    # Filter WashedUsedProduct based on these product IDs and today's date
    used_bottle_stock = WashedUsedProduct.objects.filter(
        product__product_name = "5 Gallon",
    ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
    
    
    # Fetch market bottle count
    start_date = request.GET.get('start_date')

    market_bottle_count = Van_Routes.objects.all()

    # Prepare dictionaries to hold the stock and pending bottle data for each van route
    stock_data_by_route = {}
    pending_bottles_by_route = {}
     # Filter based on date if provided
    if start_date:
        market_bottle_count = market_bottle_count.filter(created_date__date=start_date)

    for route in market_bottle_count:
        # Get the salesman ID for the current van route
        salesman_id = route.van.salesman.id

        # Get total stock with customers for this salesman
        stock_data = CustomerSupplyStock.objects.filter(customer__sales_staff__id=salesman_id).aggregate(total_stock=Sum('stock_quantity'))
        stock_data_by_route[route.van_route_id] = stock_data['total_stock'] or 0  # Default to 0 if no stock

        # Get pending bottles for this salesman
        pending_bottles = CustomerSupply.objects.filter(customer__sales_staff__id=salesman_id).aggregate(total_pending=Sum('allocate_bottle_to_pending'))['total_pending'] or 0
        pending_bottles_by_route[route.van_route_id] = pending_bottles
    
    
    sold_coupons_data = CustomerCouponStock.get_sold_coupons_by_type()
    
    # Fetch all van routes
    van_routes = Van_Routes.objects.all()

    # Prepare a dictionary to hold excess bottle data for each van route
    excess_data_by_route = {}

    for route in van_routes:
        # Fetch the van related to the current route
        van = route.van

        # Get the total excess bottle count for the van from the VanProductStock model
        excess_data = VanProductStock.objects.filter(van=van).aggregate(total_excess=Sum('excess_bottle'))

        # Store the excess data by route
        excess_data_by_route[route.van_route_id] = excess_data['total_excess'] or 0  # If no data, default to 0
    
    
    #Coupon Book Sale Summary
    
    coupon_summary = CustomerCouponStock.objects.values('coupon_type_id__coupon_type_name').annotate(
            manual_count=Sum(
                Case(
                    When(coupon_method='manual', then='count'),
                    output_field=IntegerField(),
                )
            ),
            digital_count=Sum(
                Case(
                    When(coupon_method='digital', then='count'),
                    output_field=IntegerField(),
                )
            ),
            total=Sum('count')
        )
        
    # print("coupon_summary",coupon_summary)
    
    #--------------------start of Customer statictics Overview------------#
    
    # finding of New Customer
    
    # Get today's and month's start dates
    today = datetime.today().date()
    start_of_month = today.replace(day=1)
    
    # Filter customers created today and this month
    today_customers = Customers.objects.filter(created_date__date=today)
    month_customers = Customers.objects.filter(created_date__date__gte=start_of_month)

    # Group by routes and count customers
    today_customer_counts = today_customers.values('routes__route_name').annotate(count_today=Count('customer_id'))
    month_customer_counts = month_customers.values('routes__route_name').annotate(count_month=Count('customer_id'))

    # Creating dictionaries to hold route-based counts
    today_counts = {item['routes__route_name']: item['count_today'] for item in today_customer_counts}
    month_counts = {item['routes__route_name']: item['count_month'] for item in month_customer_counts}
    
    # Get all routes
    routes = RouteMaster.objects.all()
    
    # Prepare data for template
    newCustomer_data = []
    for route in routes:
        route_name = route.route_name
        newCustomer_data.append({
            'route_name': route_name,
            'count_today': today_counts.get(route_name, 0),
            'count_month': month_counts.get(route_name, 0)
        })
        
    
    # Finding Inactive Customers
        today = timezone.now().date()
        last_20_days = today - timedelta(days=20)

        # Dictionary to store data for each route
        inactive_routes_data = []

        # Fetch all routes
        inactive_routes = RouteMaster.objects.all()

        for route in inactive_routes:
            # All customers assigned to this route
            route_customers = Customers.objects.filter(routes=route)

            # Customers who made a purchase in the last 20 days
            visited_customers = CustomerSupply.objects.filter(
                created_date__date__gte=last_20_days,
                customer__in=route_customers
            ).values_list('customer', flat=True)

            # Inactive customers in the last 20 days
            inactive_customers = route_customers.exclude(pk__in=visited_customers)

            # Add the route data to the list
            inactive_routes_data.append({
                'route_name': route.route_name,
                'inactive_customers_count': inactive_customers.count(),
            })
            
        
    # Non-Visited Customers
    non_visited_data = []

    # Iterate over all routes and calculate non-visited customers
    all_nonvisitedroutes = RouteMaster.objects.all()
    for route in all_nonvisitedroutes:
        # Find the corresponding van route using the correct field
        van_route = Van_Routes.objects.filter(routes=route).first()
        
        if van_route:
            # Get the associated van
            van = van_route.van
            
            # Assuming the Van model is linked to the salesman (CustomUser)
            salesman = van.salesman  # You need to ensure this field exists in the Van model
            
            # Get planned visits for this route
            todays_customers = find_customers(request, str(datetime.today().date()), route.pk)

            if todays_customers is None:
                todays_customers = []  # Handle None case, treat as an empty list

            # Extract customer IDs from todays_customers
            customer_ids = [customer['customer_id'] for customer in todays_customers]



            # Actual visits (filter by salesman)
            visited_customers = CustomerSupply.objects.filter(customer__in=customer_ids, salesman=salesman)

            visited_customer_ids = set(visited_customers.values_list('customer_id', flat=True))

            # Filter non-visited customers
            non_visited = [customer for customer in todays_customers if customer['customer_id'] not in visited_customer_ids]

            # Add the route and non-visited customer count to the data
            non_visited_data.append({
                'route_name': route.route_name,
                'non_visited_count': len(non_visited),
            })
            
    #-----Customer's Sales Type Count of cash,credit,is_calling,Coupon----------------
    # Initialize route_customer_data and totals
    route_customer_data = []
    total_cash = 0
    total_credit = 0
    total_coupon = 0
    total_call = 0
    total_route_sum = 0
    
    # Get all routes
    all_routes = RouteMaster.objects.all()

    # Iterate over all routes
    for route in all_routes:
        # Get customers for the current route
        customers = Customers.objects.filter(routes=route)

        # Count customers based on sales_type and is_calling_customer
        cash_count = customers.filter(sales_type='CASH').count()
        credit_count = customers.filter(sales_type='CREDIT').count()
        coupon_count = customers.filter(sales_type='CASH COUPON').count()
        call_count = customers.filter(is_calling_customer=True).count()

        # Calculate the total for the current route
        route_total = cash_count + credit_count + coupon_count + call_count

        # Append data for the current route
        route_customer_data.append({
            'route_name': route.route_name,
            'cash_count': cash_count,
            'credit_count': credit_count,
            'coupon_count': coupon_count,
            'call_count': call_count,
            'route_total': route_total,
        })

        # Add to the overall totals
        total_cash += cash_count
        total_credit += credit_count
        total_coupon += coupon_count
        total_call += call_count
        total_route_sum += route_total  

    # Get the sales type counts for each route
    sales_customer_data = []
    total_home = 0
    total_corporate = 0
    total_shop = 0
    total_customer_sales_type = 0
    
    # Get all routes
    all_routes = RouteMaster.objects.all()
    
    # Iterate over all routes
    for route in all_routes:
        # Get customers for the current route
        customers = Customers.objects.filter(routes=route)
        # Count customers based on customer_type
        home_count = customers.filter(customer_type='HOME').count()
        corporate_count = customers.filter(customer_type='CORPORATE').count()
        shop_count = customers.filter(customer_type='SHOP').count()
        # Calculate the total for the current route
        total_sales_type = home_count + corporate_count + shop_count
        
        # Append data for the current route
        sales_customer_data.append({
            'route_name': route.route_name,
            'home_count': home_count,
            'corporate_count': corporate_count,
            'shop_count': shop_count,
            'total_sales_type': total_sales_type,
        })
        
        # Add counts to the total counters
        total_home += home_count
        total_corporate += corporate_count
        total_shop += shop_count
        total_customer_sales_type += total_sales_type


    context = {
        'cash_sales': cash_sales,
        'credit_sales': credit_sales,
        'total_sales': total_sales,
        'expense':expense,
        'todays_collection':todays_collection,
        'old_payment':old_payment,
        'total_collection':total_collection,
        
        # 'active_vans_count': active_vans_count,
        'total_vans':total_vans,
        'planned_visitors':planned_visitors,
        'visited_customers_count':visited_customers_count,
        'total_missed_customers_yesterday': total_missed_customers,
        'total_customers': total_customers,
        'new_customers_count': new_customers_count,
        'total_emergency_customers': total_emergency_customers,
        'vacation_customers_count': vacation_customers_count,
        'door_lock_count':door_lock_count,
        
        'sales_chart_data':sales_chart_data,
        'salesmen':salesmen,
        'customer_counts':customer_counts,
        # 'five_G_supply_data':list(five_G_supply_data),
        # 'salesmen_names':salesmen_names,
        # 'salesmen_percentages':salesmen_percentages,
        'salesmen_names': json.dumps(salesmen_names),  # Ensure it's JSON-encoded
        'salesmen_percentages': json.dumps(salesmen_percentages),  # Ensure it's JSON-encoded

        'sales_return':sales_return,
        'product_replacement':product_replacement,
        'cash_returns_today': cash_returns_today,
        'credit_returns_today': credit_returns_today,
        'total_returns_today': total_returns_today,
        'cash_collection_today': cash_collection_today,
        'credit_collection_today': credit_collection_today,
        'total_collection_today': total_collection_today,
        'cash_collection_previous': cash_collection_previous,
        'credit_collection_previous': credit_collection_previous,
        'total_collection_previous': total_collection_previous,
        'cash_outstanding_today': cash_outstanding_today,
        'credit_outstanding_today': credit_outstanding_today,
        'total_outstanding_today': total_outstanding_today,
        
        'total_issued_5gallon_today': total_issued_5gallon_today,  
        'pending_bottles_given_today':pending_bottles_given_today,
        
        'calling_customers_count':calling_customers_count,
        'scrap_bottle_collected_today':scrap_bottle_collected_today,
        'bottle_in_service_today':bottle_in_service_today,
        'company_fresh_stock':company_fresh_stock,
        'used_bottle_stock':used_bottle_stock,
        
        #Bottle count in market
        'market_bottle_count' :market_bottle_count,
        'stock_data_by_route': stock_data_by_route,  
        'pending_bottles_by_route': pending_bottles_by_route,
        'filter_data': {'start_date': start_date},

        
        #Excess / Shortage Bottle 
        'van_routes': van_routes,
        'excess_data_by_route': excess_data_by_route,
        
        #Coupon Book Sale Summary
        'coupon_summary':coupon_summary,
        
        #
        'sold_coupons_data':sold_coupons_data,
        
        # New customer data
        'newCustomer_data':newCustomer_data,
        
        'inactive_routes_data': inactive_routes_data,
    

        'non_visited_data': non_visited_data,
        'inactive_routes': inactive_routes,
        
        'route_customer_data': route_customer_data,
        'total_cash': total_cash,
        'total_credit': total_credit,
        'total_coupon': total_coupon,
        'total_call': total_call,
        'grand_total': total_cash + total_credit + total_coupon + total_call,  
        'total_route_sum': total_route_sum,
        
        'sales_customer_data': sales_customer_data,
        'total_home': total_home,
        'total_corporate': total_corporate,
        'total_shop': total_shop,
        'total_customer_sales_type': total_customer_sales_type,
        
        'manual_book_sold':manual_book_sold,
        'digital_book_sold':digital_book_sold,
        'manual_coupons_collected':manual_coupons_collected,
        'digital_coupons_collected':digital_coupons_collected,
        'manual_leaflets_used_count':manual_leaflets_used_count,
        'digital_leaflets_used_count':digital_leaflets_used_count,

    }
    
    return render(request, template_name, context)  


class Branch_List(View):
    template_name = 'master/branch_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        branch_li = BranchMaster.objects.all().order_by("-created_date")
        context = {'branch_li': branch_li}
        return render(request, self.template_name, context)

class Branch_Create(View):
    template_name = 'master/branch_create.html'
    form_class = Branch_Create_Form

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            branch = BranchMaster.objects.get(branch_id=data.branch_id) 
            username=request.POST.get('username')
            password=request.POST.get('pswd')
            hashed_password=make_password(password)
            email=data.email
            user_name=data.name
            branch_data=CustomUser.objects.create(password=hashed_password,username=username,first_name=user_name,email=email,user_type='Branch User',branch_id=branch)
            data.save()
            messages.success(request, 'Branch Successfully Added.', 'alert-success')
            return redirect('branch')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)


class Branch_Edit(View):
    template_name = 'master/branch_edit.html'
    form_class = Branch_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = BranchMaster.objects.get(branch_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)
 
    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = BranchMaster.objects.get(branch_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            print(request)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Branch Data Successfully Updated', 'alert-success')
            return redirect('branch')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Branch_Details(View):
    template_name = 'master/branch_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        branch_det = BranchMaster.objects.get(branch_id=pk)
        context = {'branch_det': branch_det}
        return render(request, self.template_name, context)    
class Branch_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(BranchMaster, branch_id=pk)
        return render(request, 'master/branch_delete.html', {'branch': rec})
    
    def post(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(BranchMaster, branch_id=pk)
        rec.delete()
        messages.success(request, 'Route Deleted Successfully', 'alert-success')
        return redirect('branch')    

   
class Route_List(View):
    template_name = 'master/route_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        route_li = RouteMaster.objects.filter()
        context = {'route_li': route_li}
        return render(request, self.template_name, context)
    
class Route_Create(View):
    template_name = 'master/route_create.html'
    form_class = Route_Create_Form

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            
            branch_id=request.user.branch_id.branch_id
            branch = BranchMaster.objects.get(branch_id=branch_id)  # Adjust the criteria based on your model
            data.branch_id = branch
            data.save()
            messages.success(request, 'Route Successfully Added.', 'alert-success')
            return redirect('route')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)


class Route_Edit(View):
    template_name = 'master/route_edit.html'
    form_class = Route_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = RouteMaster.objects.get(route_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)
    
    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = RouteMaster.objects.get(route_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Route Data Successfully Updated', 'alert-success')
            return redirect('route')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Route_Details(View):
    template_name = 'master/route_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        route_det = RouteMaster.objects.get(route_id=pk)
        context = {'route_det': route_det}
        return render(request, self.template_name, context)  

class Route_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(RouteMaster, route_id=pk)
        return render(request, 'master/route_delete.html', {'route': rec})
    
    def post(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(RouteMaster, route_id=pk)
        rec.delete()
        messages.success(request, 'Route Deleted Successfully', 'alert-success')
        return redirect('route')
  

class Designation_List(View):
    template_name = 'master/designation_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        designation_li = DesignationMaster.objects.filter()
        context = {'designation_li': designation_li}
        return render(request, self.template_name, context)
    
class Designation_Create(View):
    template_name = 'master/designation_create.html'
    form_class = Designation_Create_Form

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            messages.success(request, 'Designation Successfully Added.', 'alert-success')
            return redirect('designation')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Designation_Edit(View):
    template_name = 'master/designation_edit.html'
    form_class = Designation_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = DesignationMaster.objects.get(designation_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = DesignationMaster.objects.get(designation_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Designation Data Successfully Updated', 'alert-success')
            return redirect('designation')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Designation_Details(View):
    template_name = 'master/designation_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        designation_det = DesignationMaster.objects.get(designation_id=pk)
        context = {'designation_det': designation_det}
        return render(request, self.template_name, context)
 
class Designation_Delete(View):
    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        del_designation = get_object_or_404(DesignationMaster, designation_id=pk)
        return render(request, 'master/designation_delete.html', {'del': del_designation})

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        designation_del = get_object_or_404(DesignationMaster, designation_id=pk)
        designation_del.delete()
        messages.success(request, 'Designation Successfully Deleted.', 'alert-success')
        return redirect('designation')
       
def branch(request):
    context = {}
    return render(request, 'master/branch_list.html',context)
    
class Location_List(View):
    template_name = 'master/locations_list.html'

    def get(self, request, *args, **kwargs):
        location_li = LocationMaster.objects.all()
        context = {'location_li': location_li}
        return render(request, self.template_name, context)

class Location_Adding(View):
    template_name = 'master/location_add.html'
    form_class = Location_Add_Form

    def get(self, request, *args, **kwargs):
        emirate_values = EmirateMaster.objects.all()
        print(emirate_values)
        context = {'emirate_values': emirate_values}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        print(" check valid")
        try:
            if form.is_valid():
                data = form.save(commit=False)
                branch_id=request.user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                data.branch_id = branch
                data.created_by = str(request.user)
                data.save()
                messages.success(request, 'Location Successfully Added.', 'alert-success')
                return redirect('locations_list')
            else:
                messages.success(request, 'Data is not valid.', 'alert-danger')
                context = {'form': form}
                return render(request, self.template_name, context)
        except Exception as e:
            print(":::::::::::::::::::::::",e)


class Location_Edit(View):
    template_name = 'master/location_edit.html'
    form_class = Location_Edit_Form

    def get(self, request, pk, *args, **kwargs):
        rec = LocationMaster.objects.get(location_id=pk)
        form = self.form_class(instance=rec)
        emirate_values = EmirateMaster.objects.all()  # Queryset for populating emirate dropdown
        context = {'form': form, 'emirate_values': emirate_values}
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        rec = LocationMaster.objects.get(location_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            messages.success(request, 'Location Data Successfully Updated', 'alert-success')
            return redirect('locations_list')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)


class Location_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = LocationMaster.objects.get(location_id=pk)
        return render(request, 'master/location_delete.html', {'location': rec})
    
    def post(self, request, pk, *args, **kwargs):
        rec = LocationMaster.objects.get(location_id=pk)
        rec.delete()
        messages.success(request, 'Location Data Deleted Successfully', 'alert-success')
        return redirect('locations_list')
    

        
class Category_List(View):
    template_name = 'master/category_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        category_li = CategoryMaster.objects.filter()
        context = {'category_li': category_li}
        return render(request, self.template_name, context)

class Category_Create(View):
    template_name = 'master/category_create.html'
    form_class = Category_Create_Form

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user.id)
            data.save()
            messages.success(request, 'Category Successfully Added.', 'alert-success')
            return redirect('category')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Category_Edit(View):
    template_name = 'master/category_edit.html'
    form_class = Category_Edit_Form

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        rec = CategoryMaster.objects.get(category_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        rec = CategoryMaster.objects.get(category_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Category Data Successfully Updated', 'alert-success')
            return redirect('category')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class Category_Details(View):
    template_name = 'master/category_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        category_det = CategoryMaster.objects.get(category_id=pk)
        context = {'category_det': category_det}
        return render(request, self.template_name, context)
    
# def create_emirates():
#     EmirateMaster.objects.create(created_by = "default",name = "Abudhabi")
#     EmirateMaster.objects.create(created_by = "default",name = "Dubai")
#     EmirateMaster.objects.create(created_by = "default",name = "Sharjah")
#     EmirateMaster.objects.create(created_by = "default",name = "Ajman")
#     EmirateMaster.objects.create(created_by = "default",name = "Fujeriah")
#     EmirateMaster.objects.create(created_by = "default",name = "RAK")
#     EmirateMaster.objects.create(created_by = "default",name = "UAQ")
# create_emirates()
def privacy(request):
    """
    Privacy instance.
    """
    try:
        instance = PrivacyPolicy.objects.all().latest("created_date")
    except:
        instance = PrivacyPolicy.objects.none
    
    context = {
        'instance': instance
    }
    return render(request, 'master/privacy.html', context)

def privacy_list(request):
    """
    View to list all Privacy instances.
    """
    instances = PrivacyPolicy.objects.all()
    context = {
        'instances': instances
    }
    return render(request, 'master/privacy_list.html', context)

def privacy_create(request):
    """
    View to create a new Privacy instance.
    """
    if request.method == 'POST':
        form = PrivacyForm(request.POST)
        if form.is_valid():
            privacy = form.save(commit=False)
            privacy.created_by = request.user
            privacy.save()
            return redirect('privacy_list')
    else:
        form = PrivacyForm()

    return render(request, 'master/privacy_create.html', {'form': form})

def privacy_edit(request, pk):
    """
    View to edit an existing privacy instance.
    """
    instance = get_object_or_404(PrivacyPolicy, pk=pk)
    if request.method == 'POST':
        form = PrivacyForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('privacy_list')
    else:
        form = PrivacyForm(instance=instance)
    return render(request, 'master/privacy_edit.html', {'form': form})

def privacy_delete(request, pk):
    """
    View to delete an existing privacy instance.
    """
    instance = get_object_or_404(PrivacyPolicy, pk=pk)
    if request.method == 'POST':
        instance.delete()
        return redirect('privacy_list')
    return render(request, 'master/privacy_delete.html', {'instance': instance})

def terms_and_conditions(request):
    """
    terms and conditions instance.
    """
    try:
        instance = TermsAndConditions.objects.all().latest("created_date")
    except:
        instance = TermsAndConditions.objects.none
    
    context = {
        'instance': instance
    }
    return render(request, 'master/terms_and_conditions.html', context)

def terms_and_conditions_list(request):
    """
    View to list all TermsAndConditions instances.
    """
    instances = TermsAndConditions.objects.all()
    context = {
        'instances': instances
    }
    return render(request, 'master/terms_and_conditions_list.html', context)

def terms_and_conditions_create(request):
    """
    View to create a new TermsAndConditions instance.
    """
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST)
        if form.is_valid():
            terms_and_conditions = form.save(commit=False)
            terms_and_conditions.created_by = request.user
            terms_and_conditions.save()
            return redirect('terms_and_conditions_list')
    else:
        form = TermsAndConditionsForm()

    return render(request, 'master/terms_and_conditions_create.html', {'form': form})

def terms_and_conditions_edit(request, pk):
    """
    View to edit an existing TermsAndConditions instance.
    """
    instance = get_object_or_404(TermsAndConditions, pk=pk)
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('terms_and_conditions_list')
    else:
        form = TermsAndConditionsForm(instance=instance)
    return render(request, 'master/terms_and_conditions_edit.html', {'form': form})

def terms_and_conditions_delete(request, pk):
    """
    View to delete an existing TermsAndConditions instance.
    """
    instance = get_object_or_404(TermsAndConditions, pk=pk)
    if request.method == 'POST':
        instance.delete()
        return redirect('terms_and_conditions_list')
    return render(request, 'master/terms_and_conditions_delete.html', {'instance': instance})