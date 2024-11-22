import datetime
from datetime import timedelta
from django.utils import timezone

from django import template
from django.db.models import Q, Sum, F, Case, When, IntegerField

from accounts.models import Customers
from client_management.models import *
from sales_management.models import *

register = template.Library()

@register.simple_tag
def route_wise_bottle_count(route_pk):
    customers = Customers.objects.filter(routes__pk=route_pk)
    
    final_bottle_count = 0 
    
    for customer in customers:
        total_bottle_count = CustomerSupply.objects.filter(customer=customer.customer_id)\
                                                     .aggregate(total_quantity=Sum('allocate_bottle_to_custody'))['total_quantity'] or 0
        
        last_supplied_count = 0
        
        if (supply_items:=CustomerSupplyItems.objects.filter(customer_supply__customer=customer.customer_id)).exists():
            last_supplied_count = supply_items.values_list('quantity', flat=True).latest("customer_supply__created_date") or 0

        pending_count = CustomerSupply.objects.filter(customer=customer.customer_id)\
                                                .aggregate(total_quantity=Sum('allocate_bottle_to_pending'))['total_quantity'] or 0

        customer_bottle_count = total_bottle_count + last_supplied_count + pending_count
        final_bottle_count += customer_bottle_count
    
    return final_bottle_count


@register.simple_tag
def route_wise_customer_bottle_count(customer_pk):
    customer = Customers.objects.get(pk=customer_pk)
    custody_count = 0
    outstanding_bottle_count = 0
    
    if (custody_stock:=CustomerCustodyStock.objects.filter(customer=customer,product__product_name="5 Gallon")).exists() :
        custody_count = custody_stock.first().quantity 
    
    if (outstanding_count:=CustomerOutstandingReport.objects.filter(customer=customer,product_type="emptycan")).exists() :
        outstanding_bottle_count = outstanding_count.first().value
    
    last_supplied_count = CustomerSupplyItems.objects.filter(customer_supply__customer=customer).order_by('-customer_supply__created_date').values_list('quantity', flat=True).first() or 0

    total_bottle_count = custody_count + outstanding_bottle_count + last_supplied_count
    
    return {
        'custody_count': custody_count,
        'outstanding_bottle_count': outstanding_bottle_count,
        'last_supplied_count': last_supplied_count,
        'total_bottle_count': total_bottle_count
    }
        
        
