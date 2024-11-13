import json
import uuid
import datetime
from datetime import timedelta
from calendar import monthrange

from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum,Count
from django.shortcuts import render, redirect
from django.db import transaction, IntegrityError
from django.db.models.functions import ExtractDay
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from django.db.models.functions import ExtractWeekDay
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import *
from .models import *
from . serializers import *
from accounts.models import *
from customer_care.models import DiffBottlesModel
from sales_management.models import CollectionPayment
from van_management.models import Van, VanProductStock , Expense
from product.models import ProductStock, ScrapProductStock, WashedUsedProduct, WashingProductStock
from client_management.models import OutstandingAmount, Vacation, NonvisitReport,CustomerSupplyItems
from client_management.models import CustodyCustomItems, CustomerSupply,CustomerCoupon, CustomerSupplyCoupon, CustomerSupplyDigitalCoupon, OutstandingCoupon, OutstandingProduct



# Create your views here.
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
    supply_cash_sales_instances = CustomerSupply.objects.filter(created_date__date=date,amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON")
    supply_credit_sales_instances = CustomerSupply.objects.filter(created_date__date=date,amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"])
    # recharge
    recharge_cash_sales_instances = CustomerCoupon.objects.filter(created_date__date=date,amount_recieved__gt=0)
    recharge_credit_sales_instances = CustomerCoupon.objects.filter(created_date__date=date,amount_recieved__lte=0)
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
    
    context = {
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
    }

    return render(request, 'master/dashboard/overview_dashboard.html', context) 



class Branch_List(View):
    template_name = 'master/branch_list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        branch_li = BranchMaster.objects.all().order_by("-created_date")
        context = {'branch_li': branch_li}
        log_activity(request.user, "Viewed branch list.")
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
            log_activity(
                        created_by=request.user,
                        description=f"Branch ID {rec.name} successfully edited by User ID {request.user}"
                    )
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
        log_activity(
                created_by=request.user,
                description=f"Viewed details for Branch ID {pk} by  User ID {request.user}"
            )
        return render(request, self.template_name, context)    
class Branch_Delete(View):

    def get(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(BranchMaster, branch_id=pk)
        return render(request, 'master/branch_delete.html', {'branch': rec})
    
    def post(self, request, pk, *args, **kwargs):
        rec = get_object_or_404(BranchMaster, branch_id=pk)
        rec.delete()
        log_activity(
                created_by=request.user,
                description=f"Branch ID {pk} deleted by User ID {request.user}"
            )
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