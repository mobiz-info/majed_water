import json
import random
import datetime
# django
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone
from django.forms import inlineformset_factory
from django.contrib.auth.models import User,Group
from django.forms.formsets import formset_factory
from django.db import transaction, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apiservices.views import delete_coupon_recharge
from client_management.models import CustomerCoupon, CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyItems
from client_management.views import handle_coupons, handle_invoice_deletion, handle_outstanding_amounts, update_van_product_stock
from customer_care.models import DiffBottlesModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view,renderer_classes, permission_classes
#local
from accounts.models import Customers
from master.functions import generate_form_errors
from master.models import CategoryMaster, RouteMaster
from invoice_management.models import Invoice, InvoiceItems
from product.models import Product, Product_Default_Price_Level
from invoice_management.forms import InvoiceForm, InvoiceItemsForm
from invoice_management.serializers import BuildingNameSerializers, ProductSerializers,CustomersSerializers

# Create your views here.
@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_building_no(request,route_id):
    customers = Customers.objects.filter(routes__pk=route_id)
    serialized = BuildingNameSerializers(customers, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_customer(request,route_id,building_no):
    customers = Customers.objects.filter(routes__pk=route_id,building_name=building_no)
    serialized = CustomersSerializers(customers, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_products(request,category_id):
    category = Product.objects.filter(category_id__pk=category_id)
    serialized = ProductSerializers(category, many=True, context={"request":request})

    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data,
    }
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_customer_rate(request,product,customer):
    product_price = 0
    vat_rate = 0
    total_include_vat = 0
    # print(product)
    # print(customer)
    try :
        product = Product.objects.get(pk=product)
        customer = Customers.objects.get(pk=customer)
        product_price = Product_Default_Price_Level.objects.get(product_id=product,customer_type=customer.customer_type).rate
        
        if product.product_name.tax:
            # print('vat')
            vat_rate = product.product_name.tax.percentage
            # print(vat_rate)
            total_include_vat = (float(vat_rate)/100) * float(product_price)
            # print(total_include_vat, "vat")
        
        
        response_data = {
            "StatusCode" : 6000,
            'product_price':product_price,
            'total_include_vat':total_include_vat,
        }
    except:
        response_data = {
            "StatusCode" : 6001,
            'product_price':product_price,
            'total_include_vat':total_include_vat,
        }
    return Response(response_data, status=status.HTTP_200_OK)

@login_required
def invoice_info(request,pk):
    """
    single view of invoice
    :param request:
    :return: invoice single view
    """
    instance = Invoice.objects.get(pk=pk,is_deleted=False)
    
    context = {
        'instance': instance,
        'page_name' : 'Invoice',
        'page_title' : 'Invoice',
        'is_invoice': True,
    }

    return render(request, 'invoice_management/info.html', context)

@login_required
def invoice_list(request):
    """
    Invoice List
    :param request:
    :return: Invoices list view
    """
    
    instances = Invoice.objects.filter(is_deleted=False).order_by("-created_date")
         
    date_range = ""
    date_range = request.GET.get('date_range')
    # print(date_range)

    if date_range:
        start_date_str, end_date_str = date_range.split(' - ')
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y').date()
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y').date()
        instances = instances.filter(date__range=[start_date, end_date])
    
    filter_data = {}
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(invoice_no__icontains=query) |
            Q(product__invoice_id__icontains=query) 
        )
        title = "Invoice List - %s" % query
        filter_data['q'] = query
    
    context = {
        'instances': instances,
        'page_name' : 'Invoice List',
        'page_title' : 'Invoice List',
        'filter_data' :filter_data,
        'date_range': date_range,
        
        'is_invoice': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'invoice_management/list.html', context)

