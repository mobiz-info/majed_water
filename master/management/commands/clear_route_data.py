from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from client_management.models import CustodyCustom, CustomerOutstanding, CustomerOutstandingReport, Vacation
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
        
        outstanding_in = CustomerOutstanding.objects.filter(customer__routes__route_name="v1")
        for i in outstanding_in:
            Invoice.objects.filter(invoice_no=i.invoice_no).delete()
        outstanding_in.delete()
        CustomerOutstandingReport.objects.filter(customer__routes__route_name="v1").delete()
        
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
        CollectionPayment.objects.filter(customer__routes__route_name="v1").delete()
        # SalesmanSpendingLog.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerProductReturn.objects.filter(customer_routes_route_name="v1").delete()
        # CustomerProductReplace.objects.filter(customer_routes_route_name="v1").delete()

