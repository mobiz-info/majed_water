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
from apiservices.views import find_customers
from van_management.models import Van_Routes,Van,VanProductStock
from django.contrib.auth import update_session_auth_hash

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
        

        instances = CustomUser.objects.exclude(user_type__in=['Customers','Customer','customers','customer'])
       
        context = {
            'instances': instances
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
        filter_data = {}
        # Retrieve the query parameter
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        customer_type_filter = request.GET.get('customer_type')

        # Start with all customers
        user_li = Customers.objects.all()
            
        # Apply filters if they exist
        if query:
            user_li = user_li.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )
            filter_data['q'] = query

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)
            filter_data['route_filter'] = route_filter
            
        if customer_type_filter:
            user_li = user_li.filter(sales_type=customer_type_filter)
            filter_data['customer_type'] = customer_type_filter

        # Get all route names for the dropdown
        route_li = RouteMaster.objects.all()
        
        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'route_filter': route_filter,
            'q': query,
            'filter_data': filter_data,
        }



        return render(request, self.template_name, context)
    
class Latest_Customer_List(View):
    template_name = 'accounts/latest_customer_list.html'

    def get(self, request, *args, **kwargs):
        filter_data = {}
        
        query = request.GET.get("q")
        route_filter = request.GET.get('route_name')
        customer_type_filter = request.GET.get('customer_type')

        ten_days_ago = datetime.now() - timedelta(days=10)
        user_li = Customers.objects.filter(created_date__gte=ten_days_ago)
        
        if request.GET.get('start_date'):
            start_date = request.GET.get('start_date')
        else:
            start_date = datetime.today().date()
            
        if request.GET.get('end_date'):
            end_date = request.GET.get('end_date')
        else:
            end_date = datetime.today().date()
        
        start_date = datetime.strptime(str(start_date), '%Y-%m-%d').date()   
        end_date = datetime.strptime(str(end_date), '%Y-%m-%d').date()
        
        filter_data["start_date"] = start_date.strftime('%Y-%m-%d') if start_date else None
        filter_data["end_date"] = end_date.strftime('%Y-%m-%d') if end_date else None
        
        user_li = user_li.filter(Q(created_date__date__range=[start_date, end_date]))
        
        if customer_type_filter:
            user_li = user_li.filter(sales_type=customer_type_filter)
            filter_data['customer_type'] = customer_type_filter

        if route_filter:
            user_li = user_li.filter(routes__route_name=route_filter)

        if query and query != "None":
            user_li = user_li.filter(
                Q(custom_id__icontains=query) |
                Q(customer_name__icontains=query) |
                Q(mobile_no__icontains=query) |
                Q(location__location_name__icontains=query) |
                Q(building_name__icontains=query)
            )
            filter_data['q'] = query

        route_li = RouteMaster.objects.all()
        
        context = {
            'user_li': user_li.order_by("-created_date"),
            'route_li': route_li,
            'route_filter': route_filter,
            'q': query,
        }

        return render(request, self.template_name, context)

