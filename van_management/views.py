from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from coupon_management.models import CouponStock
from coupon_management.serializers import couponStockSerializers
from .models import Van, Van_Routes, Van_License, BottleAllocation
from accounts.models import CustomUser, Customers
from master.models import EmirateMaster, RouteMaster
from customer_care.models import DiffBottlesModel
from client_management.models import Vacation,CustomerSupply
from product.models import ProductStock, ScrapProductStock, Staff_IssueOrders, WashingProductStock

from django.db import transaction, IntegrityError
from .forms import  *
import json
from django.core.serializers import serialize
from django.views import View
from datetime import datetime
from collections import defaultdict
from reportlab.pdfgen import canvas
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.db.models import Q,Count,Sum
from datetime import datetime
import math
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse

from .forms import BottleAllocationForm
from django.db.models import Max



def get_van_coupon_bookno(request):
    coupon_type = request.GET.get("productName")
    if (instances := VanCouponStock.objects.filter(coupon__coupon_type__coupon_type_name=coupon_type,stock__gt=0)).exists():
        instance = instances.values_list('coupon__pk')
        stock_instances = CouponStock.objects.filter(couponbook__pk__in=instance)
        serialized = couponStockSerializers(stock_instances, many=True)
        status_code = 200
        response_data = {
            "status": "true",
            "data": serialized.data,
        }
    else:
        status_code = 404
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "item not found",
        }

    return HttpResponse(json.dumps(response_data),status=status_code, content_type="application/json")


# Van
# def van(request):
#     all_van = Van.objects.all()
#     context = {'all_van': all_van}
#     return render(request, 'van_management/van.html', context)
def van(request):
    all_van = Van.objects.all()
    
    routes_assigned = {}  # Initialize an empty dictionary
    
    # print("All Vans:", all_van)  
    
    for van in all_van:
        van_routes = Van_Routes.objects.filter(van=van)
        route_names = [van_route.routes.route_name for van_route in van_routes]
        routes_assigned[van.van_id] = route_names
        
    # print("Routes Assigned:", routes_assigned)  
    context = {
        'all_van': all_van,
        'routes_assigned': routes_assigned,
    }
    
    # print("Context:", context)  
    
    return render(request, 'van_management/van.html', context)

def create_van(request):
    if request.method == 'POST':
        form = VanForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.branch_id = request.user.branch_id
            data.created_by = str(request.user.id)
            data.save()
            messages.success(request, 'Van created successfully!')
            return redirect('van')
        else:
            messages.error(request, 'Invalid form data. Please check the input.')
    else:
        form = VanForm()
    context = {'form': form}
    return render(request, 'van_management/create_van.html', context)

def edit_van(request, van_id):
    van = get_object_or_404(Van, van_id=van_id)
    if request.method == 'POST':
        form = EditVanForm(request.POST, instance=van)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.branch_id = request.user.branch_id
            data.save()
            return redirect('van')
    else:
        form = EditVanForm(instance=van)
    return render(request, 'van_management/edit_van.html', {'form': form, 'van': van})

def view_van(request, van_id):
    van = get_object_or_404(Van, van_id=van_id)
    return render(request, 'van_management/view_van.html', {'van': van})

def delete_van(request, van_id):
    van = Van.objects.get(van_id=van_id)
    if request.method == 'POST':
        van.delete()
        return redirect('van')
    return render(request, 'master/confirm_delete.html', {'van': van})



# Van staff assigning
def view_association(request):
    vans_with_associations = Van.objects.exclude(driver=None).exclude(salesman=None)
    return render(request, 'van_management/driver_salesman_list.html', {'vans_with_associations': vans_with_associations})

def create_association(request):
    if request.method == 'POST':
        form = VanAssociationForm(request.POST)
        if form.is_valid():
            van_instance = form.cleaned_data['van']
            driver_id = form.cleaned_data['driver']
            salesman_id = form.cleaned_data['salesman']
            van = get_object_or_404(Van, van_id=van_instance.van_id)
            driver_instance = get_object_or_404(CustomUser, id=driver_id)
            salesman_instance = get_object_or_404(CustomUser, id=salesman_id)
            van.driver = driver_instance
            van.salesman = salesman_instance
            van.save()
            return redirect('/van_assign')
    else:
        form = VanAssociationForm()
    return render(request, 'van_management/create_assign.html', {'form': form})


def edit_assign(request, van_id):
    van = get_object_or_404(Van, van_id=van_id)
    if request.method == 'POST':
        form = EditAssignForm(van, request.POST)
        if form.is_valid(): 
            driver_id = form.cleaned_data['driver']
            salesman_id = form.cleaned_data['salesman']
            driver_instance = get_object_or_404(CustomUser, id=driver_id)
            salesman_instance = get_object_or_404(CustomUser, id=salesman_id)
            van.driver = driver_instance
            van.salesman = salesman_instance
            van.save()
            return redirect('/van_assign')
    else:
        form = EditAssignForm(van)

    return render(request, 'van_management/edit_assign.html', {'form': form, 'van': van})



def delete_assign(request, van_id):
    van = Van.objects.get(van_id=van_id)
    if request.method == 'POST':
        van.driver = None
        van.salesman = None
        van.save()
        return redirect('/van_assign')
    return render(request, 'master/confirm_delete_assign.html', {'van': van})

