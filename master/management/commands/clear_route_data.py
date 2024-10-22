import datetime
from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from django.db.models import Q, Sum
from client_management.models import CustodyCustom, CustomerOutstanding, CustomerOutstandingReport, OutstandingAmount, OutstandingCoupon, OutstandingProduct, Vacation
from customer_care.models import CouponPurchaseModel, CustodyPullOutModel, CustomerComplaint, DiffBottlesModel, OtherRequirementModel
from invoice_management.models import Invoice
from order.models import ChangeOrReturn, Customer_Order
from sales_management.models import CollectionPayment, CustomerCoupons, OutstandingLog, SaleEntryLog, SalesmanSpendingLog, Transaction, Transactionn
from van_management.models import CustomerProductReplace, CustomerProductReturn

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        # customers = Customers.objects.filter(routes__route_name="v8")
        # for customer in customers:
        #     if customer.user_id:
        #         CustomUser.objects.filter(pk=customer.user_id.pk).delete()
        # customers.delete()
        date = datetime.datetime.strptime('2024-09-04', '%Y-%m-%d').date()
        outstanding_in = CustomerOutstanding.objects.filter(customer__routes__route_name="v16",created_date__date__lt=date)
        outstanding_in.delete()
        Invoice.objects.filter(customer__routes__route_name="v16",created_date__date__lt=date).delete()
        # CustomerOutstandingReport.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        
        # CustodyCustom.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # Vacation.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # DiffBottlesModel.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # OtherRequirementModel.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CouponPurchaseModel.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CustodyPullOutModel.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CustomerComplaint.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # Customer_Order.objects.filter(customer_id__routes__route_name="v1").delete()
        # ChangeOrReturn.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # SaleEntryLog.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # OutstandingLog.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # Transaction.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CustomerCoupons.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # Transactionn.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CollectionPayment.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # SalesmanSpendingLog.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CustomerProductReturn.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # CustomerProductReplace.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        
        # Invoice.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        
        # CustodyCustom.objects.filter(customer_routes_route_name="v1").delete()
        # Vacation.objects.filter(customer_routes_route_name="v1").delete()
        # DiffBottlesModel.objects.filter(customer_routes_route_name="v1").delete()
        # OtherRequirementModel.objects.filter(customer_routes_route_name="v1").delete()
        # CouponPurchaseModel.objects.filter(customer_routes_route_name="v1").delete()
        # CustodyPullOutModel.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerComplaint.objects.filter(customer_routes_route_name="v1").delete()
        # Customer_Order.objects.filter(customer_id_routes_route_name="v1").delete()
        # ChangeOrReturn.objects.filter(customer_routes_route_name="v1").delete()
        # SaleEntryLog.objects.filter(customer_routes_route_name="v1").delete()
        # OutstandingLog.objects.filter(customer_routes_route_name="v1").delete()
        # Transaction.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerCoupons.objects.filter(customer_routes_route_name="v1").delete()
        # Transactionn.objects.filter(customer_routes_route_name="v1").delete()
        # CollectionPayment.objects.filter(customer__routes__route_name="v1",created_date__date__lt=date).delete()
        # SalesmanSpendingLog.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerProductReturn.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerProductReplace.objects.filter(customer_routes_route_name="v1").delete()
        
        
        # customers = Customers.objects.filter(routes__route_name="v1")
        # for customer in customers:
        #     outstanding_amount = OutstandingAmount.objects.filter(customer_outstanding__customer=customer).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        #     collections = CollectionPayment.objects.filter(customer=customer).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
        #     CustomerOutstandingReport.objects.filter(customer=customer,product_type="amount").update(value=outstanding_amount - collections)
            
        #     outstanding_bottles = OutstandingProduct.objects.filter(customer_outstanding__customer=customer).aggregate(total_empty_bottle=Sum('empty_bottle'))['total_empty_bottle'] or 0
        #     CustomerOutstandingReport.objects.filter(customer=customer,product_type="emptycan").update(value=outstanding_bottles)
            
        #     outstanding_coupon = OutstandingCoupon.objects.filter(customer_outstanding__customer=customer).aggregate(total_count=Sum('count'))['total_count'] or 0
        #     CustomerOutstandingReport.objects.filter(customer=customer,product_type="coupons").update(value=outstanding_coupon)