class Inactive_Customer_List(View):
    template_name = 'accounts/inactive_customer_list.html'

    def get(self, request, *args, **kwargs):
        # Get filter data from request
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        route_name = request.GET.get('route_name')
        query = request.GET.get("q")
        filter_data = {}
        inactive_customers = []

        # Parse date filters
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            filter_data['from_date'] = from_date.strftime('%Y-%m-%d')
        else:
            from_date = datetime.today().date()
            filter_data['from_date'] = from_date.strftime('%Y-%m-%d')

        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            filter_data['to_date'] = to_date.strftime('%Y-%m-%d')
        else:
            to_date = datetime.today().date()
            filter_data['to_date'] = to_date.strftime('%Y-%m-%d')

        if route_name:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            if van_route:
                salesman_id = van_route.van.salesman.pk
                filter_data['route_name'] = route_name

                # Get customers who have made purchases within the date range
                visited_customers = CustomerSupply.objects.filter(
                    salesman_id=salesman_id,
                    created_date__date__range=(from_date, to_date)
                ).values_list('customer_id', flat=True)

                # Get all customers assigned to the route
                route_customers = Customers.objects.filter(routes=van_route.routes)

                # Filter out the visited customers
                inactive_customers = route_customers.exclude(pk__in=visited_customers)

                # Get today's planned customers
                todays_customers = find_customers(request, str(datetime.today().date()), van_route.routes.pk)
                todays_customer_ids = [customer['customer_id'] for customer in todays_customers]

                # Filter out today's planned customers from inactive customers
                inactive_customers = inactive_customers.exclude(pk__in=todays_customer_ids)

        if query and query != "None":
            query = query.lower()
            inactive_customers = inactive_customers.filter(
                custom_id__icontains=query
            ) | inactive_customers.filter(
                customer_name__icontains=query
            ) | inactive_customers.filter(
                building_name__icontains=query
            )
            filter_data['q'] = query

        context = {
            'inactive_customers': inactive_customers,
            'routes_instances': RouteMaster.objects.all(),
            'filter_data': filter_data,
            'data_filter': bool(route_name),
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

# class Customer_Details(View):
#     template_name = 'accounts/customer_details.html'

#     def get(self, request, pk, *args, **kwargs):
#         user_det = Customers.objects.get(customer_id=pk)
#         context = {'user_det': user_det}
#         return render(request, self.template_name, context) 

class Customer_Details(View):
    template_name = 'accounts/customer_details.html'

    def get(self, request, pk, *args, **kwargs):
        user_det = Customers.objects.get(customer_id=pk)
        visit_schedule = self.format_visit_schedule(user_det.visit_schedule)
        context = {'user_det': user_det, 'visit_schedule': visit_schedule}
        return render(request, self.template_name, context)

    def format_visit_schedule(self, visit_schedule):
        week_schedule = {}
        no_week_days = []

        for day, weeks in visit_schedule.items():
            if weeks == ['']:
                no_week_days.append(day)
            else:
                for week in weeks:
                    if week not in week_schedule:
                        week_schedule[week] = []
                    week_schedule[week].append(day)
        
        formatted_schedule = []
        
        if no_week_days:
            days = ', '.join(no_week_days)
            formatted_schedule.append(f"General: {days}")
        
        for week in sorted(week_schedule.keys(), reverse=True):
            days = ', '.join(week_schedule[week])
            formatted_schedule.append(f"{week}: {days}")
        return formatted_schedule

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
            previous_rate =cust_Data.rate

            if form.is_valid():
                print("previous_rate",previous_rate)
                data = form.save(commit=False)
                data.emirate = data.location.emirate
                data.save()
                
                # Create CustomerRateHistory entry
                CustomerRateHistory.objects.create(
                    customer=cust_Data,
                    previous_rate=previous_rate,
                    new_rate=data.rate,
                    created_by=request.user
                    )
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
            
        # print(visit_schedule_data)
        
    except Customers.DoesNotExist:
        messages.error(request, 'Customer does not exist.')
        return redirect('customers')
    
    if request.method == 'POST':
        # Initialize an empty dictionary to store the new visit schedule data
        visit_schedule_data = {day: [] for day in days_of_week}

        # Iterate over the days of the week and update the dictionary based on the POST data
        for week_number in "12345":
            week_key = f"Week{week_number}[]"
            selected_days = request.POST.getlist(week_key)
            for day in selected_days:
                visit_schedule_data[day].append(f"Week{week_number}")
                
        # Split the week strings into lists and ensure all weeks are individual elements
        for day in days_of_week:
            visit_schedule_data[day] = [
                week for weeks in visit_schedule_data[day]
                for week in weeks.split(',')
            ]
            
        # print(visit_schedule_data)

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


class CustomerRateHistoryListView(View):
    template_name = 'accounts/customer_rate_history.html'

    def get(self, request, *args, **kwargs):
        selected_route = request.GET.get('route_name')
        
        # Fetch all routes
        routes = RouteMaster.objects.all()

        # Fetch customer rate histories based on the selected route
        if selected_route:
            histories = CustomerRateHistory.objects.filter(customer__routes__route_name=selected_route).order_by('-created_date')
        else:
            histories = CustomerRateHistory.objects.all().order_by('-created_date')
        
        context = {
            'histories': histories,
            'routes': routes,
            'filter_data': {
                'selected_route': selected_route,
            },
        }
        return render(request, self.template_name, context)
    
class NonVisitedCustomersView(View):
    template_name = 'accounts/non_visited_customers.html'
    paginate_by = 50  # Optional: For pagination, you can set this value

    def get(self, request, *args, **kwargs):
        # Get filter data from request
        date = request.GET.get('date')
        route_name = request.GET.get('route_name')
        query = request.GET.get("q")
        filter_data = {}
        non_visited = []

        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
            
        
        if route_name:
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            if van_route:
                salesman_id = van_route.van.salesman.pk
                filter_data['route_name'] = route_name

                # Actual visit
                visited_customers = CustomerSupply.objects.filter(salesman_id=salesman_id, created_date__date=date)
                todays_customers = find_customers(request, str(date), van_route.routes.pk)
                # # Convert each dictionary to a tuple of items for hashing
                # planned_visit = set(tuple(customer.items()) for customer in todays_customers)
                # visited = set(visited_customers.values_list('customer_id', flat=True))
                # non_visited = list(planned_visit - visited)
                # Convert the data to dictionaries for easier processing
                todays_customers_dict = [dict(customer) for customer in todays_customers]
                visited_customers_ids = set(visited_customers.values_list('customer_id', flat=True))
                
                # Filter out visited customers
                non_visited = [customer for customer in todays_customers_dict if customer['customer_id'] not in visited_customers_ids]
        
        
        if query and query != "None":
            query = query.lower()
            # Ensure query is a string
            query_str = str(query)
            non_visited = [customer for customer in non_visited if (
                query_str in str(customer.get('custom_id', '')).lower() or
                query_str in str(customer.get('customer_name', '')).lower() or
                query_str in str(customer.get('mobile', '')).lower() or
                query_str in str(customer.get('location', '')).lower() or
                query_str in str(customer.get('building_name', '')).lower()
            )]
            filter_data['q'] = query
       
        context = {
            'non_visited': non_visited,
            'routes_instances': RouteMaster.objects.all(),
            'filter_data': filter_data,
            'data_filter': bool(route_name),
            'q': query,
        }

        return render(request, self.template_name, context)    


def change_password(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  
            log_activity(
                created_by=request.user.username, 
                description=f"Password changed for user: {user.username}"
            )
            return redirect('password_change_done')
        else:
            log_activity(
                created_by=request.user.username, 
                description=f"Failed password change attempt for user: {user.username}. Errors: {form.errors}"
            )
    else:
        form = CustomPasswordChangeForm(user=user)

    return render(request, 'accounts/change_password.html', {'form': form})


class MissingCustomersView(View):
    template_name = 'accounts/missing_customers.html'

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()  # Or pass this as an argument if needed

        routes = RouteMaster.objects.all()  # Get all RouteMaster instances
        route_data = []

        for route in routes:
            route_id = route.route_id  # Use route_id from RouteMaster
            actual_visitors = Customers.objects.filter(routes__pk=route_id, is_active=True).count()

            planned_visitors_list = find_customers(request, str(date), route_id)  # Ensure this returns a list
            planned_visitors = len(planned_visitors_list) if planned_visitors_list else 0

            supplied_customers = CustomerSupply.objects.filter(
                customer__routes__pk=route_id,
                created_date__date=date
            ).count()

            if isinstance(planned_visitors_list, list):
                todays_customers_dict = planned_visitors_list
            else:
                todays_customers_dict = []

            visited_customers_ids = set(
                CustomerSupply.objects.filter(
                    customer__routes__pk=route_id,
                    created_date__date=date
                ).values_list('customer_id', flat=True)
            )

            # Filter out visited customers
            missed_customers = [
                customer for customer in todays_customers_dict 
                if customer['customer_id'] not in visited_customers_ids
            ]

            missed_customers_count = len(missed_customers)
            print("missed_customers_count", missed_customers_count)

            route_data.append({
                'route_name': route.route_name,  
                'actual_visitors': actual_visitors,
                'planned_visitors': planned_visitors,
                'missed_customers': missed_customers_count,
                'supplied_customers': supplied_customers,
                'route_id': route.route_id  
            })

        context = {
            'route_data': route_data
        }

        return render(request, self.template_name, context)

class MissingCustomersPdfView(View):
    template_name = 'accounts/missing_customers_pdf.html'

    def get(self, request, *args, **kwargs):
        date = datetime.now().date()  

        routes = RouteMaster.objects.all()  
        route_data = []

        for route in routes:
            route_id = route.route_id
            actual_visitors = Customers.objects.filter(routes__pk=route_id, is_active=True).count()

            planned_visitors_list = find_customers(request, str(date), route_id)  # Ensure this returns a list
            planned_visitors = len(planned_visitors_list) if planned_visitors_list else 0

            supplied_customers = CustomerSupply.objects.filter(
                customer__routes__pk=route_id,
                created_date__date=date
            ).count()

            if isinstance(planned_visitors_list, list):
                todays_customers_dict = planned_visitors_list
            else:
                todays_customers_dict = []

            visited_customers_ids = set(
                CustomerSupply.objects.filter(
                    customer__routes__pk=route_id,
                    created_date__date=date
                ).values_list('customer_id', flat=True)
            )

            missed_customers = [
                customer for customer in todays_customers_dict
                if customer['customer_id'] not in visited_customers_ids
            ]

            missed_customers_count = len(missed_customers)

            route_data.append({
                'route_name': route.route_name,
                'actual_visitors': actual_visitors,
                'planned_visitors': planned_visitors,
                'missed_customers': missed_customers_count,
                'supplied_customers': supplied_customers,
                'route_id': route.route_id
            })

        context = {
            'route_data': route_data
        }
        return render(request, self.template_name, context)


        
class MissedOnDeliveryView(View):
    template_name = 'accounts/missed_on_delivery.html'

    def get(self, request, route_id, *args, **kwargs):
        date = timezone.now().date()
        van_route = get_object_or_404(Van_Routes, routes__route_id=route_id)
        print("van_route",van_route)
        planned_customers = find_customers(request, str(date), route_id)

        supplied_customers_ids = CustomerSupply.objects.filter(
            customer__routes__route_id=route_id,
            created_date__date=date
        ).values_list('customer_id', flat=True)

        missed_customers = []
        for customer in planned_customers:
            if customer['customer_id'] not in supplied_customers_ids:
                last_supply = CustomerSupply.objects.filter(
                    customer_id=customer['customer_id']
                ).order_by('-created_date').last()

                last_sold_date = last_supply.created_date if last_supply else None

                # Get the reason for non-visit if exists
                non_visit_report = NonvisitReport.objects.filter(
                    customer_id=customer['customer_id'],
                    supply_date=date
                ).last()

                reason_for_non_visit = non_visit_report.reason if non_visit_report else None

                customer['last_sold_date'] = last_sold_date
                customer['reason_for_non_visit'] = reason_for_non_visit
                missed_customers.append(customer)

        context = {
            'missed_customers': missed_customers,
            'route_id': route_id
        }

        return render(request, self.template_name, context)


class MissedOnDeliveryPrintView(View):
    
    template_name = 'accounts/missed_on_delivery_print.html'

    
    def get(self, request, route_id, *args, **kwargs):
        date = timezone.now().date()
        van_route = get_object_or_404(Van_Routes, routes__route_id=route_id)

        planned_customers = find_customers(request, str(date), route_id)

        supplied_customers_ids = CustomerSupply.objects.filter(
            customer__routes__route_id=route_id,
            created_date__date=date
        ).values_list('customer_id', flat=True)

        missed_customers = []
        for customer in planned_customers:
            if customer['customer_id'] not in supplied_customers_ids:
                last_supply = CustomerSupply.objects.filter(
                    customer_id=customer['customer_id']
                ).order_by('-created_date').last()

                last_sold_date = last_supply.created_date if last_supply else None

                # Get the reason for non-visit if exists
                non_visit_report = NonvisitReport.objects.filter(
                    customer_id=customer['customer_id'],
                    supply_date=date
                ).last()

                reason_for_non_visit = non_visit_report.reason if non_visit_report else None

                customer['last_sold_date'] = last_sold_date
                customer['reason_for_non_visit'] = reason_for_non_visit
                missed_customers.append(customer)

        context = {
            'missed_customers': missed_customers,
            'route_id':route_id,
        }

        return render(request, self.template_name, context)

def log_activity(created_by, description, created_date=None):
    
    if created_date is None:
        created_date = timezone.now()

    Processing_Log.objects.create(
        created_by=created_by,
        description=description,
        created_date=created_date
    )

def processing_log_list(request):
    logs = Processing_Log.objects.all().order_by("-created_date")
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'accounts/processing_log_list.html', context)