def route_assign(request,van_id):
    form = VanAssignRoutesForm()
    all_van=Van_Routes.objects.filter(van__van_id = van_id)
    van_data = Van.objects.get(van_id = van_id)
    context = {'all_van' : all_van,"form":form,"van_data":van_data}
    if request.method == 'POST':
        form = VanAssignRoutesForm(request.POST)
        context = {'all_van' : all_van,"form":form,"van_data":van_data}
        if form.is_valid():
            data = form.save(commit=False)
            route = data.routes
            route_exists = Van_Routes.objects.filter(van = van_data,routes = route).exists()
            if route_exists:
                messages.success(request, 'Route is already assigned..')
                context = {'all_van' : all_van,"form":form,"van_data":van_data}
                return render(request, 'van_management/assignroute_tovan.html',context)
            data.van = van_data
            data.created_by = str(request.user)
            data.created_date = datetime.now()
            data.save()
            messages.success(request, 'Van Route Assigned successfully!')
            return redirect('route_assign',van_id)
        else:
            messages.success(request, 'Invalid form data. Please check the input.')
            return render(request, 'van_management/assignroute_tovan.html',context)
    return render(request, 'van_management/assignroute_tovan.html',context)

def delete_route_assign (request):
    van_route_id = request.POST.get('delete_id')
    van_id = request.POST.get('van_idd')
    van = Van_Routes.objects.get(van_route_id=van_route_id)
    if request.method == 'POST':
        van.delete()
        return redirect('route_assign',van_id)
    return render(request, 'master/confirm_delete.html',{'van': van} )





class Licence_List(View):
    template_name = 'van_management/licence_list.html'
    
    def get(self, request, *args, **kwargs):
        emirates = EmirateMaster.objects.all().order_by('emirate_id')
        licenses = Van_License.objects.all()
        vans = {}
        emirate_names = [emirate.name for emirate in emirates]  # List to store emirate names dynamically
        license_list = []
        # for license in licenses:
        #     van_plate = license.van.plate
        #     emirate_name = license.emirate.name
        #     emirate_id = license.emirate.emirate_id
        #     expiry_date = license.expiry_date
        
        # for license in licenses:
        #     lic= {'license_id':license.van_license_id,'van_plate':license.van.plate,
        #            'emirate_name':license.emirate,"expiry_date":license.expiry_date}
        #     license_list.append(lic)

        #     if van_plate not in vans:
        #         vans[van_plate] = {emirate: None for emirate in emirate_names}
        #     vans[van_plate][emirate_name] = expiry_date
        
        for license in licenses:
            if license.van:
                van_plate = license.van.plate
                emirate_name = license.emirate.name
                emirate_id = license.emirate.emirate_id
                expiry_date = license.expiry_date
            
            
                lic= {'license_id':license.van_license_id,'van_plate':license.van.plate,
                    'emirate_name':license.emirate,"expiry_date":license.expiry_date}
                license_list.append(lic)

                if van_plate not in vans:
                    vans[van_plate] = {emirate: None for emirate in emirate_names}
                vans[van_plate][emirate_name] = expiry_date
        
        return render(request, self.template_name, {'vans': vans, 'emirate_names': emirate_names,'license_list':license_list})
   
    

class Licence_Adding(View):
    template_name = 'van_management/licence_add.html'
    form_class = Licence_Add_Form

    def get(self, request, *args, **kwargs):
        emirate_values = EmirateMaster.objects.all()
        van = Van.objects.all()
        context = {'emirate_values': emirate_values, 'vans': van}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit = False )
            van_id = request.POST.get('van')
            license_no = request.POST.get('licence_no')
            emirate_id = request.POST.get('emirate')
            expiry_date = request.POST.get('expiry_date')
            van = Van.objects.get(van_id = van_id)
            emirate = EmirateMaster.objects.get(pk = emirate_id)
            data.created_by = str(request.user.id)
            data.license_no = license_no
            data.van = van
            data.emirate = emirate
            data.expiry_date = expiry_date
            data.save()
            messages.success(request, 'Licence Successfully Added.', 'alert-success')
            return redirect('licence_list')
        else:
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)
        
class License_Edit(View):
    template_name = 'van_management/licence_edit.html'
    form_class = Licence_Edit_Form

    def get(self, request, pk, *args, **kwargs):
        rec = Van_License.objects.get(van_license_id=pk)
        form = self.form_class(instance=rec)
        context = {'form': form,'rec':rec}
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        rec = Van_License.objects.get(van_license_id=pk)
        form = self.form_class(request.POST, request.FILES, instance=rec)
        if form.is_valid():
            data = form.save(commit=False)
            data.modified_by = str(request.user.id)
            data.modified_date = datetime.now()
            data.save()
            messages.success(request, 'Licence Successfully Updated', 'alert-success')
            return redirect('licence_list')
        else:
            messages.success(request, 'Data is not valid.', 'alert-danger')
            context = {'form': form}
            return render(request, self.template_name, context)
        
def licence_edit(request, plate):
    van = get_object_or_404(Van, plate=plate)
    van_id = van.van_id
    van_licence = Van_License.objects.filter(van=van)
    emirate = EmirateMaster.objects.all()
    if request.method == 'POST':
        emirate_id = request.POST.get('emirate')
        expiry_date = request.POST.get('expiry_date')
        existing_van_licence = Van_License.objects.filter(van=van, emirate_id=emirate_id).first()
        if existing_van_licence:
            existing_van_licence.expiry_date = expiry_date
            existing_van_licence.save()
        else:
            Van_License.objects.create(van=van, emirate_id=emirate_id, expiry_date=expiry_date)
        return redirect('licence_list')
    return render(request, 'van_management/licence_edit.html', {'emirate_values' : emirate})

