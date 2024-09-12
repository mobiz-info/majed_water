# from django.core.management.base import BaseCommand
# from accounts.models import CustomUser, Customers
# from client_management.models import CustodyCustom, Vacation
# from customer_care.models import CouponPurchaseModel, CustodyPullOutModel, CustomerComplaint, DiffBottlesModel, OtherRequirementModel
# from order.models import ChangeOrReturn, Customer_Order
# from sales_management.models import CollectionPayment, CustomerCoupons, OutstandingLog, SaleEntryLog, SalesmanSpendingLog, Transaction, Transactionn
# from van_management.models import CustomerProductReplace, CustomerProductReturn

# class Command(BaseCommand):
#     help = 'Generate usernames and passwords for customers based on their name and mobile number'

#     def handle(self, *args, **kwargs):
#         CustodyCustom.objects.filter(customer__isnull=True).delete()
#         Vacation.objects.filter(customer__isnull=True).delete()
#         DiffBottlesModel.objects.filter(customer__isnull=True).delete()
#         OtherRequirementModel.objects.filter(customer__isnull=True).delete()
#         CouponPurchaseModel.objects.filter(customer__isnull=True).delete()
#         CustodyPullOutModel.objects.filter(customer__isnull=True).delete()
#         CustomerComplaint.objects.filter(customer__isnull=True).delete()
#         Customer_Order.objects.filter(customer_id__isnull=True).delete()
#         SaleEntryLog.objects.filter(customer__isnull=True).delete()
#         OutstandingLog.objects.filter(customer__isnull=True).delete()
#         Transaction.objects.filter(customer__isnull=True).delete()
#         CustomerCoupons.objects.filter(customer__isnull=True).delete()
#         Transactionn.objects.filter(customer__isnull=True).delete()
#         CollectionPayment.objects.filter(customer__isnull=True).delete()
#         SalesmanSpendingLog.objects.filter(customer__isnull=True).delete()
#         CustomerProductReturn.objects.filter(customer__isnull=True).delete()
#         CustomerProductReplace.objects.filter(customer__isnull=True).delete()
        
        
