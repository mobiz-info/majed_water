import requests
import datetime
from decimal import Decimal
from datetime import datetime


from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.db.models import Q, Sum, Min, Max
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.views.decorators.cache import cache_page

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes

from itertools import chain

from master.models import BranchMaster, DesignationMaster, EmirateMaster, LocationMaster, RouteMaster
from accounts.models import CustomUser, Customers
from client_management.models import *
from van_management.models import *

from api_erp.v1.transaction.serializers import *
from api_erp.v1.transaction.functions import get_sales_data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def sales_invoices_list(request):
    start_date = request.GET.get('start_date', datetime.today().date())
    end_date = request.GET.get('end_date', datetime.today().date())
    sales_type = request.GET.get('invoice_types')  
    route_name = request.GET.get('route_id')
    customer_id = request.GET.get('customer_id')

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    try:
        route = Van_Routes.objects.get(van__salesman=request.user).routes
        is_salesman = True
    except Van_Routes.DoesNotExist:
        route = None
        is_salesman = False
    
    sales_filter = {
        "created_date__date__gte": start_date,
        "created_date__date__lte": end_date,
    }

    if is_salesman:
        sales_filter["customer__routes"] = route
    elif route_name:
        sales_filter["customer__routes"] = route_name
    else:
        all_routes = Van_Routes.objects.values_list("routes", flat=True)
        sales_filter["customer__routes__in"] = all_routes

    if customer_id:
        sales_filter["customer__customer_id"] = customer_id

    if sales_type == "cash_invoice":
        sales = CustomerSupply.objects.filter(
            Q(amount_recieved__gt=0) | Q(customer__sales_type="FOC"),
            **sales_filter
        )
    elif sales_type == "credit_invoice":
        sales = CustomerSupply.objects.filter(
            amount_recieved__lte=0,
            **sales_filter
        ).exclude(customer__sales_type="FOC")
    else:
        sales = CustomerSupply.objects.filter(**sales_filter)

    total_sales = sales.aggregate(
        total_grand_total=Sum('grand_total'),
        total_vat=Sum('vat'),
        total_net_payable=Sum('net_payable'),
        total_amount_received=Sum('amount_recieved')
    )

    response_data = {
        "StatusCode": 200,
        "status": "success",
        "data": {
            "invoices": SalesReportSerializer(sales, many=True).data,
            "total_amount": round(total_sales.get("total_grand_total") or 0, 2),
            "total_vat": round(total_sales.get("total_vat") or 0, 2),
            "total_taxable": round(total_sales.get("total_net_payable") or 0, 2),
            "total_amount_collected": round(total_sales.get("total_amount_received") or 0, 2),
            "filters": {
                "route_name": str(route) if route else "All Routes",
                "invoice_types": sales_type if sales_type else "All", 
                "start_date": str(start_date),
                "end_date": str(end_date),
                "customer_id": customer_id if customer_id else "All"
            }
        },
    }
    return Response(response_data, status=200)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# @renderer_classes([JSONRenderer])
# def customer_transaction(request):
#     customer_pk = request.GET.get("customer_id")  
#     transaction_type = request.GET.get('transaction_type')
    
#     if request.GET.get('start_date'):
#         start_date = request.GET.get('start_date')
#     else:
#         start_date = datetime.today().date()
        
#     if request.GET.get('end_date'):
#         end_date = request.GET.get('end_date')
#     else:
#         end_date = datetime.today().date()
        
#     # Fetch data
#     supply_qs = CustomerSupply.objects.filter(created_date__date__gte=start_date, created_date__date__lte=end_date)
#     coupon_qs = CustomerCoupon.objects.filter(created_date__date__gte=start_date, created_date__date__lte=end_date)
#     collection_qs = CollectionPayment.objects.filter(created_date__date__gte=start_date, created_date__date__lte=end_date)

#     # Serialize
#     supply_data = TransactionCusomerSupplySerializer(supply_qs, many=True, context={'request': request}).data
#     for item in supply_data:
#         item["type"] = "supply"

#     coupon_data = TransactionCusomerCouponSerializer(coupon_qs, many=True, context={'request': request}).data
#     for item in coupon_data:
#         item["type"] = "coupon_recharge"

#     collection_data = TransactionCollectionPaymentSerializer(collection_qs, many=True, context={'request': request}).data
#     for item in collection_data:
#         item["type"] = "collection"

#     # Combine and sort all transactions by date (descending)
#     combined_data = list(chain(supply_data, coupon_data, collection_data))
#     combined_data.sort(key=lambda x: x.get("transaction_date") or datetime.min, reverse=True)

#     # Apply Pagination
#     class StandardPagination(PageNumberPagination):
#         page_size = 10
#         page_size_query_param = 'page_size'
#         max_page_size = 100

#     paginator = StandardPagination()
#     paginated_result = paginator.paginate_queryset(combined_data, request)

#     return paginator.get_paginated_response({
#         "StatusCode": 6000,
#         "status": status.HTTP_200_OK,
#         "transactions": paginated_result
#     })