@login_required
def invoice_customers(request):
    filter_data = {}
    
    instances = Customers.objects.all()
    
    if request.GET.get('route'):
        instances = instances.filter(routes__pk=request.GET.get('route'))
        
    if request.GET.get('building_no'):
        instances = instances.filter(door_house_no=request.GET.get('building_no'))
    
    query = request.GET.get("q")
    
    if query:

        instances = instances.filter(
            Q(customer_id__icontains=query) |
            Q(mobile_no__icontains=query) |
            Q(whats_app__icontains=query) |
            Q(customer_name__icontains=query) 
        )
        title = "Invoice Customers - %s" % query
        filter_data['q'] = query
        
    route_instances = RouteMaster.objects.all()

    context = {
        'instances': instances,
        'route_instances' : route_instances,
        
        'page_title': 'Create invoice',
        'invoice_page': True,
        'is_need_datetime_picker': True
    }
    
    return render(request,'invoice_management/customer_list.html',context)

def create_invoice(request, customer_pk):
    # customer_pk = request.GET.get("customer_pk")
    customer_instance = Customers.objects.get(pk=customer_pk)
    InvoiceItemsFormset = formset_factory(InvoiceItemsForm, extra=2)
    
    message = ''
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        invoice_items_formset = InvoiceItemsFormset(request.POST,prefix='invoice_items_formset', form_kwargs={'empty_permitted': False})
        
        if invoice_form.is_valid() and invoice_items_formset.is_valid():
            
            date_part = timezone.now().strftime('%Y%m%d')
            random_part = str(random.randint(1000, 9999))
            invoice_number = f'WTR-{date_part}-{random_part}'
            
            try:
                with transaction.atomic():
                    invoice = invoice_form.save(commit=False)
                    invoice.created_date = datetime.datetime.today()
                    invoice.invoice_no = invoice_number
                    invoice.customer = customer_instance
                    invoice.save()
                    
                    for form in invoice_items_formset:
                        data = form.save(commit=False)
                        data.invoice = invoice
                        data.save()
                    
                    
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Invoice created successfully.",
                        'redirect': 'true',
                        "redirect_url": reverse('invoice:invoice_list')
                    }
                    
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
        else:
            message = generate_form_errors(invoice_form,formset=False)
            message += generate_form_errors(invoice_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
    
    else:
        invoice_form = InvoiceForm()
        invoice_items_formset = InvoiceItemsFormset(prefix='invoice_items_formset')
        
        context = {
            'invoice_form': invoice_form,
            'invoice_items_formset': invoice_items_formset,
            'customer_instance': customer_instance,
            
            'page_title': 'Create invoice',
            'invoice_page': True,
            'is_need_datetime_picker': True
        }
        
        return render(request,'invoice_management/create.html',context)


@login_required
def edit_invoice(request,pk):
    """
    edit operation of invoice
    :param request:
    :param pk:
    :return:
    """
    invoice_instance = get_object_or_404(Invoice, pk=pk)
    invoice_items = InvoiceItems.objects.filter(invoice=invoice_instance)
    customer_instance = invoice_instance.customer
    
    if invoice_items.exists():
        extra = 0
    else:
        extra = 1 

    InvoiceItemsFormset = inlineformset_factory(
        Invoice,
        InvoiceItems,
        extra=extra,
        form=InvoiceItemsForm,
    )
        
    message = ''
    
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST,instance=invoice_instance)
        invoice_items_formset = InvoiceItemsFormset(request.POST,request.FILES,
                                            instance=invoice_instance,
                                            prefix='invoice_items_formset',
                                            form_kwargs={'empty_permitted': False})            
        
        if invoice_form.is_valid() and  invoice_items_formset.is_valid() :
            #create
            data = invoice_form.save(commit=False)
            data.save()
            
            for form in invoice_items_formset:
                if form not in invoice_items_formset.deleted_forms:
                    i_data = form.save(commit=False)
                    if not i_data.invoice :
                        i_data.invoice = invoice_instance
                    i_data.save()

            for f in invoice_items_formset.deleted_forms:
                f.instance.delete()
                
            response_data = {
                "status": "true",
                "title": "Successfully Updated",
                "message": "invoice Updated Successfully.",
                'redirect': 'true',
                "redirect_url": reverse('invoice:invoice_list'),
                "return" : True,
            }
    
        else:
            message = generate_form_errors(invoice_form,formset=False)
            message += generate_form_errors(invoice_items_formset,formset=True)
            
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": message
            }

        return HttpResponse(json.dumps(response_data), content_type='application/javascript')
                        
    else:
        # initial_values = []
        # for invoice_item in invoice_items:
        #     category_id = invoice_item.product.category_id
        #     initial_values.append({'category': category_id})

        invoice_form = InvoiceForm(instance=invoice_instance,initial={'customer_id': invoice_instance.customer.pk})
        invoice_items_formset = InvoiceItemsFormset(queryset=invoice_items,
                                                    prefix='invoice_items_formset',
                                                    instance=invoice_instance)
        # category_ids = [invoice_item.product.category_id for invoice_item in invoice_items]

        # # Create a list of initial data for each form in the formset
        # initial_data = [{'category': category_id} for category_id in category_ids]

        # # Create the formset instance with initial data
        # invoice_items_formset = InvoiceItemsFormset(
        #     queryset=invoice_items,
        #     prefix='invoice_items_formset',
        #     instance=invoice_instance,
        #     initial=initial_data
        # )
                
        route_instances = RouteMaster.objects.all()
        building_names_queryset = Customers.objects.filter(routes=invoice_form.instance.customer.routes).values_list('building_name', flat=True).distinct()
        # building_names = [name for name in building_names_queryset if isinstance(name, str) and name.strip()]
        

        context = {
            'invoice_form': invoice_form,
            'invoice_items_formset': invoice_items_formset,
            'route_instances': route_instances,
            'building_names': building_names_queryset,
            'customer_instance': customer_instance,
            
            'message': message,
            'page_name' : 'edit invoice',
            'url' : reverse('invoice:edit_invoice', args=[invoice_instance.pk]),
            'invoice_page': True,   
            'is_edit' : True,        
        }

        return render(request, 'invoice_management/create.html', context)
    
