import uuid
import json
import base64
import datetime

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse

from competitor_analysis.forms import CompetitorAnalysisFilterForm
from master.functions import generate_form_errors, get_custom_id
from .forms import *
from .models import *
from django.db.models import Q
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from client_management.models import *
from django.db.models import Q, Sum, Count
from customer_care.models import *


# Create your views here.
def user_login(request):
    template_name = 'registration/user_login.html'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = CustomUser.objects.get(username = username)
        user = authenticate(username=username, password=password)
        # print("::::::::::::::::::::::::::",user)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                context = {'error_msg': 'Invalid Username or Password'}
                return render(request, template_name, context)
        else:
            context = {'error_msg': 'User Doest Not exist'}
            return render(request, template_name, context)
        
    return render(request, template_name)   

class UserLogout(View):

    def get(self, request):
        try:
            logout(request)
            messages.success(request, 'Successfully logged out', extra_tags='success')
            return redirect("login")
        except Exception as e:
            # Handle exceptions if necessary
            messages.error(request, 'An error occurred while logging out', extra_tags='danger')
            return redirect("login")
        
class Users_List(View):
    template_name = 'accounts/user_list.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")

        instances = CustomUser.objects.filter(user_type__in=['Driver','Salesman','Supervisor','Manager','Customer Care','Accounts'])
        if query:
            instances = instances.filter(
                Q(first_name__icontains=query) |
                Q(designation_id__designation_name__icontains=query) |
                Q(staff_id__icontains=query) |
                Q(username__icontains=query) |
                Q(branch_id__name__icontains=query) 
            )

        context = {
            'instances': instances,
            'q': query
            }
        return render(request, self.template_name, context)

class User_Create(View):
    template_name = 'accounts/user_create.html'
    form_class = User_Create_Form

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            passw = make_password(data.password)
            data.password = passw
            data.save()
            messages.success(request, 'User Successfully Added.', 'alert-success')
            return redirect('users')
        else:
            #print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Field: {field}, Error: {error}")
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)


class User_Edit(View):
    template_name = 'accounts/user_edit.html'
    form_class = User_Edit_Form

    def get(self, request, pk, *args, **kwargs):
        rec = CustomUser.objects.get(id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        rec = CustomUser.objects.get(id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            #data.modified_by = request.user
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'User Data Successfully Updated', 'alert-success')
            return redirect('users')
        else:
            #print(form.errors)
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)

class User_Details(View):
    template_name = 'accounts/user_details.html'

    def get(self, request, pk, *args, **kwargs):
        user_det = CustomUser.objects.get(id=pk)
        context = {'user_det': user_det}
        return render(request, self.template_name, context)  
    
class User_Delete(View):
    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=pk)
        return render(request, 'accounts/user_delete.html', {'user': user})

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=pk)
        user.delete()
        messages.success(request, 'User Successfully Deleted.', 'alert-success')
        return redirect('users')
# class Customer_List(View):
#     template_name = 'accounts/customer_list.html'

#     def get(self, request, *args, **kwargs):
#         # Create an instance of the form and populate it with GET data
#         form = CompetitorAnalysisFilterForm(request.GET)
        
#         user_li = Customers.objects.all()
#         query = request.GET.get("q")
#         if query:
#             user_li = user_li.filter(
#                 Q(customer_name__icontains=query) |
#                 Q(mobile_no__icontains=query) |
#                 Q(routes__route_name__icontains=query) |
#                 Q(location__location_name__icontains=query)|
#                 Q(building_name__icontains=query)
#             )

#         # Check if the form is valid
#         # if form.is_valid():
#             # Filter the queryset based on the form data
#         route_filter = request.GET.get('route_name')
#         if route_filter :
#             user_li = Customers.objects.filter(routes__route_name=route_filter)
#         # else:
#         #         user_li = Customers.objects.all()
#         # else:
#         #     # If the form is not valid, retrieve all customers
#         #     user_li = Customers.objects.all()
#         route_li = RouteMaster.objects.all()
#         context = {'user_li': user_li, 'form': form, 'route_li': route_li}
#         return render(request, self.template_name, context)

# class Customer_List(View):
#     template_name = 'accounts/customer_list.html'

