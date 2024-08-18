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
from django.db.models import Sum
from . serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication 
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from van_management.models import Van, VanProductStock , VanCouponStock
from customer_care.models import DiffBottlesModel
from client_management.models import CustomerSupply, CustomerOutstandingReport, CustomerSupplyCoupon
from sales_management.models import CollectionItems
from invoice_management.models import Invoice
from coupon_management.models import CouponStock


# Create your views here.
@login_required(login_url='login')
def home(request):
    template_name = 'master/dashboard.html'
    
    # Get the total count of all vans
    total_vans = Van.objects.count()
    
    # Get the total count of all customers
    total_customers = Customers.objects.count()
    
    # Calculate the date 10 days ago
    ten_days_ago = timezone.now() - timedelta(days=10)
    
    # Get the count of customers created exactly 10 days ago
    new_customers_count = Customers.objects.filter(created_date__date=ten_days_ago.date()).count()
    
    # Get the total count of emergency customers
    today = timezone.now().date()
    emergency_customers = DiffBottlesModel.objects.filter(delivery_date=today)
    emergency_customer_ids = {ec.customer_id for ec in emergency_customers}
    total_emergency_customers = Customers.objects.filter(customer_id__in=emergency_customer_ids).count()
    
    # Get the total sales for today filtered by cash and credit
    cash_sales = CustomerSupply.objects.filter(created_date__date=today,customer__sales_type='CASH').count()
    credit_sales = CustomerSupply.objects.filter(created_date__date=today,customer__sales_type='CREDIT').count()
    total_sales = cash_sales + credit_sales
    
    # Get the total returns for today filtered by cash and credit
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
    
    
    
    
    context = {
        'total_vans': total_vans,
        'total_customers': total_customers,
        'new_customers_count': new_customers_count,
        'total_emergency_customers': total_emergency_customers,
        'cash_sales': cash_sales,
        'credit_sales': credit_sales,
        'total_sales': total_sales,
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
        'scrap_bottle_collected_today':scrap_bottle_collected_today,
        'bottle_in_service_today':bottle_in_service_today,
        'company_fresh_stock':company_fresh_stock,
        'manual_book_sold':manual_book_sold,
        'digital_book_sold':digital_book_sold,
        'manual_coupons_collected':manual_coupons_collected,
        'digital_coupons_collected':digital_coupons_collected,

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