@login_required
def delete_invoice(request, pk):
    """
    invoice deletion, it only mark as is deleted field to true
    :param request:
    :param pk:
    :return:
    """
    try:
        with transaction.atomic():
            invoice = Invoice.objects.get(pk=pk)
            if CustomerSupply.objects.filter(invoice_no=invoice.invoice_no).exists():
                customer_supply_instance = get_object_or_404(CustomerSupply, invoice_no=invoice.invoice_no)
                supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=customer_supply_instance)
                five_gallon_qty = supply_items_instances.filter(product__product_name="5 Gallon").aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
                
                DiffBottlesModel.objects.filter(
                    delivery_date__date=customer_supply_instance.created_date.date(),
                    assign_this_to=customer_supply_instance.salesman,
                    customer=customer_supply_instance.customer_id
                    ).update(status='pending')
                
                # Handle invoice related deletions
                handle_invoice_deletion(customer_supply_instance)
                
                # Handle outstanding amount adjustments
                handle_outstanding_amounts(customer_supply_instance, five_gallon_qty)
                
                # Handle coupon deletions and adjustments
                handle_coupons(customer_supply_instance, five_gallon_qty)
                
                # Update van product stock and empty bottle counts
                update_van_product_stock(customer_supply_instance, supply_items_instances, five_gallon_qty)
                
                # Mark customer supply and items as deleted
                customer_supply_instance.delete()
                supply_items_instances.delete()
                
            if CustomerCoupon.objects.filter(invoice_no=invoice.invoice_no).exists():
                instance = CustomerCoupon.objects.get(invoice_no=invoice.invoice_no)
                delete_coupon_recharge(instance)
                
            if CustomerOutstanding.objects.filter(invoice_no=invoice.invoice_no).exists():
                # Retrieve outstanding linked to the invoice
                outstanding = CustomerOutstanding.objects.get(invoice_no=invoice.invoice_no)
                
                # Reverse the outstanding invoice creation
                outstanding.invoice_no = None
                outstanding.save()
                
                # Adjust CustomerOutstandingReport
                report = CustomerOutstandingReport.objects.get(customer=outstanding.customer, product_type='amount')
                report.value -= invoice.amout_total  # Adjust based on your invoice amount field
                report.save()
                
            invoice.is_deleted=True
            invoice.save()
            
            InvoiceItems.objects.filter(invoice=invoice).update(is_deleted=True)
            
            response_data = {
            "status": "true",
            "title": "Successfully Deleted",
            "message": "Invoice and associated data successfully deleted and reversed.",
            "redirect": "true",
            "redirect_url": reverse('invoice:invoice_list'),
        }
        
        return HttpResponse(json.dumps(response_data), content_type='application/javascript')

    except Invoice.DoesNotExist:
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "Invoice not found.",
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    except CustomerOutstanding.DoesNotExist:
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": "Customer outstanding record not found.",
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_404_NOT_FOUND, content_type='application/javascript')

    except Exception as e:
        response_data = {
            "status": "false",
            "title": "Failed",
            "message": str(e),
        }
        return HttpResponse(json.dumps(response_data), status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type='application/javascript')