@register.simple_tag
def get_outstanding_amount(customer_id,date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_amounts = OutstandingAmount.objects.filter(customer_outstanding__customer__pk=customer_id,customer_outstanding__created_date__date__lte=date).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    collection_amount = CollectionPayment.objects.filter(customer__pk=customer_id,created_date__date__lte=date).aggregate(total_amount_received=Sum('amount_received'))['total_amount_received'] or 0
    
    return outstanding_amounts - collection_amount
    # if outstanding_amounts > collection_amount:
    # else:
    #     return collection_amount - outstanding_amounts

@register.simple_tag
def get_outstanding_bottles(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_bottles = OutstandingProduct.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date
    ).aggregate(total_bottles=Sum('empty_bottle'))['total_bottles'] or 0
    return outstanding_bottles

@register.simple_tag
def get_outstanding_coupons(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_coupons = OutstandingCoupon.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date,
    ).aggregate(total_coupons=Sum('count'))
    
    return outstanding_coupons.get('total_coupons') or 0






# @register.simple_tag
# def get_customer_outstanding_aging(route=None):
#     if not route:
#         return []

#     aging_report = []
#     current_date = timezone.now().date()
#     outstanding_data = (
#         OutstandingAmount.objects
#         .filter(customer_outstanding__customer__routes__route_name=route)
#         .values('customer_outstanding__customer__customer_id', 'customer_outstanding__customer__customer_name')
#         .annotate(
#             total_amount=Sum('amount'),
#             less_than_30=Sum(
#                 Case(
#                     When(customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=30), then=F('amount')),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             ),
#             between_31_and_60=Sum(
#                 Case(
#                     When(
#                         customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=60),
#                         customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=30),
#                         then=F('amount')
#                     ),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             ),
#             between_61_and_90=Sum(
#                 Case(
#                     When(
#                         customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=90),
#                         customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=60),
#                         then=F('amount')
#                     ),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             ),
#             between_91_and_150=Sum(
#                 Case(
#                     When(
#                         customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=150),
#                         customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=90),
#                         then=F('amount')
#                     ),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             ),
#             between_151_and_365=Sum(
#                 Case(
#                     When(
#                         customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=365),
#                         customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=150),
#                         then=F('amount')
#                     ),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             ),
#             more_than_365=Sum(
#                 Case(
#                     When(customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=365), then=F('amount')),
#                     default=0,
#                     output_field=DecimalField(),
#                 )
#             )
#         )
#     )

#     # Build the aging report
#     for data in outstanding_data:
#         aging_data = {
#             'customer_id': data['customer_outstanding__customer__customer_id'],
#             'customer_name': data['customer_outstanding__customer__customer_name'],
#             'less_than_30': data['less_than_30'],
#             'between_31_and_60': data['between_31_and_60'],
#             'between_61_and_90': data['between_61_and_90'],
#             'between_91_and_150': data['between_91_and_150'],
#             'between_151_and_365': data['between_151_and_365'],
#             'more_than_365': data['more_than_365'],
#             'grand_total': data['total_amount'],
#         }

#         # Only add to report if there's a total outstanding amount
#         if aging_data['grand_total'] > 0:
#             aging_report.append(aging_data)

#     return aging_report


@register.simple_tag
def get_customer_outstanding_aging(route=None):
    if not route:
        return []

    aging_report = []
    current_date = timezone.now().date()

    # Step 1: Get outstanding amounts for customers in the given route
    outstanding_data = OutstandingAmount.objects.filter(
        customer_outstanding__customer__routes__route_name=route
    ).values(
        'customer_outstanding__customer__customer_id',
        'customer_outstanding__customer__customer_name',
        'customer_outstanding__customer__custom_id'
    ).annotate(
        total_outstanding=Sum('amount'),
        less_than_30=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=30),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_31_and_60=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=60),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=30),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_61_and_90=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=90),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=60),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_91_and_150=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=150),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=90),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        between_151_and_365=Sum(
            Case(
                When(
                    customer_outstanding__created_date__gte=current_date - timezone.timedelta(days=365),
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=150),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        ),
        more_than_365=Sum(
            Case(
                When(
                    customer_outstanding__created_date__lt=current_date - timezone.timedelta(days=365),
                    then='amount'
                ),
                default=0,
                output_field=DecimalField(),
            )
        )
    )

    # Step 2: For each customer, calculate collections for each aging bucket and adjust outstanding
    for data in outstanding_data:
        customer_id = data['customer_outstanding__customer__customer_id']
        custom_id = data['customer_outstanding__customer__custom_id']
        
        # Calculate collections for each bucket
        collections = CollectionPayment.objects.filter(
            customer__customer_id=customer_id,
            created_date__date__lte=current_date
        ).aggregate(
            collected_less_than_30=Sum(
                Case(
                    When(
                        created_date__gte=current_date - timezone.timedelta(days=30),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            collected_between_31_and_60=Sum(
                Case(
                    When(
                        created_date__gte=current_date - timezone.timedelta(days=60),
                        created_date__lt=current_date - timezone.timedelta(days=30),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            collected_between_61_and_90=Sum(
                Case(
                    When(
                        created_date__gte=current_date - timezone.timedelta(days=90),
                        created_date__lt=current_date - timezone.timedelta(days=60),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            collected_between_91_and_150=Sum(
                Case(
                    When(
                        created_date__gte=current_date - timezone.timedelta(days=150),
                        created_date__lt=current_date - timezone.timedelta(days=90),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            collected_between_151_and_365=Sum(
                Case(
                    When(
                        created_date__gte=current_date - timezone.timedelta(days=365),
                        created_date__lt=current_date - timezone.timedelta(days=150),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            collected_more_than_365=Sum(
                Case(
                    When(
                        created_date__lt=current_date - timezone.timedelta(days=365),
                        then='amount_received'
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            )
        )

        # Subtract collections from respective outstanding buckets
        less_than_30 = data['less_than_30'] - (collections['collected_less_than_30'] or 0)
        between_31_and_60 = data['between_31_and_60'] - (collections['collected_between_31_and_60'] or 0)
        between_61_and_90 = data['between_61_and_90'] - (collections['collected_between_61_and_90'] or 0)
        between_91_and_150 = data['between_91_and_150'] - (collections['collected_between_91_and_150'] or 0)
        between_151_and_365 = data['between_151_and_365'] - (collections['collected_between_151_and_365'] or 0)
        more_than_365 = data['more_than_365'] - (collections['collected_more_than_365'] or 0)

        # Ensure no negative values
        less_than_30 = max(less_than_30, 0)
        between_31_and_60 = max(between_31_and_60, 0)
        between_61_and_90 = max(between_61_and_90, 0)
        between_91_and_150 = max(between_91_and_150, 0)
        between_151_and_365 = max(between_151_and_365, 0)
        more_than_365 = max(more_than_365, 0)

        # Calculate grand total
        grand_total = less_than_30 + between_31_and_60 + between_61_and_90 + between_91_and_150 + between_151_and_365 + more_than_365

        if grand_total > 0:
            aging_report.append({
                'custom_id': custom_id,
                'customer_id': customer_id,
                'customer_name': data['customer_outstanding__customer__customer_name'],
                'less_than_30': less_than_30,
                'between_31_and_60': between_31_and_60,
                'between_61_and_90': between_61_and_90,
                'between_91_and_150': between_91_and_150,
                'between_151_and_365': between_151_and_365,
                'more_than_365': more_than_365,
                'grand_total': grand_total,
            })

    return aging_report