#     def get_next_visit_date(self, customer):
#         try:
#             staff_day_of_visit = Staff_Day_of_Visit.objects.get(customer=customer)
#             # Logic to determine the next visit date based on the visit schedule
#             # For demonstration purposes, let's assume the next visit is 7 days from today
#             next_visit_date = timezone.now() + timezone.timedelta(days=7)
#             return next_visit_date
#         except Staff_Day_of_Visit.DoesNotExist:
#             # Handle the case where no staff day of visit is found
#             return None

#     def get(self, request, *args, **kwargs):
#         # Retrieve the query parameter
#         query = request.GET.get("q")
#         route_filter = request.GET.get('route_name')
#         # Start with all customers
#         user_li = Customers.objects.all()

#         # Apply filters if they exist
#         if query:
#             user_li = user_li.filter(
#                 Q(custom_id__icontains=query) |
#                 Q(customer_name__icontains=query) |
#                 Q(mobile_no__icontains=query) |
#                 Q(routes__route_name__icontains=query) |
#                 Q(location__location_name__icontains=query) |
#                 Q(building_name__icontains=query)
#             )

#         if route_filter:
#             user_li = user_li.filter(routes__route_name=route_filter)

#         # Get all route names for the dropdown
#         route_li = RouteMaster.objects.all()

#         # Iterate over each customer and get the next visit date
#         for customer in user_li:
#             next_visit_date = self.get_next_visit_date(customer)
#             customer.next_visit_date = next_visit_date  # Add the next visit date to the customer object

#         context = {
#             'user_li': user_li.order_by("-created_date"), 
#             'route_li': route_li,
#             'route_filter': route_filter,
#             'q': query,
#         }
#         return render(request, self.template_name, context)
class Customer_List(View):
    template_name = 'accounts/customer_list.html'

    def get(self, request, *args, **kwargs):
        # Retrieve the query parameter
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')

        # Start with all customers
        user_li = Customers.objects.all()
        
            
        # Apply filters if they exist
        if query:
            user_li = user_li.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(routes__route_name__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)

        # Get all route names for the dropdown
        route_li = RouteMaster.objects.all()
        
        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'route_filter': route_filter,
            'q': query,
        }



        return render(request, self.template_name, context)
    

class CustomerComplaintView(View):
    template_name = 'accounts/customer_complaint.html'

    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customers, customer_id=pk)
        complaints = CustomerComplaint.objects.filter(customer=customer)
        return render(request, self.template_name, {'customer': customer, 'complaints': complaints})

    def post(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customers, customer_id=pk)
        complaint_id = request.POST.get('complaint_id')
        status = request.POST.get('status')
        complaint = get_object_or_404(CustomerComplaint, id=complaint_id, customer=customer)
        if status == "Completed":
            complaint.status = status
            complaint.save()
        return redirect('customer_complaint', pk=pk)


def create_customer(request):
    branch = request.user.branch_id
    template_name = 'accounts/create_customer.html'
    form = CustomercreateForm(branch)
    context = {"form":form}
    # try:
    if request.method == 'POST':
        form = CustomercreateForm(branch,data = request.POST)
        context = {"form":form}
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = str(request.user)
            data.created_date = datetime.now()
            data.emirate = data.location.emirate
            branch_id=request.user.branch_id.branch_id
            branch = BranchMaster.objects.get(branch_id=branch_id)
            data.branch_id = branch
            data.custom_id = get_custom_id(Customers)
            data.save()
            Staff_Day_of_Visit.objects.create(customer = data)
            messages.success(request, 'Customer Created successfully!')
            return redirect('customers')
        else:
            messages.success(request, 'Invalid form data. Please check the input.')
            return render(request, template_name,context)
    return render(request, template_name,context)
    # except Exception as e:
    #         messages.success(request, 'Something went wrong')
    #         return render(request, template_name,context)
def load_locations(request):
    emirate_id = request.GET.get('emirate_id')
    locations = LocationMaster.objects.filter(emirate__pk=emirate_id).all()
    return JsonResponse(list(locations.values('location_id', 'location_name')), safe=False)

class Customer_Details(View):
    template_name = 'accounts/customer_details.html'

    def get(self, request, pk, *args, **kwargs):
        user_det = Customers.objects.get(customer_id=pk)
        context = {'user_det': user_det}
        return render(request, self.template_name, context) 
    