@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
@cache_page(60 * 5)  # Cache the response for 5 minutes
def customer_transaction(request):
    customer_pk = request.GET.get("customer_id")  
    transaction_type = request.GET.get('transaction_type')

    start_date = request.GET.get('start_date') or str(datetime.today().date())
    end_date = request.GET.get('end_date') or str(datetime.today().date())

    # Prepare queryset filters
    filters = {
        'created_date__date__range': (start_date, end_date)
    }

    if customer_pk:
        filters['customer_id'] = customer_pk

    supply_qs = coupon_qs = collection_qs = []

    if transaction_type == "supply":
        supply_qs = CustomerSupply.objects.filter(**filters)
    elif transaction_type == "coupon_recharge":
        coupon_qs = CustomerCoupon.objects.filter(**filters)
    elif transaction_type == "collection":
        collection_qs = CollectionPayment.objects.filter(**filters)
    else:
        # If no specific type given, fetch all
        supply_qs = CustomerSupply.objects.filter(**filters)
        coupon_qs = CustomerCoupon.objects.filter(**filters)
        collection_qs = CollectionPayment.objects.filter(**filters)
    # Combine all objects
    combined_qs = list(chain(supply_qs, coupon_qs, collection_qs))

    # Sort by created_date descending
    combined_qs.sort(key=lambda x: x.created_date or datetime.min, reverse=True)

    # Pagination setup
    class StandardPagination(PageNumberPagination):
        page_size = 50
        page_size_query_param = 'page_size'
        max_page_size = 100

    paginator = StandardPagination()
    paginated_qs = paginator.paginate_queryset(combined_qs, request)

    # Serialize paginated items
    paginated_serialized = []
    for obj in paginated_qs:
        if isinstance(obj, CustomerSupply):
            data = TransactionCusomerSupplySerializer(obj, context={'request': request}).data
        elif isinstance(obj, CustomerCoupon):
            data = TransactionCusomerCouponSerializer(obj, context={'request': request}).data
        elif isinstance(obj, CollectionPayment):
            data = TransactionCollectionPaymentSerializer(obj, context={'request': request}).data
        else:
            continue  # skip unknown types

        paginated_serialized.append(data)

    # Final response
    return paginator.get_paginated_response({
        "StatusCode": 6000,
        "status": status.HTTP_200_OK,
        "transactions": paginated_serialized
    })



@api_view(['POST'])
@permission_classes([AllowAny])
def saletransaction(request):
    customer_pk = request.data.get("customer_id")
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    try:
        transactions = get_sales_data(customer_pk, start_date, end_date)
        response_data = {
            "StatusCode": 6000,
            "status": 200,
            "transactions": transactions,
        }
        return Response(response_data, status=200)
    except ValueError as e:
        return Response({"StatusCode": 4001, "message": str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def process_sales_transaction(request):
    try:
        data = request.data
        
        trx_time = data['trX_TIME']
        trx_type = data['trX_TYPE']
        branch_name = data['brancH_NAME']
        city = data['city']
        location_name = data['locatioN_NAME']
        vehicle_number = data['vehiclE_NUMBER']
        route_name = data['routE_NAME']
        customer_unique_number = data['customeR_UNIQ_NUMBER']
        before_tax_amount = Decimal(data['beF_TAX_AMOUNT'])
        tax_amount = Decimal(data['taX_AMOUNT'])
        with_tax_amount = Decimal(data['witH_TAX_AMOUNT'])
        received_amount = Decimal(data['receiveD_AMOUNT'])
        payment_type = data['paymenT_TYPE']
        bank_name = data['banK_NAME']
        receipt_number = data['receipT_NUMBER']
        receipt_date = data['receipT_DATE']
        delivery_type = data['deliverY_TYPE']
        description = data['hdR_DESC']
        employee_id = data['erP_SYS_EMP_ID']
        transaction_id = data['otheR_SYS_HDR_ID']
        
        customer = Customers.objects.get(custom_id=customer_unique_number)

        customer_supply = CustomerSupply.objects.create(
            customer=customer,
            subtotal=before_tax_amount,
            vat=tax_amount,
            grand_total=with_tax_amount,
            amount_recieved=received_amount,
            invoice_no=receipt_number
        )

        for item in data['salesTransactionLines']:
            product = Product.objects.get(id=item['erP_SYS_ITEM_ID'])
            quantity = item['qty']
            unit_price = item['uniT_PRICE']
            item_subtotal = item['beF_TAX_AMOUNT']
            item_tax = item['taX_AMOUNT']
            item_grand_total = item['witH_TAX_AMOUNT']
            
            CustomerSupplyItems.objects.create(
                customer_supply=customer_supply,
                product=product,
                quantity=quantity,
                subtotal=item_subtotal,
                vat=item_tax,
                grand_total=item_grand_total
            )

        for payment in data['paymentApplications']:
            CollectionPayment.objects.create(
                customer=customer,
                amount_received=payment['applieD_AMOUNT']
            )

        return Response({
            "success": True,
            "message": "Successfully Processed."
        })

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=400)
        
        
        
@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def expense_summary(request):
    branch_id = request.GET.get('branch_id')
    trx_date = request.GET.get('trx_date')

    instances = Expense.objects.select_related("route__branch_id", "van__salesman", "expence_type")

    if branch_id:
        instances = instances.filter(route__branch_id=branch_id)
    
    if trx_date:
        instances = instances.filter(expense_date=trx_date)

    serializer = ExpenseSummarySerializer(instances, many=True)
    
    status_code = status.HTTP_200_OK
    response_data = {
        "StatusCode": 6000,
        "status": status_code,
        "data": serializer.data
    }

    return Response(response_data, status=status_code)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def sales_summary(request):
    branch_name = request.GET.get('branch_name')
    staff_id = request.GET.get('staff_id')
    trx_date = request.GET.get('trx_date')
    
    filters = {}
    if branch_name:
        filters['salesman__branch_id__name'] = branch_name 
    if staff_id:
        filters['salesman__id'] = staff_id
    if trx_date:
        filters['created_date__date'] = datetime.strptime(trx_date, '%Y-%m-%d').date()
    
    instances = CustomerSupply.objects.filter(**filters)
    serializer = SalesSummarySerializer(instances, many=True)
    
    return Response({"StatusCode": 6000, "status": status.HTTP_200_OK, "data": serializer.data}, status=status.HTTP_200_OK)