# Need to remove 
def licence_delete(request, plate):
    van = get_object_or_404(Van, plate=plate)
    if request.method == 'POST':

        van = get_object_or_404(Van, plate=plate)
        van_id = van.van_id
        van_licence = Van_License.objects.filter(van_id = van_id)
        van_licence.delete()
        return redirect('licence_list')
    return render(request, 'van_management/licence_delete.html', {'van' : van})


# Trip schedule

def schedule_view(request):
    date_str = request.POST.get('date') if request.method == 'POST' else now().strftime('%Y-%m-%d')
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    routes = RouteMaster.objects.all()
    route_details = []
    
    for route in routes:
        todays_customers = find_customers(request, date_str, route.route_id)
        if todays_customers:
            customer_count = len(todays_customers)
            bottle_count = sum(customer['no_of_bottles'] if customer['no_of_bottles'] is not None else 0 for customer in todays_customers)
            trips = list(set(customer['trip'] for customer in todays_customers))
            trips.reverse()
            route_details.append({
                'route_name': route.route_name,
                'route_id': route.route_id,
                'no_of_customers': customer_count,
                'no_of_bottles': bottle_count,
                'no_of_trips': len(trips),
                'trips': trips
            })
    
    return render(request, 'van_management/schedule_view.html', {'def_date': date_str, 'details': route_details})

            
def schedule_by_route(request, def_date, route_id, trip):
    route = RouteMaster.objects.get(route_id = route_id)
    todays_customers = find_customers(request, def_date, route_id)
    customers = []
    for customer in todays_customers:
        if customer['trip'] == trip:
            customers.append(customer)
    totale_bottle=0
    no_of_bottles=0
    for customer in customers:
        if customer['no_of_bottles'] :
            no_of_bottles = customer['no_of_bottles']
        totale_bottle+=no_of_bottles
    return render(request, 'van_management/schedule_by_route.html', {
        'def_date':def_date,  
        'route':route, 
        'todays_customers' :customers, 
        'trip':trip, 
        'totale_bottle':totale_bottle })
    


def find_customers(request, def_date, route_id):
    date_str = def_date
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date.strftime('%A')
        week_num = (date.day - 1) // 7 + 1
        week_number = f'Week{week_num}'
    route = RouteMaster.objects.get(route_id=route_id)

    van_route = Van_Routes.objects.filter(routes=route).first()
    if van_route:
        van_capacity = van_route.van.capacity
    else:
        van_capacity = 200
    todays_customers = []

    buildings = []
    for customer in Customers.objects.filter(routes = route):
        if customer.visit_schedule and day_of_week in customer.visit_schedule and week_number in customer.visit_schedule[day_of_week]:
            todays_customers.append(customer)
            if customer.building_name not in buildings:
                buildings.append(customer.building_name)

    # Customers on vacation
    date = datetime.strptime(def_date, '%Y-%m-%d').date()
    for vacation in Vacation.objects.all():
        if vacation.start_date <= date <= vacation.end_date:
            if vacation.customer in todays_customers:
                todays_customers.remove(vacation.customer)

    # Emergency customer
    special_customers = DiffBottlesModel.objects.filter(delivery_date = date)
    emergency_customers = []
    for client in special_customers:
        if client.customer in todays_customers:
            emergency_customers.append(client.customer)
        else:
            if client.customer.routes == route:
                todays_customers.append(client.customer)
                emergency_customers.append(client.customer)
                if client.customer.building_name not in buildings:
                    buildings.append(client.customer.building_name)
    co = 0
    for cus in todays_customers:
        if cus.no_of_bottles_required:
            co+=cus.no_of_bottles_required
    # print(route,co)
    
    if not len(buildings) == 0:
        building_count = {}

        for building in buildings:
            for customer in todays_customers:
                if customer.building_name == building:
                    if building in building_count:
                        building_count[building] += customer.no_of_bottles_required
                    else:
                        building_count[building] = customer.no_of_bottles_required


        building_gps = []

        for building, bottle_count in building_count.items():
            c = Customers.objects.filter(building_name=building, routes=route).first()
            gps_longitude = c.gps_longitude
            gps_latitude = c.gps_latitude
            building_gps.append((building, gps_longitude, gps_latitude, bottle_count))

        sorted_building_gps = sorted(building_gps, key=lambda x: (x[1] if x[1] is not None else '', x[2] if x[2] is not None else ''))
        sorted_buildings = [item[0] for item in sorted_building_gps]
        sorted_building_count = dict(sorted(building_count.items(), key=lambda item: item[1]))

        trips = {}
        trip_count = 1
        current_trip_bottle_count = 0
        trip_buildings = []
        bottle_count = 0
        for building in sorted_buildings:
          
            for building_data in sorted_building_gps:
                if building_data[0]==building:
                    building = building_data[0]
                    if building_data[3]:
                        bottle_count = building_data[3]
                        
                    if current_trip_bottle_count + bottle_count > van_capacity:
                        trip_buildings = [building]
                        trip_count+=1
                        trips[f"Trip{trip_count}"] = trip_buildings
                        # print(route,"trip",trip_count)
                        current_trip_bottle_count = bottle_count
                    else:
                        
                        trip_buildings.append(building)
                        trips[f"Trip{trip_count}"] = trip_buildings
                        current_trip_bottle_count += bottle_count
            
        

        # Merge trips if possible to optimize
        merging_occurred = False
        for trip_num in range(1, trip_count + 1):
            for other_trip_num in range(trip_num + 1, trip_count + 1):
                trip_key = f"Trip{trip_num}"
                other_trip_key = f"Trip{other_trip_num}"
                combined_buildings = trips.get(trip_key, []) + trips.get(other_trip_key, [])
                total_bottles = sum(sorted_building_count.get(building, 0) for building in combined_buildings)
                if total_bottles <= van_capacity:
                    trips[trip_key] = combined_buildings
                    del trips[other_trip_key]
                    merging_occurred = True
                    break
            if merging_occurred:  
                break
                    
        # List to store trip-wise customer details
        trip_customers = []
        location_name = ""
        for trip in trips:
            for building in trips[trip]:
                for customer in todays_customers:
                    if customer.building_name == building:
                        if customer.location :
                            location_name = customer.location.location_name
                        trip_customer = {
                            "customer_name" : customer.customer_name,
                            "mobile":customer.mobile_no,
                            "trip":trip,
                            "building":customer.building_name,
                            "route" : customer.routes.route_name,
                            "no_of_bottles": customer.no_of_bottles_required,
                            "location" : location_name,
                            "building": customer.building_name,
                            "door_house_no": customer.door_house_no,
                            "floor_no": customer.floor_no,
                            "gps_longitude": customer.gps_longitude,
                            "gps_latitude": customer.gps_latitude,
                            "customer_type": customer.sales_type,
                            # 'rate': customer.rate,
                        }
                        if customer in emergency_customers:
                            trip_customer['type'] = 'Emergency'
                            dif = DiffBottlesModel.objects.filter(customer=customer, delivery_date=date).latest('created_date')
                            trip_customer['no_of_bottles'] = dif.quantity_required
                        else:
                            trip_customer['type'] = 'Default'
                        if customer.sales_type == 'CASH' or  customer.sales_type == 'CREDIT':
                            trip_customer['rate'] = customer.rate

                        trip_customers.append(trip_customer)
        return trip_customers
        