def edit_customer(request,pk):
    branch = request.user.branch_id
    cust_Data = Customers.objects.get(customer_id = pk)
    form = CustomerEditForm(branch,instance = cust_Data)
    template_name = 'accounts/edit_customer.html'
    context = {"form":form}
    try:
        if request.method == 'POST':
            form = CustomerEditForm(branch,instance = cust_Data,data = request.POST)
            context = {"form":form}
            if form.is_valid():
                data = form.save(commit=False)
                data.emirate = data.location.emirate
                data.save()
                messages.success(request, 'Customer Details Updated successfully!')
                return redirect('customers')
            else:
                messages.success(request, 'Invalid form data. Please check the input.')
                return render(request, template_name,context)
        return render(request, template_name,context)
    except Exception as e:
        print(":::::::::::::::::::::::",e)
        messages.success(request, 'Something went wrong')
        return render(request, template_name,context)

def delete_customer(request,pk):
    cust_Data = Customers.objects.get(customer_id = pk)
    cust_Data.delete()
    
    response_data = {
        "status": "true",
        "title": "Successfully Deleted",
        "message": "Customer Successfully Deleted.",
        "redirect": "true",
        "redirect_url": reverse('customers'),
    }
    
    return HttpResponse(json.dumps(response_data), content_type='application/javascript')

from accounts.templatetags.accounts_templatetags import get_next_visit_day

def customer_list_excel(request):
    query = request.GET.get("q")
    route_filter = request.GET.get('route_name')
    user_li = Customers.objects.all()

    # Apply filters if they exist
    if query and query != '' and query != 'None':
        user_li = user_li.filter(
            Q(custom_id__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(mobile_no__icontains=query) |
            Q(routes__route_name__icontains=query) |
            Q(location__location_name__icontains=query) |
            Q(building_name__icontains=query)
        )
    
    print('route_filter :', route_filter)
    if route_filter and route_filter != '' and route_filter != 'None':
        user_li = user_li.filter(routes__route_name=route_filter)

    # Get all route names for the dropdown
    route_li = RouteMaster.objects.all()
    
    data = {
        'Serial Number': [],
        'Customer ID': [],
        'Customer name': [],
        'Route': [],
        'Location': [],
        'Mobile No': [],
        'Building Name': [],
        'House No': [],
        'Bottles stock': [],
        'Next Visit date': [],  # Create an empty list for next visit dates
        'Sales Type': [],
    }

    for serial_number, customer in enumerate(user_li, start=1):
        next_visit_date = get_next_visit_day(customer.pk)
        custody_count = 0
        outstanding_bottle_count = 0

        if (custody_stock:=CustomerCustodyStock.objects.filter(customer=customer,product__product_name="5 Gallon")).exists() :
            custody_count = custody_stock.first().quantity 

        if (outstanding_count:=CustomerOutstandingReport.objects.filter(customer=customer,product_type="emptycan")).exists() :
            outstanding_bottle_count = outstanding_count.first().value

        last_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).order_by('-customer_supply__created_date').values_list('quantity', flat=True).first() or 0

        total_bottle_count = custody_count + outstanding_bottle_count + last_supplied_count 
        print("final_bottle_count",total_bottle_count)
        data['Serial Number'].append(serial_number)
        data['Customer ID'].append(customer.custom_id)
        data['Customer name'].append(customer.customer_name)
        data['Route'].append(customer.routes.route_name if customer.routes else '')
        data['Location'].append(customer.location.location_name if customer.location else '')
        data['Mobile No'].append(customer.mobile_no)
        data['Building Name'].append(customer.building_name)
        data['House No'].append(customer.door_house_no if customer.door_house_no else 'Nil')
        data['Bottles stock'].append(total_bottle_count)
        data['Next Visit date'].append(next_visit_date)
        data['Sales Type'].append(customer.sales_type)

    df = pd.DataFrame(data)

    # Excel writing code...

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=4)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        table_border_format = workbook.add_format({'border':1})
        worksheet.conditional_format(4, 0, len(df.index)+4, len(df.columns) - 1, {'type':'cell', 'criteria': '>', 'value':0, 'format':table_border_format})
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 16, 'border': 1})
        worksheet.merge_range('A1:K2', f'Majed Water', merge_format)
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        worksheet.merge_range('A3:K3', f'    Customer List   ', merge_format)
        # worksheet.merge_range('E3:H3', f'Date: {def_date}', merge_format)
        # worksheet.merge_range('I3:M3', f'Total bottle: {total_bottle}', merge_format)
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        worksheet.merge_range('A4:K4', '', merge_format)
    
    filename = f"Customer List.xlsx"
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'inline; filename = "{filename}"'
    return response

