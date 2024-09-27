from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from client_management.models import CustodyCustom, Vacation
from customer_care.models import CouponPurchaseModel, CustodyPullOutModel, CustomerComplaint, DiffBottlesModel, OtherRequirementModel
from order.models import ChangeOrReturn, Customer_Order
from sales_management.models import CollectionPayment, CustomerCoupons, OutstandingLog, SaleEntryLog, SalesmanSpendingLog, Transaction, Transactionn
from van_management.models import CustomerProductReplace, CustomerProductReturn

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        customers = Customers.objects.filter(routes__route_name="v8")
        for customer in customers:
            if customer.user_id:
                CustomUser.objects.filter(pk=customer.user_id.pk).delete()
        customers.delete()
        
        CustodyCustom.objects.filter(customer__routes__route_name="v8").delete()
        Vacation.objects.filter(customer__routes__route_name="v8").delete()
        DiffBottlesModel.objects.filter(customer__routes__route_name="v8").delete()
        OtherRequirementModel.objects.filter(customer__routes__route_name="v8").delete()
        CouponPurchaseModel.objects.filter(customer__routes__route_name="v8").delete()
        CustodyPullOutModel.objects.filter(customer__routes__route_name="v8").delete()
        CustomerComplaint.objects.filter(customer__routes__route_name="v8").delete()
        Customer_Order.objects.filter(customer_id__routes__route_name="v8").delete()
        ChangeOrReturn.objects.filter(customer__routes__route_name="v8").delete()
        SaleEntryLog.objects.filter(customer__routes__route_name="v8").delete()
        OutstandingLog.objects.filter(customer__routes__route_name="v8").delete()
        Transaction.objects.filter(customer__routes__route_name="v8").delete()
        CustomerCoupons.objects.filter(customer__routes__route_name="v8").delete()
        Transactionn.objects.filter(customer__routes__route_name="v8").delete()
        CollectionPayment.objects.filter(customer__routes__route_name="v8").delete()
        SalesmanSpendingLog.objects.filter(customer__routes__route_name="v8").delete()
        CustomerProductReturn.objects.filter(customer__routes__route_name="v8").delete()
        CustomerProductReplace.objects.filter(customer__routes__route_name="v8").delete()
        
        
