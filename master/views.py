import json
import uuid
import datetime
from datetime import timedelta
from django.utils.timezone import now
from calendar import monthrange

from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum,Count,F
from django.shortcuts import render, redirect
from django.db import transaction, IntegrityError
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from django.db.models.functions import ExtractWeekDay
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,Count,F,Q,DecimalField
from django.db.models.functions import ExtractDay,TruncDate
from django.shortcuts import render, redirect, get_object_or_404

from invoice_management.models import Invoice

from .forms import *
from .models import *
from . serializers import *
from accounts.models import *
from customer_care.models import *
from sales_management.models import CollectionPayment
from van_management.models import Van, VanProductStock , Expense
from product.models import ProductStock, ScrapProductStock, WashedUsedProduct, WashingProductStock
from client_management.models import CustomerOutstanding, OutstandingAmount, Vacation, NonvisitReport,CustomerSupplyItems
from client_management.models import CustodyCustomItems, CustomerSupply,CustomerCoupon, CustomerSupplyCoupon, CustomerSupplyDigitalCoupon, OutstandingCoupon, OutstandingProduct
from apiservices.views import find_customers

@login_required(login_url='login')
def home(request):
    context={}

    return render(request, 'master/dashboard.html', context)


def overview(request):
    # Get the date from the request or use today's date
    date = request.GET.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        date = datetime.today().date()
        
    yesterday_date = date - timedelta(days=1)
    
    # supply
    todays_supply_instances = CustomerSupply.objects.filter(created_date__date=date)
    supply_cash_sales_instances = todays_supply_instances.filter(amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON")
    supply_credit_sales_instances = todays_supply_instances.filter(amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"])
    # recharge
    todays_recharge_instances = CustomerCoupon.objects.filter(created_date__date=date)
    recharge_cash_sales_instances = todays_recharge_instances.filter(amount_recieved__gt=0)
    recharge_credit_sales_instances = todays_recharge_instances.filter(amount_recieved__lte=0)
    # total cash and credit
    total_cash_sales_count = supply_cash_sales_instances.count() + recharge_cash_sales_instances.count()
    total_credit_sales_count = supply_credit_sales_instances.count() + recharge_credit_sales_instances.count()
    # total collection
    total_supply_cash_sales = supply_cash_sales_instances.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
    total_rechage_cash_sales = recharge_cash_sales_instances.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
    total_today_collections = total_supply_cash_sales + total_rechage_cash_sales
    # old collections
    old_payment_collections_instances = CollectionPayment.objects.filter(created_date__date=date)
    total_old_payment_collections = old_payment_collections_instances.aggregate(total_amount_recieved=Sum('amount_received'))['total_amount_recieved'] or 0
    # expences
    expenses_instanses = Expense.objects.filter(expense_date=date)
    total_expences = expenses_instanses.aggregate(total_expense=Sum('amount'))['total_expense'] or 0
    # active vans
    active_vans_ids = VanProductStock.objects.filter(stock__gt=0).values_list('van__pk').distinct()
    active_van_count = Van.objects.filter(pk__in=active_vans_ids).count()
    
    customers_instances = Customers.objects.all()
    vocation_customers_instances = Vacation.objects.all()
    # scheduled customers
    route_instances = RouteMaster.objects.all()
    todays_customers = []
    yesterday_customers = []
        
    for route in route_instances:
        # todays
        day_of_week = date.strftime('%A')
        week_num = (date.day - 1) // 7 + 1
        week_number = f'Week{week_num}'
        
        today_vocation_customer_ids = vocation_customers_instances.filter(start_date__gte=date,end_date__lte=date).values_list('customer__pk')
        today_scheduled_customers = customers_instances.filter(routes=route, is_calling_customer=False).exclude(pk__in=today_vocation_customer_ids)
        
        for customer in today_scheduled_customers:
            if customer.visit_schedule:
                for day, weeks in customer.visit_schedule.items():
                    if str(day_of_week) == str(day) and str(week_number) in weeks:
                        todays_customers.append(customer)
                        
        # yesterdays
        y_day_of_week = yesterday_date.strftime('%A')
        y_week_num = (yesterday_date.day - 1) // 7 + 1
        y_week_number = f'Week{y_week_num}'
        
        yesterday_vocation_customer_ids = vocation_customers_instances.filter(start_date__gte=yesterday_date,end_date__lte=yesterday_date).values_list('customer__pk')
        yesterday_scheduled_customers = customers_instances.filter(routes=route, is_calling_customer=False).exclude(pk__in=yesterday_vocation_customer_ids)
        
        for customer in yesterday_scheduled_customers:
            if customer.visit_schedule:
                for day, weeks in customer.visit_schedule.items():
                    if str(y_day_of_week) == str(day) and str(y_week_number) in weeks:
                        yesterday_customers.append(customer)
                        
    door_lock_count = NonvisitReport.objects.filter(created_date__date=date,reason__reason_text="Door Lock").count()
    emergency_customers_count = customers_instances.filter(pk__in=DiffBottlesModel.objects.filter(delivery_date=date).values_list('customer__pk')).count()
    
    new_customers_count_with_salesman = (Customers.objects.filter(created_date__date=date).values('sales_staff__username').annotate(customer_count=Count('customer_id')).order_by('sales_staff__username'))
    
    # sales section
    total_cash_sales_amount = supply_cash_sales_instances.aggregate(total_amount=Sum('subtotal'))['total_amount'] or 0
    total_credit_sales_amount = supply_cash_sales_instances.aggregate(total_amount=Sum('subtotal'))['total_amount'] or 0
    total_sales_grand_total = total_cash_sales_amount + total_credit_sales_amount
    total_reachage_sales_amount = CustomerCoupon.objects.filter(created_date__date=date).aggregate(total_amount=Sum('total_payeble'))['total_amount'] or 0
    
    total_old_payment_cash_collections = old_payment_collections_instances.filter(customer__sales_type="CASH").aggregate(total_amount_recieved=Sum('amount_received'))['total_amount_recieved'] or 0
    total_old_payment_credit_collections = old_payment_collections_instances.filter(customer__sales_type="CREDIT").aggregate(total_amount_recieved=Sum('amount_received'))['total_amount_recieved'] or 0
    total_old_payment_coupon_collections = old_payment_collections_instances.filter(customer__sales_type="CASH COUPON").aggregate(total_amount_recieved=Sum('amount_received'))['total_amount_recieved'] or 0
    
    today_outstangings = OutstandingAmount.objects.filter(customer_outstanding__created_date__date=date)
    total_cash_outstanding_amounts = today_outstangings.filter(customer_outstanding__customer__sales_type="CASH").aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_credit_outstanding_amounts = today_outstangings.filter(customer_outstanding__customer__sales_type="CREDIT").aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    total_outstanding_amounts = total_cash_outstanding_amounts + total_credit_outstanding_amounts
    total_coupon_outstanding_amounts = today_outstangings.filter(customer_outstanding__customer__sales_type="CASH COUPON").aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    
    # Calculate weekly sales for each day
    def get_sales_per_day_for_week(start_date):
        end_date = start_date + timedelta(weeks=1)
        
        # Query supply sales
        supply_sales = CustomerSupply.objects.filter(
            created_date__date__range=[start_date, end_date]
        ).annotate(weekday=ExtractWeekDay('created_date')).values('weekday').annotate(count=Count('id')).order_by('weekday')
        
        # Query coupon sales
        coupon_sales = CustomerCoupon.objects.filter(
            created_date__date__range=[start_date, end_date]
        ).annotate(weekday=ExtractWeekDay('created_date')).values('weekday').annotate(count=Count('id')).order_by('weekday')
        
        # Initialize combined sales
        combined_sales = {i: 0 for i in range(1, 8)}  # Weekdays from 1 (Sunday) to 7 (Saturday)

        # Populate combined sales from supply sales
        for sale in supply_sales:
            combined_sales[sale['weekday']] += sale['count']
        
        # Populate combined sales from coupon sales
        for sale in coupon_sales:
            combined_sales[sale['weekday']] += sale['count']
        
        # Prepare the output in the required format
        return [{'weekday': k, 'count': v} for k, v in combined_sales.items()]

    # Get start dates for the current and last three weeks
    this_week_start = date.today() - timedelta(days=date.today().weekday())
    last_week_start = this_week_start - timedelta(weeks=1)
    second_last_week_start = this_week_start - timedelta(weeks=2)
    third_last_week_start = this_week_start - timedelta(weeks=3)

    # Fetch sales data for the current and last three weeks
    this_week_sales = get_sales_per_day_for_week(this_week_start)
    last_week_sales = get_sales_per_day_for_week(last_week_start)
    second_last_week_sales = get_sales_per_day_for_week(second_last_week_start)
    third_last_week_sales = get_sales_per_day_for_week(third_last_week_start)

    # Get the first and last day of the current month for the previous year
    last_year_start = (date.today().replace(year=date.today().year - 1)).replace(day=1)
    last_year_end = (last_year_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # Query for last year's sales aggregated by day
    last_year_sales = CustomerSupply.objects.filter(
        created_date__date__range=[last_year_start, last_year_end]
    ).annotate(day=ExtractDay('created_date')).values('day').annotate(count=Count('id')).order_by('day')

    # Convert to desired format
    last_year_sales_day_wise = [{'day': sale['day'], 'count': sale['count']} for sale in last_year_sales]

    # If you want to ensure all days are represented (e.g., even days with 0 sales)
    # Prepare a full list of days in the month
    num_days = monthrange(last_year_start.year, last_year_start.month)[1]
    full_sales_data = [{'day': day, 'count': 0} for day in range(1, num_days + 1)]

    # Fill in actual sales data
    for sale in last_year_sales_day_wise:
        full_sales_data[sale['day'] - 1] = {'day': sale['day'], 'count': sale['count']}
        
    # Convert sales data to JSON string for JavaScript
    this_week_sales_json = json.dumps(this_week_sales)
    last_week_sales_json = json.dumps(last_week_sales)
    second_last_week_sales_json = json.dumps(second_last_week_sales)
    third_last_week_sales_json = json.dumps(third_last_week_sales)
    last_year_monthly_avg_sales_json = json.dumps(full_sales_data)
    
    # Bottle Section
    today_supply_bottle_count = CustomerSupplyItems.objects.filter(product__product_name="5 Gallon",customer_supply__pk__in=todays_supply_instances.values_list("pk")).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    today_custody_issued_count = CustodyCustomItems.objects.filter(product__product_name="5 Gallon",custody_custom__created_date__date=date).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    today_empty_bottle_collected_count = todays_supply_instances.aggregate(total_qty=Sum('collected_empty_bottle'))['total_qty'] or 0
    today_pending_bottle_given_count = todays_supply_instances.aggregate(total_qty=Sum('allocate_bottle_to_pending'))['total_qty'] or 0
    today_pending_bottle_collected_count = max(today_supply_bottle_count - today_empty_bottle_collected_count, 0)
    today_outstanding_bottle_count = OutstandingProduct.objects.filter(customer_outstanding__created_date__date=date).aggregate(total_qty=Sum('empty_bottle'))['total_qty'] or 0
    today_scrap_bottle_count = ScrapProductStock.objects.filter(created_date__date=date).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    today_service_bottle_count = WashingProductStock.objects.filter(created_date__date=date).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    today_fresh_bottle_stock = ProductStock.objects.filter(product_name__product_name="5 Gallon").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    total_used_bottle_count = WashedUsedProduct.objects.filter(product__product_name="5 Gallon").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    salesmans_instances = CustomUser.objects.filter(pk__in=todays_supply_instances.values_list('salesman__pk'))
    salesman_sales_serializer = SalesmanSupplyCountSerializer(salesmans_instances,many=True,context={"date": date}).data
    
    # Coupon Section
    manual_coupon_sold_instances = todays_recharge_instances.filter(coupon_method="manual")
    digital_coupon_sold_instances = todays_recharge_instances.filter(coupon_method="digital")
    manual_coupon_sold_count = manual_coupon_sold_instances.count()
    digital_coupon_sold_count = digital_coupon_sold_instances.count()
    collected_manual_coupons_count = CustomerSupplyCoupon.objects.filter(customer_supply__pk__in=todays_supply_instances.values_list("pk")).aggregate(Count('leaf'))['leaf__count']
    collected_manual_coupons_count += CustomerSupplyCoupon.objects.filter(customer_supply__pk__in=todays_supply_instances.values_list("pk")).aggregate(Count('free_leaf'))['free_leaf__count']
    collected_digital_coupons_count = CustomerSupplyDigitalCoupon.objects.filter(customer_supply__pk__in=todays_supply_instances.values_list("pk")).aggregate(total_count=Sum('count'))['total_count'] or 0
    today_manual_coupon_outstanding_count = OutstandingCoupon.objects.filter(customer_outstanding__created_date__date=date).exclude(coupon_type__coupon_type_name="Digital").aggregate(total_count=Sum('count'))['total_count'] or 0
    today_digital_coupon_outstanding_count = OutstandingCoupon.objects.filter(customer_outstanding__created_date__date=date,coupon_type__coupon_type_name="Digital").aggregate(total_count=Sum('count'))['total_count'] or 0
    today_supply_quantity_ex_foc_count = CustomerSupplyItems.objects.filter(product__product_name="5 Gallon",customer_supply__pk__in=todays_supply_instances.values_list("pk"),customer_supply__customer__sales_type="CASH COUPON").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    collected_total_coupon = collected_manual_coupons_count + collected_digital_coupons_count
    
    today_pending_manual_coupons_count = 0
    today_pending_digital_coupons_count = 0
    if today_supply_quantity_ex_foc_count < collected_total_coupon:
        today_pending_manual_coupons_count = today_supply_quantity_ex_foc_count - collected_manual_coupons_count
        today_pending_digital_coupons_count = today_supply_quantity_ex_foc_count - collected_digital_coupons_count
        
    today_pending_manual_coupons_collected_count = 0
    today_pending_digital_coupons_collected_count = 0
    if collected_total_coupon > today_supply_quantity_ex_foc_count:
        today_pending_manual_coupons_collected_count = collected_manual_coupons_count - today_supply_quantity_ex_foc_count
        today_pending_digital_coupons_collected_count = collected_digital_coupons_count - today_supply_quantity_ex_foc_count
    
    coupon_salesmans_instances = CustomUser.objects.filter(pk__in=CustomerCoupon.objects.filter(created_date__date=date).values_list('salesman__pk'))
    salesman_recharge_serializer = SalesmanRechargeCountSerializer(coupon_salesmans_instances,many=True,context={"date": date}).data
    
    # Customer  statistics
    call_customers_count = customers_instances.filter(is_calling_customer=True).count()
    # inactive_customers_count = customers_instances.filter(is_active=False).count()
    
    today = now().date()
    start_of_month = today.replace(day=1)

    route_data = Customers.objects.filter(routes__route_name__isnull=False).values(
        'routes__route_name'
    ).annotate(
        today_new_customers=Count('customer_id', filter=Q(created_date__date=today)),
        month_new_customers=Count('customer_id', filter=Q(created_date__date__gte=start_of_month))
    )
    
    last_20_days = today - timedelta(days=20)

        # Get all the routes
    routes = RouteMaster.objects.all()

        # Initialize a dictionary to store the inactive customers count by route
    route_inactive_customer_count = {}
    inactive_customers_count = 0
    for route in routes:
            # Get the customers associated with this route
        route_customers = Customers.objects.filter(routes=route)

            # Get customers who haven't had a supply in the last 20 days
        visited_customers = CustomerSupply.objects.filter(
                created_date__date__range=(last_20_days, today)
            ).values_list('customer_id', flat=True)

        todays_customers = find_customers(request, str(today), route.pk) or []
        todays_customer_ids = {customer['customer_id'] for customer in todays_customers}

            # Filter out customers who had a supply in the last 20 days or today
        inactive_customers = route_customers.exclude(
                pk__in=visited_customers
            ).exclude(
                pk__in=todays_customer_ids
            )

            # Add the count of inactive customers for this route
        route_inactive_customer_count[route.route_name] = inactive_customers.count()
        inactive_customers_count += inactive_customers.count()


    non_visited_customers_data = []

    for route in route_instances:
        
        today_vocation_customer_ids = vocation_customers_instances.filter(start_date__lte=date, end_date__gte=date).values_list('customer__pk', flat=True)
        scheduled_customers = customers_instances.filter(
            routes=route,
            is_calling_customer=False
        ).exclude(pk__in=today_vocation_customer_ids)
        
        scheduled_customers_filtered = []
        for customer in scheduled_customers:
            if customer.visit_schedule:
                for day, weeks in customer.visit_schedule.items():
                    if str(day_of_week) == str(day) and str(week_number) in weeks:
                        scheduled_customers_filtered.append(customer.pk)
                        
        # Get non-visited customers
        non_visited_customers = set(scheduled_customers_filtered) - set(
            NonvisitReport.objects.filter(
                created_date__date=date, 
                customer__routes=route
            ).values_list('customer__pk', flat=True)
        )
        
        # Append route and non-visited customer count to the list
        non_visited_customers_data.append({
            'route': route.route_name,
            'non_visited_customers_count': len(non_visited_customers)
        })
        
    pending_complaints_count = CustomerComplaint.objects.filter(status='Pending').count()
    
    context = {
        # overview section
        "cash_sales": total_cash_sales_count,
        "credit_sales": total_credit_sales_count,
        "total_sales_count": total_cash_sales_count + total_credit_sales_count,
        "today_expenses": total_expences,
        "total_today_collections": total_today_collections,
        "total_old_payment_collections": total_old_payment_collections,
        "total_collection": total_today_collections + total_old_payment_collections,
        "total_cash_in_hand": total_today_collections + total_old_payment_collections - total_expences,
        "active_van_count": active_van_count,
        "delivery_progress": f'{supply_cash_sales_instances.count() + supply_credit_sales_instances.count()} / {len(todays_customers)}',
        "total_customers_count": customers_instances.count(),
        "new_customers_count": customers_instances.filter(created_date__date=date).count(),
        "door_lock_count": door_lock_count,
        "emergency_customers_count": emergency_customers_count,
        "total_vocation_customers_count": len(vocation_customers_instances.filter(start_date__gte=date,end_date__lte=date).values_list('customer__pk').distinct()),        
        "yesterday_missed_customers_count": len(yesterday_customers) - CustomerSupply.objects.filter(created_date__date=yesterday_date).count(),
        "new_customers_count_with_salesman": [
            {
                "salesman_names": item['sales_staff__username'] if item['sales_staff__username'] else "Unassigned",
                "customer_count": item['customer_count']
            }
            for item in new_customers_count_with_salesman
        ],
        # sales section
        "total_cash_sales_amount": total_cash_sales_amount,
        "total_credit_sales_amount": total_credit_sales_amount,
        "total_sales_grand_total": total_sales_grand_total,
        "total_reachage_sales_amount": total_reachage_sales_amount,
        "total_rechage_collections": total_rechage_cash_sales,
        "total_old_payment_cash_collections": total_old_payment_cash_collections,
        "total_old_payment_credit_collections": total_old_payment_credit_collections,
        "total_old_payment_grand_total_collections": total_old_payment_cash_collections + total_old_payment_credit_collections,
        "total_old_payment_coupon_collections": total_old_payment_coupon_collections,
        "total_cash_outstanding_amounts": total_cash_outstanding_amounts,
        "total_credit_outstanding_amounts": total_credit_outstanding_amounts,
        "total_outstanding_amounts": total_outstanding_amounts,
        "total_coupon_outstanding_amounts": total_coupon_outstanding_amounts,
        'this_week_sales': this_week_sales_json,
        'last_week_sales': last_week_sales_json,
        'second_last_week_sales': second_last_week_sales_json,
        'third_last_week_sales': third_last_week_sales_json,
        'last_year_monthly_avg_sales': last_year_monthly_avg_sales_json,
        # Bottle Section 
        "today_supply_bottle_count": today_supply_bottle_count,
        "today_custody_issued_count": today_custody_issued_count,
        "today_pending_bottle_given_count": today_pending_bottle_given_count,
        "today_pending_bottle_collected_count": today_pending_bottle_collected_count,
        "today_outstanding_bottle_count": today_outstanding_bottle_count,
        "today_scrap_bottle_count": today_scrap_bottle_count,
        "today_service_bottle_count": today_service_bottle_count,
        "today_fresh_bottle_stock": today_fresh_bottle_stock,
        "total_used_bottle_count": total_used_bottle_count,
        "salesman_sales_serializer": json.dumps(salesman_sales_serializer),
        # Coupon Sections
        "manual_coupon_sold_count": manual_coupon_sold_count,
        "digital_coupon_sold_count": digital_coupon_sold_count,
        "collected_manual_coupons_count": collected_manual_coupons_count,
        "collected_digital_coupons_count": collected_digital_coupons_count,
        "today_manual_coupon_outstanding_count": today_manual_coupon_outstanding_count,
        "today_digital_coupon_outstanding_count": today_digital_coupon_outstanding_count,
        "today_pending_manual_coupons_count": today_pending_manual_coupons_count,
        "today_pending_digital_coupons_count": today_pending_digital_coupons_count,
        "today_pending_manual_coupons_collected_count": today_pending_manual_coupons_collected_count,
        "today_pending_digital_coupons_collected_count": today_pending_digital_coupons_collected_count,
        "salesman_recharge_serializer": json.dumps(salesman_recharge_serializer),
        # Customer  statistics
        "call_customers_count": call_customers_count,
        "inactive_customers_count" : inactive_customers_count,
        "route_data" : route_data,
        "route_inactive_customer_count" : route_inactive_customer_count,
        "non_visited_customers_data": non_visited_customers_data,
        "pending_complaints_count":pending_complaints_count,
    }

    return render(request, 'master/dashboard/overview_dashboard.html', context) 


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
        username=request.POST.get('username')
        password=request.POST.get('pswd')
        hashed_password=make_password(password)
        
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            
            try:
                with transaction.atomic():
                    auth_data=CustomUser.objects.create(
                    username=username,
                    first_name=username,
                    password=hashed_password,
                    user_type='Branch User')
                    
                    data = form.save(commit=False)
                    data.created_by = str(request.user.id)
                    data.user_id = auth_data
                    data.save()
                    
                    auth_data.branch_id=data
                    auth_data.save()
                    
            except IntegrityError as e:
                # Handle database integrity error
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }
            except Exception as e:
                # Handle other exceptions
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": str(e),
                }
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

class AmountChangesCustomersList(View):
    template_name = 'master/amount_changes_customer_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        mismatched_customers = []
        route_li = RouteMaster.objects.all()
        filter_data = {}
        
        if request.GET.get('route_name'):
            filter_data['route_filter'] = request.GET.get('route_name')
            
            # Fetch customers in the specified route
            customer_instances = Customers.objects.filter(routes__route_name=request.GET.get('route_name'))

            for customer_instance in customer_instances:
                # Calculate outstanding amount
                outstanding = OutstandingAmount.objects.filter(
                    customer_outstanding__customer=customer_instance,
                    customer_outstanding__product_type="amount"
                ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

                # Calculate total collection amount
                collection = CollectionPayment.objects.filter(
                    customer=customer_instance
                ).aggregate(total_amount_received=Sum('amount_received'))['total_amount_received'] or 0

                # Calculate outstanding balance
                outstanding_balance = outstanding - collection

                # Fetch all invoices for the customer
                invoice_instances = Invoice.objects.filter(
                    customer=customer_instance,
                    is_deleted=False
                )

                # Calculate invoice balance
                invoice_balance = sum(
                    invoice.amout_total - invoice.amout_recieved for invoice in invoice_instances
                )

                # Check for mismatch
                if outstanding_balance != invoice_balance:
                    mismatched_customers.append({
                        'customer': customer_instance,
                        'outstanding_balance': outstanding_balance,
                        'invoice_balance': invoice_balance
                    })

        context = {
            'instances': mismatched_customers,
            'route_li': route_li,
            'filter_data': filter_data,
        }
        return render(request, self.template_name, context)


from datetime import time
from django.utils.timezone import localtime
class AmountChangesList(View):
    template_name = 'master/amount_changes_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        customer = request.GET.get("customer_pk")
        
        # Retrieve dates from both CustomerSupply, Invoice, and CustomerOutstanding models
        supply_dates = CustomerSupply.objects.filter(customer__pk=customer).values_list("created_date", flat=True)
        invoice_dates = Invoice.objects.filter(customer__pk=customer, is_deleted=False).values_list("created_date", flat=True)
        outstanding_dates = CustomerOutstanding.objects.filter(customer__pk=customer).values_list("created_date", flat=True)
        collection_dates = CollectionPayment.objects.filter(customer__pk=customer).values_list("created_date", flat=True)
        
        # Combine and remove duplicates by using a set, filter out midnight dates, then sort the dates
        unique_dates = sorted(
            {localtime(created_date).date() for created_date in supply_dates if created_date} |
            {localtime(created_date).date() for created_date in invoice_dates if created_date} |
            {localtime(created_date).date() for created_date in outstanding_dates if created_date} |
            {localtime(created_date).date() for created_date in collection_dates if created_date}
        )

        # Add the dates to the context
        context = {
            'instances': unique_dates,
            'customer': customer, 
        }
        return render(request, self.template_name, context)