import math

def pdf_download(request, route_id, def_date, trip):
    route = RouteMaster.objects.get(route_id=route_id)
    customers = []
    todays_customers = find_customers(request, def_date, route_id)
    for customer in todays_customers:
        if customer['trip'] == trip:
            customers.append(customer)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    x_route_name, y_route_name = 80, 730
    formatted_date = datetime.strptime(def_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    p.setFont("Helvetica", 14)
    p.drawString(x_route_name, y_route_name, f"Client list for {route.route_name} --> {trip}")
    p.drawString(x_route_name + 380, y_route_name, f"{formatted_date}")
    line_y = y_route_name - 14
    p.line(x_route_name - 12, line_y, x_route_name + 450, line_y)

    x, y = 70, 700
    p.setFont("Helvetica", 9)
    p.drawString(x, y, "Si No")
    p.drawString(x + 30, y, "Client Name")
    p.drawString(x + 135, y, "Location")
    p.drawString(x + 200, y, "No of Bottles")
    p.drawString(x + 267, y, "Outstanding")
    p.drawString(x + 280, y-10, "Bottles")
    p.drawString(x + 330, y, "Outstanding")
    p.drawString(x + 337, y-10, "Coupons")
    p.drawString(x + 400, y, "Type")
    y -= 16
    p.line(x, y, x + 460, y)

    y -= 25
    counter = 1
    multiline_client = False  # Flag to track multiline client name in the row
    for customer in customers:
        if y <= 100:  
            p.showPage()  
            y = 700 
            
            
            # Draw headers on the new page
            p.setFont("Helvetica", 9)
            p.drawString(x, y, "Si No")
            p.drawString(x + 30, y, "Client Name")
            p.drawString(x + 135, y, "Location")
            p.drawString(x + 200, y, "No of Bottles")
            p.drawString(x + 267, y, "Outstanding")
            p.drawString(x + 280, y-10, "Bottles")
            p.drawString(x + 330, y, "Outstanding")
            p.drawString(x + 337, y-10, "Coupons")
            p.drawString(x + 400, y, "Type")
            y -= 16
            p.line(x, y, x + 460, y)
            y -= 50

        # Split the client name from the nearest space if it needs to be split into multiple lines
        client_name = customer['customer_name']
        client_name_parts = []
        if p.stringWidth(client_name, "Helvetica", 9) > 86:
            parts = client_name.split()
            current_line = parts[0]
            for part in parts[1:]:
                if p.stringWidth(current_line + ' ' + part, "Helvetica", 9) <= 86:
                    current_line += ' ' + part
                else:
                    client_name_parts.append(current_line)
                    current_line = part
            client_name_parts.append(current_line)
            multiline_client = True  # Set flag for multiline client name
        else:
            client_name_parts.append(client_name)

        if multiline_client:
            client_name_height = 10 * len(client_name_parts)
            cell_middle_y = y - client_name_height / 2
            p.drawString(x + 5, cell_middle_y + 6, str(counter))
        else:
            y -= 0
            
            p.drawString(x + 5, y, str(counter))
            
        # Draw the client name
        client_name_height = 10 * len(client_name_parts)
        for part in client_name_parts:
            p.drawString(x + 30, y, part)
            y -= 10
            

        # Adjust vertical position for the other cells if multiline client name is printed
        if multiline_client:
            cell_middle_y = y + client_name_height / 2
            cell_middle_y += 10
            p.drawString(x + 135, cell_middle_y, str(customer['location']))
            p.drawString(x + 220, cell_middle_y, str(customer['no_of_bottles']))
            p.drawString(x + 300, cell_middle_y, "")
            p.drawString(x + 350, cell_middle_y, "")
            p.drawString(x + 400, cell_middle_y, "Emergency" if customer['type'] == 'Emergency' else "Default")
        else:
            y += 10
            p.drawString(x + 135, y, str(customer['location']))
            p.drawString(x + 220, y, str(customer['no_of_bottles']))
            p.drawString(x + 300, y, "")
            p.drawString(x + 350, y, "")
            p.drawString(x + 400, y, "Emergency" if customer['type'] == 'Emergency' else "Default")
            y -= 20  # Adjust vertical position for the next entry

        # Draw horizontal line below each row
        p.line(x, y, x + 460, y)
        y -= 25
        counter += 1

    p.save()
    buffer.seek(0)

    filename = f"{route.route_name}_{def_date}_{trip}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def excel_download(request, route_id, def_date, trip):
    route = RouteMaster.objects.get(route_id=route_id)
    customers = []
    todays_customers = find_customers(request, def_date, route_id)
    
    # Manually generate serial numbers
    serial_number = 1
    for customer in todays_customers:
        if customer['trip'] == trip:
            customer['serial_number'] = serial_number
            customers.append(customer)
            serial_number += 1 

    # Prepare data for DataFrame
    data = {
        'Si No': [customer['serial_number'] for customer in customers],
        'Client Name': [customer['customer_name'] for customer in customers],
        'Mobile': [customer['mobile'] for customer in customers],
        'Locations': [customer['location'] for customer in customers],
        'Building': [customer['building'] for customer in customers],
        'Floor': [customer['floor_no'] for customer in customers],
        'Door': [customer['door_house_no'] for customer in customers],
        'No of Bottles': [customer['no_of_bottles'] for customer in customers],
        'Out- Bottles': [' ' for _ in customers],
        'Out- Coupons': [' ' for _ in customers],
        'Out- Cash': [' ' for _ in customers],
        'Rate': [customer.get('rate', '') for customer in customers],
        'Type': [customer['customer_type'] for customer in customers],
        'Delivery Type': [customer['type'] for customer in customers]
    }
    total_bottle=0
    no_of_bottles=0
    for customer in customers:
        if customer['no_of_bottles'] :
            no_of_bottles = customer['no_of_bottles']
        total_bottle+=no_of_bottles
    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=4)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        table_border_format = workbook.add_format({'border': 1})  
        worksheet.conditional_format(4, 0, len(df.index) + 4, len(df.columns) - 1, {'type': 'cell', 'criteria': '>', 'value': 0, 'format': table_border_format})

        # Merge cells and write other information with borders
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 16, 'border': 1})
        worksheet.merge_range('A1:N2', f'Majed Water', merge_format)
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        worksheet.merge_range('A3:D3', f'Route:    {route.route_name}    {trip}', merge_format)
        worksheet.merge_range('E3:I3', f'Date: {def_date}', merge_format)
        worksheet.merge_range('J3:N3', f'Total bottle: {total_bottle}', merge_format)
        merge_format = workbook.add_format({'align': 'center', 'bold': True, 'border': 1})
        worksheet.merge_range('A4:N4', '', merge_format)

    filename = f"{route.route_name}_{def_date}_{trip}.xlsx"
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
    



