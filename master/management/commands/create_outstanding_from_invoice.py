import datetime
import random

from django.db.models import Q
from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from client_management.models import CustomerCoupon, CustomerOutstanding, CustomerOutstandingReport, CustomerSupply, CustomerSupplyItems, DialyCustomers, InactiveCustomers, OutstandingAmount
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from sales_management.models import Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        user = CustomUser.objects.get(username="zeeshan")
        date = datetime.datetime.strptime("2024-09-15", '%Y-%m-%d').date()
        invoices  = Invoice.objects.filter(customer__routes__route_name="v3",created_date__date=date,is_deleted=False)
        
        for invoice in invoices:
            if not CustomerSupply.objects.filter(invoice_no=invoice.invoice_no).exists() or not CustomerCoupon.objects.filter(invoice_no=invoice.invoice_no).exists():
                if not CustomerOutstanding.objects.filter(created_date__date=date,invoice_no=invoice.invoice_no).exists():
                    customer_outstanding = CustomerOutstanding.objects.create(
                        customer=invoice.customer,
                        product_type='amount',
                        created_by=user.id,
                        modified_by=user.id,
                        created_date=date,
                        invoice_no=invoice.invoice_no,
                    )

                    # Create OutstandingAmount
                    outstanding_amount = OutstandingAmount.objects.create(
                        customer_outstanding=customer_outstanding,
                        amount=invoice.amout_total
                    )

                    # Update or create CustomerOutstandingReport
                    if (instances:=CustomerOutstandingReport.objects.filter(customer=invoice.customer,product_type='amount')).exists():
                        report = instances.first()
                    else:
                        report = CustomerOutstandingReport.objects.create(customer=invoice.customer,product_type='amount')

                    report.value += invoice.amout_total
                    report.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {invoice.invoice_no}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all invoices are updated'))