@login_required
def invoice(request,pk):
    """
    Invoice Download
    :param request:
    :return: Invoices Download view
    """
    
    instance = Invoice.objects.get(pk=pk,is_deleted=False)  
           
    context = {
        'instance': instance,
        'page_name' : 'Invoice',
        'page_title' : 'Invoice',
        
        'is_invoice': True,
        'is_need_datetime_picker': True,
    }

    return render(request, 'invoice_management/invoice.html', context)

@login_required

def customerwise_invoice(request):
    
    invoices = Invoice.objects.filter( invoice_status="non_paid",is_deleted=False).exclude(amout_total__lt=1)
    query = request.GET.get("q")
    route_filter = request.GET.get('route_name')

    if query:
            invoices = invoices.filter(
                Q(customer__customer_name__icontains=query) |
                Q(customer__routes__route_name__icontains=query) 
            )

    if route_filter:
            invoices = invoices.filter(customer__routes__route_name=route_filter)

    route_li = RouteMaster.objects.all()
    invoices = invoices.values(
        'customer__customer_name',
        'customer__routes__route_name',
        'customer__customer_id'
    ).distinct()

    context = {
        'route_li':route_li,
        'invoices': invoices,
        
    }
    return render(request, 'invoice_management/customerwiseinvoice_list.html', context)
@login_required
def edit_customerwise_invoice(request,customer_id):
    print("customer_id",customer_id)
    invoices = Invoice.objects.filter(customer__customer_id=customer_id, invoice_status="non_paid",is_deleted=False).exclude(amout_total__lt=1)
    total_amount_total = 0
    total_amount_received = 0
    total_balance_amount = 0

    for invoice in invoices:
        invoice.balance_amount = invoice.amout_total - invoice.amout_recieved
        total_amount_total += invoice.amout_total
        total_amount_received += invoice.amout_recieved
        total_balance_amount += invoice.balance_amount

           
           
    context = {
        'invoices': invoices,
        'total_amount_total': total_amount_total,
        'total_amount_received': total_amount_received,
        'total_balance_amount': total_balance_amount,
    }
    return render(request, 'invoice_management/customerwiseinvoice.html', context)

from django.contrib import messages
def make_payment(request):
        if request.method == 'POST':
            customer_id = request.POST.get('customer_id')
            payment_amount = float(request.POST.get('payment_amount')) 
            
            customer = get_object_or_404(Customers, pk=customer_id)
            invoices = Invoice.objects.filter(
                customer=customer, 
                invoice_status="non_paid", 
                is_deleted=False
            ).exclude(amout_total__lt=1).order_by('created_date')

            with transaction.atomic():
                for invoice in invoices:
                    balance_amount = float(invoice.amout_total) - float(invoice.amout_recieved)  
                    if payment_amount > 0:
                        if payment_amount >= balance_amount:
                            invoice.amout_recieved = float(invoice.amout_recieved) + balance_amount 
                            invoice.invoice_status = "paid"
                            payment_amount -= balance_amount
                        else:
                            invoice.amout_recieved = float(invoice.amout_recieved) + payment_amount  
                            payment_amount = 0
                        invoice.save()
                    else:
                        break
            
            messages.success(request, 'Payment applied successfully!')
            return redirect('invoice:customerwise_invoice')

        return redirect('invoice:customerwise_invoice')
    