#Expence

class ExpenseHeadList(View):
    template_name = 'van_management/expensehead_list.html'
    def get(self, request, *args, **kwargs):
        expence_heads = ExpenseHead.objects.all()
        context = {'expence_heads':expence_heads}
        return render(request, self.template_name, context)



class ExpenseHeadAdd(View):
    template_name = 'van_management/expensehead_add.html'
    form_class = ExpenseHeadForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid:
            form.save()
            return redirect('expensehead_list')
        else:
            return render(request, self.template_name, {'form':form})
        

class ExpenseHeadEdit(View):
    template_name = 'van_management/expensehead_edit.html'
    form_class = ExpenseHeadForm

    def get(self, request, expensehead_id, *args, **kwargs):
        expensehead = ExpenseHead.objects.get(expensehead_id=expensehead_id)
        form = self.form_class(instance = expensehead)
        context = {'form':form, 'expensehead':expensehead}
        return render(request, self.template_name, context)

    def post(self, request, expensehead_id, *args, **kwargs):
       expensehead = ExpenseHead.objects.get(expensehead_id=expensehead_id)
       form = self.form_class(request.POST, instance=expensehead)
       if form.is_valid():
           form.save()
           return redirect('expensehead_list')
       else:
           context = {'form':form}
           return render(request, self.template_name, context)
       
class ExpenseHeadDelete(View):
    template_name = 'van_management/expensehead_delete.html'
    def get(self, request, expensehead_id, *args, **kwargs):
        expensehead = ExpenseHead.objects.get(expensehead_id=expensehead_id)
        context = {'expensehead':expensehead}
        return render(request, self.template_name, context)
    def post(self, request, expensehead_id, *args, **kwargs):
        expensehead = ExpenseHead.objects.get(expensehead_id=expensehead_id)
        expensehead.delete()
        return redirect('expensehead_list')