# def visit_days_assign(request,customer_id):
#     template_name = 'accounts/assign_dayof_visit.html'
#     customer_data=Customers.objects.get(customer_id = customer_id)
#     day_visits = Staff_Day_of_Visit.objects.get(customer_id__customer_id = customer_id)
#     form = Day_OfVisit_Form(instance=day_visits)
#     context = {'day_visits' : day_visits,"form":form,"customer_data":customer_data}
#     if request.method == 'POST':
#         context = {'day_visits' : day_visits,"form":form,"customer_data":customer_data}
#         form = Day_OfVisit_Form(request.POST,instance=day_visits)
#         if form.is_valid():
#             data = form.save(commit=False)
#             data.created_by = str(request.user)
#             data.created_date = datetime.now()
#             data.save()
#             messages.success(request, 'Day of visit updated successfully!')
#             return redirect('customers')
#         else:
#             messages.success(request, 'Invalid form data. Please check the input.')
#             return render(request, template_name,context)
#     return render(request,template_name ,context)


# def visit_days_assign(request, customer_id):
#     template_name = 'accounts/assign_dayof_visit.html'
    
#     try:
#         customer_data = Customers.objects.get(customer_id=customer_id)
#         visit_schedule_data = customer_data.visit_schedule
        
#         if visit_schedule_data is not None:
#             if isinstance(visit_schedule_data, str):
#                 visit_schedule_data = json.loads(visit_schedule_data)
#                 print(visit_schedule_data)
#             else:
#                 print("Visit schedule data is already a dictionary.")
#                 # Handle the case where visit_schedule_data is already a dictionary
            
#         else:
#             print("Visit schedule data is None.")
#     except Customers.DoesNotExist:
#         messages.error(request, 'Customer does not exist.')
#         return redirect('customers')
    
#     if request.method == 'POST':
#         visit_schedule_data = {}
#         for week_number in "1234":
#             selected_days = []
#             for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
#                 checkbox_name = f'week{week_number}[]'
#                 if checkbox_name in request.POST:
#                     if day in request.POST.getlist(checkbox_name):
#                         selected_days.append(day)
#             visit_schedule_data["week" + week_number] = selected_days

#         # Convert the dictionary to JSON
#         visit_schedule_json = json.dumps(visit_schedule_data)

#         # Save the JSON data to the database field
#         customer_data.visit_schedule = visit_schedule_json
#         customer_data.save()

#         messages.success(request, 'Visit schedule updated successfully!')
#         return redirect('customers')
    
#     # Render the form if it's a GET request
#     context = {
#         "customer_data": customer_data,
#         "visit_schedule_data": visit_schedule_data
#     }
#     return render(request, template_name, context)


def visit_days_assign(request, customer_id):
    template_name = 'accounts/assign_dayof_visit.html'
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    try:
        customer_data = Customers.objects.get(customer_id=customer_id)
        visit_schedule_data = customer_data.visit_schedule

        if visit_schedule_data is not None:
            if isinstance(visit_schedule_data, str):
                visit_schedule_data = visit_schedule_data
        else:
            visit_schedule_data = {}  # Initialize an empty dictionary if it's None
            
        print(visit_schedule_data)
        
    except Customers.DoesNotExist:
        messages.error(request, 'Customer does not exist.')
        return redirect('customers')
    
    if request.method == 'POST':
        # Initialize an empty dictionary to store the new visit schedule data
        visit_schedule_data = {day: [] for day in days_of_week}

        # Iterate over the days of the week and update the dictionary based on the POST data
        for week_number in "1234":
            week_key = f"Week{week_number}[]"
            selected_days = request.POST.getlist(week_key)
            for day in selected_days:
                visit_schedule_data[day].append(f"Week{week_number}")
                
        # Convert lists to comma-separated strings and handle empty lists
        for day in days_of_week:
            if visit_schedule_data[day]:
                visit_schedule_data[day] = [",".join(visit_schedule_data[day])]
            else:
                visit_schedule_data[day] = [""]
                
        print(visit_schedule_data)

        # Save the JSON data to the database field
        customer_data.visit_schedule = visit_schedule_data
        customer_data.save()

        messages.success(request, 'Visit schedule updated successfully!')
        return redirect('customers')
    
    # Render the form if it's a GET request
    context = {
        "customer_data": customer_data,
        "visit_schedule_data": visit_schedule_data,
        "days_of_week": days_of_week
    }
    return render(request, template_name, context)