class ExpenseList(View):
    template_name = 'van_management/expense_list.html'

    def get(self, request, *args, **kwargs):
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        fil_expe = request.GET.get('expense_type')
        
        expenses = Expense.objects.all()  
        
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
            expenses = expenses.filter(expense_date__range=[from_date, to_date])
        else:
            expenses = expenses.filter(expense_date=datetime.today())
        
        if fil_expe:
            expenses = expenses.filter(expence_type_id=fil_expe)
        expense_types = ExpenseHead.objects.all()
        context = {'expenses': expenses, 'expense_types':expense_types}
        return render(request, self.template_name, context)

class ExpenseAdd(View):
    template_name = 'van_management/expense_add.html'
    form_class = ExpenseAddForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)

class ExpenseEdit(View):
    template_name = 'van_management/expense_edit.html'
    form_class = ExpenseEditForm

    def get(self, request, expense_id, *args, **kwargs):
        expense = Expense.objects.get(expense_id=expense_id)
        form = self.form_class(instance=expense)
        context = {'form': form, 'expense':expense}
        return render(request, self.template_name, context)

    def post(self, request, expense_id, *args, **kwargs):
        expense = get_object_or_404(Expense, expense_id=expense_id)
        form = self.form_class(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            print('updated')
            return redirect('expense_list')
        else:
            context = {'form': form, 'expense':expense}
            return render(request, self.template_name, context)

class ExpenseDelete(View):
    template_name = 'van_management/expense_delete.html'

    def get(self, request, expense_id, *args, **kwargs):
        expense = Expense.objects.get(expense_id=expense_id)
        context = {'expense': expense}
        return render(request, self.template_name, context)

    def post(self, request, expense_id, *args, **kwargs):
        expense = Expense.objects.get(expense_id=expense_id)
        expense.delete()
        return redirect('expense_list')
    
    
# ----------VanStock-----------
# class VanStock(View):
    
#     def get(self, request, *args, **kwargs):
#         instances = VanCouponStock.objects.all()
#         van_stock = VanProductStock.objects.all()

#         if request.user.is_authenticated and request.user.user_type == "Salesman":
#             instances = instances.filter(van__salesman_id=request.user.id)
#             van_stock = van_stock.filter(van__salesman_id=request.user.id)
            
#         # Aggregate the total count of each coupon type for each van
#         van_coupon_counts = instances.values('van__van_make', 'coupon__coupon_type__coupon_type_name').annotate(
#             coupon_count=Sum('count')
#         )
        
#         # Calculate opening stock based on total count of coupons
#         for van_coupon in van_coupon_counts:
#             van_coupon['opening_stock'] = van_coupon['coupon_count']
    
#         context = {'van_stock': van_stock, 'van_coupon_counts': van_coupon_counts}
#         return render(request, 'van_management/vanstock_list.html', context)
from datetime import time
class VanStockList(View):
    
    def get(self, request, *args, **kwargs):
        filter_data = {}
        
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        
        instances = VanCouponStock.objects.filter(created_date=date)
        van_stock = VanProductStock.objects.filter(created_date=date)
        requested_quantity=CustomerSupply.objects.all()
        issued_orders = Staff_IssueOrders.objects.filter(salesman_id=request.user.id)
        
        offload=Offload.objects.all()
        morning_stock_count=0
        evening_stock_count=0
        salesman_id=request.user.id
        
        if request.user.is_authenticated and request.user.user_type == "Salesman":
            instances = instances.filter(van__salesman_id=request.user.id)
            van_stock = van_stock.filter(van__salesman_id=request.user.id)
            for v in van_stock:
                pro=v.product.id
                morning_stocks = van_stock.filter(product=pro,van__created_date__time__lt=time(12, 0, 0))
                
                morning_stock_count = morning_stocks.filter(van__salesman_id=request.user.id,).count()
            #    o morning_stocks = VanStock.objects.filter(van__salesman_id=request.user.id,created_date__time__lt=time(12, 0, 0))
            #     mrning_stock_count = morning_stocks.filter(van__salesman_id=request.user.id,).count()
                print("morning_stock_count",morning_stock_count)
            evening_stocks = VanStock.objects.filter(van__salesman_id=request.user.id,created_date__time__gte=time(12, 0, 0))
            evening_stock_count = evening_stocks.filter(van__salesman_id=request.user.id).count()

            # requested_quantity=requested_quantity.filter(salesman__salesman_id=request.user.id)
        
        offload=offload.filter(van__salesman_id=salesman_id)
       
        van_coupon_counts = instances.values('van__van_make', 'coupon__coupon_type__coupon_type_name').annotate(
            coupon_count=Sum('count')
        )
        
        # Calculate opening stock based on total count of coupons
        for van_coupon in van_coupon_counts:
            van_coupon['opening_stock'] = van_coupon['coupon_count']
    
        context = {'van_stock': van_stock, 'van_coupon_counts': van_coupon_counts,
                   'issued_orders':issued_orders,'morning_stock_count': morning_stock_count,
            'evening_stock_count': evening_stock_count}
        return render(request, 'van_management/vanstock.html', context)
    
    
class VanProductStockList(View):
    
    def get(self, request, *args, **kwargs):
        filter_data = {}
        
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        
        # products = ProdutItemMaster.objects.filter()
        # van_instances = Van.objects.all()
        print(date)
        van_product_stock = VanProductStock.objects.filter(created_date=date)
    
        context = {
            # 'products': products,
            # 'van_instances': van_instances,
            'van_product_stock': van_product_stock,
            
            'filter_data': filter_data,
        }
        return render(request, 'van_management/van_product_stock.html', context)
    
    
    
def offload(request):
    instances = Van.objects.all()
    
    context = {
        'instances': instances
        }
    return render(request, 'van_management/offload.html', context)

class View_Item_Details(View):
    template_name = 'van_management/item_details.html'

    @method_decorator(login_required)
    def get(self, request, pk, *args, **kwargs):
        filter_data = {}
        
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
            
        product_items = VanProductStock.objects.filter(created_date=date,van__pk=pk)
        coupon_items = ProdutItemMaster.objects.filter(category__category_name__iexact="coupons")
        # VanCouponStock.objects.filter(created_date=date,van__pk=pk,stock__gt=0)
        
        context = {
            'product_items': product_items,
            'coupon_items': coupon_items,
            'van_pk': pk,
            'filter_data': filter_data,
            }
        
        return render(request, self.template_name, context)   
    
class EditProductView(View):
    def post(self, request, pk):
        count = request.POST.get('count')
        stock_type = request.POST.get('stock_type')
        item = VanProductStock.objects.get(pk=pk)
        print(stock_type)
        print(count)
        
        # try:
            # with transaction.atomic():
        if item.product.product_name == "5 Gallon" and stock_type == "stock":
            print("stock")
            item.stock -= int(count)
            item.save()
            
            product_stock = ProductStock.objects.get(branch=item.van.branch_id,product_name=item.product)
            product_stock.quantity += int(count)
            product_stock.save()
            
        elif item.product.product_name == "5 Gallon" and stock_type == "empty_can":
            print("empty")
            item.empty_can_count -= int(count)
            item.save()
            
            emptycan=EmptyCanStock.objects.create(
                product=item.product,
                quantity=int(count)
            )
            emptycan.save()
            
        elif item.product.product_name == "5 Gallon" and stock_type == "return_count":
            print("return")
            scrap_count = int(request.POST.get('scrap_count'))
            washing_count = int(request.POST.get('washing_count'))
            
            # print(scrap_count)
            # print(washing_count)
            
            OffloadReturnStocks.objects.create(
                created_by=request.user.id,
                created_date=datetime.today(),
                salesman=item.van.salesman,
                van=item.van,
                product=item.product,
                scrap_count=scrap_count,
                washing_count=washing_count
            )
            
            if scrap_count > 0 :
                if not ScrapProductStock.objects.filter(created_date__date=datetime.today().date(),product=item.product).exists():
                    scrap_instance=ScrapProductStock.objects.create(created_by=request.user.id,created_date=datetime.today(),product=item.product)
                else:
                    scrap_instance=ScrapProductStock.objects.get(created_date__date=datetime.today().date(),product=item.product)
                scrap_instance.quantity = scrap_count
                scrap_instance.save()
            
            if washing_count > 0 :
                if not WashingProductStock.objects.filter(created_date__date=datetime.today().date(),product=item.product).exists():
                    washing_instance=WashingProductStock.objects.create(created_by=request.user.id,created_date=datetime.today(),product=item.product)
                else:
                    washing_instance=WashingProductStock.objects.get(created_date__date=datetime.today().date(),product=item.product)
                washing_instance.quantity = washing_count
                washing_instance.save()
                
            count = scrap_count + washing_count
            # print(count)
            item.return_count -= int(count)
            item.save()
            
        else : 
            print("else")
            item.stock -= int(count)
            item.save()
            
            product_stock = ProductStock.objects.get(branch=item.van.branch_id,product_name=item.product)
            product_stock.quantity += int(count)
            product_stock.save()
        
        Offload.objects.create(
            created_by=request.user.id,
            created_date=datetime.today(),
            salesman=item.van.salesman,
            van=item.van,
            product=item.product,
            quantity=int(count),
            stock_type=stock_type
        )
        
        response_data = {
            "status": "true",
            "title": "Successfully Offloaded",
            "message": "Offload successfully.",
            'reload': 'true',
        }
                
        # except IntegrityError as e:
        #     # Handle database integrity error
        #     response_data = {
        #         "status": "false",
        #         "title": "Failed",
        #         "message": str(e),
        #     }

        # except Exception as e:
        #     # Handle other exceptions
        #     response_data = {
        #         "status": "false",
        #         "title": "Failed",
        #         "message": str(e),
        #     }
            
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
            
        
class EditCouponView(View):
    def post(self, request, van_pk):
        book_numbers = request.POST.getlist("coupon_book_no")
        
        for book_number in book_numbers:
            coupon_instance = NewCoupon.objects.get(book_num=book_number)
            
            van_coupon_stock = VanCouponStock.objects.get(van__pk=van_pk,coupon=coupon_instance)
            van_coupon_stock.stock -= 1
            van_coupon_stock.save()
            
            product_stock = ProductStock.objects.get(branch=van_coupon_stock.van.branch_id,product_name__product_name=coupon_instance.coupon_type.coupon_type_name)
            product_stock.quantity += 1
            product_stock.save()
            
            coupon = CouponStock.objects.get(couponbook=coupon_instance)
            coupon.coupon_stock = "company"
            coupon.save()
            
            OffloadCoupon.objects.create(
                created_by=request.user.id,
                created_date=datetime.now(),
                salesman=van_coupon_stock.van.salesman,
                van=van_coupon_stock.van,
                coupon=van_coupon_stock.coupon,
                quantity = 1,
                stock_type="stock"
            )
            
        response_data = {
                "status": "true",
                "title": "Successfully Created",
                "message": "Coupon Offload successfully.",
                'reload': 'true',
            }
        
        return JsonResponse(response_data)
    
def salesman_requests(request):
    
    instances = SalesmanRequest.objects.all()
    
    context = {
        'instances': instances
        }
    return render(request, 'van_management/salesman_requests.html', context)


def BottleAllocationn(request):
    filter_data = {}
    route_details = []
    
    van_routes = Van_Routes.objects.all()
    
    date = request.GET.get('date')
    
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        filter_data['filter_date'] = date.strftime('%Y-%m-%d')
    else:
        date = datetime.today().date()
        filter_data['filter_date'] = date.strftime('%Y-%m-%d')
    
    for route in van_routes:
        # Fetch the 5 Gallon product stock for the given date, or default to 0 if not found
        five_gallon_stock = VanProductStock.objects.filter(
            created_date=date, van=route.van, product__product_name="5 Gallon"
        ).aggregate(stock=Max('stock'))['stock'] or 0
        
        latest_update = CustomerSupply.objects.filter(customer__routes=route.routes).aggregate(latest_update=Max('modified_date'))['latest_update']
        
        route_details.append({
            'route_name': route.routes.route_name,
            'five_gallon_stock': five_gallon_stock,
            'latest_update': latest_update,
            'route_id': route.routes.route_id,
        })

    context = {
        'route_details': route_details,
        'filter_data': filter_data,
    }

    return render(request, 'van_management/bottle_allocation.html', context)



def EditBottleAllocation(request, route_id=None):
    if route_id:
        route = get_object_or_404(RouteMaster, route_id=route_id)
        print("route_id",route)
    else:
        route = None

    if request.method == 'POST':
        form = BottleAllocationForm(request.POST)
        if form.is_valid():
            bottle_allocation = form.save(commit=False)
            bottle_allocation.created_by = request.user.username
            bottle_allocation.save()
            return redirect('bottle_allocation')  # Replace with your list view name
    else:
        form = BottleAllocationForm(initial={'route': route})

    context = {
        'form': form,
    }

    return render(request, 'van_management/edit_bottle_allocation.html', context)


def VansRouteBottleCount(request):
    date = request.GET.get('date')
    print(date,'date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        date = datetime.today().date()
    van_details = []

    if date:
        van_product_stocks = VanProductStock.objects.filter(created_date=date)
        print("van_product_stocks",van_product_stocks)
        for stock in van_product_stocks:
            van = stock.van
            route_name = van.get_van_route() if van else 'No route'
            bottle_count = stock.stock
            van_details.append({
                'route': route_name,
                'bottle_count': bottle_count,
                'van_id': van.van_id
            })

    context = {
        'van_details': van_details,
        'date': date,
    }
    return render(request, 'van_management/van_route_bottle_count.html', context)

def VansRouteBottleCountAdd(request, van_id):
    van = get_object_or_404(Van, van_id=van_id)
    
    if request.method == 'POST':
        form = VansRouteBottleCountAddForm(request.POST)
        if form.is_valid():
            bottle_count = form.save(commit=False)
            bottle_count.van = van
            bottle_count.created_by = request.user.username
            bottle_count.save()

            # Update the bottle_count field in the Van model
            van.bottle_count += form.cleaned_data['qty_issued']
            van.save()

            return redirect('vans_route_bottle_count')  # Redirect to your bottle count report view
    else:
        form = VansRouteBottleCountAddForm()

    context = {
        'form': form,
        'van': van,
    }
    return render(request,'van_management/van_route_bottle_count_add.html', context)
def VansRouteBottleCountDeduct(request, van_id):
    van = get_object_or_404(Van, van_id=van_id)
    
    if request.method == 'POST':
        form = VansRouteBottleCountDeductForm(request.POST)
        if form.is_valid():
            bottle_count = form.save(commit=False)
            bottle_count.van = van
            bottle_count.created_by = request.user.username
            bottle_count.save()

            # Deduct the bottle_count field in the Van model
            van.bottle_count -= form.cleaned_data['qty_deducted']
            van.save()

            return redirect('vans_route_bottle_count')  # Redirect to your bottle count report view
    else:
        form = VansRouteBottleCountDeductForm()

    context = {
        'form': form,
        'van': van,
    }
    return render(request, 'van_management/van_route_bottle_count_deduct.html', context)


class VanCouponStockList(View):
    def get(self, request, *args, **kwargs):
        filter_data = {}
        
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        else:
            date = datetime.today().date()
            filter_data['filter_date'] = date.strftime('%Y-%m-%d')
        
        van_coupon_stock = VanCouponStock.objects.filter(created_date=date)
    
        context = {
            'van_coupon_stock': van_coupon_stock,
            'filter_data': filter_data,
        }
        return render(request, 'van_management/van_coupon_stock.html', context)