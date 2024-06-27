import datetime
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers
from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice, InvoiceItems
from product.models import ProdutItemMaster

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        oustandings = CustomerOutstanding.objects.all()
        
        for outstanding in oustandings:
            out_amounts = OutstandingAmount.objects.filter(customer_outstanding=outstanding)
            for out_amount in out_amounts:
            
                random_part = str(random.randint(1000, 9999))
                invoice_number = f'WTR-{random_part}'
                
                # Create the invoice
                invoice = Invoice.objects.create(
                    invoice_no=invoice_number,
                    created_date=out_amount.customer_outstanding.created_date,
                    net_taxable=out_amount.amount,
                    vat=0,
                    discount=0,
                    amout_total=out_amount.amount,
                    amout_recieved=0,
                    customer=out_amount.customer_outstanding.customer,
                    reference_no="oustading added from backend"
                )
                
                if out_amount.customer_outstanding.customer.sales_type == "CREDIT":
                    invoice.invoice_type = "credit_invoive"
                    invoice.save()

                # Create invoice items
                item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                InvoiceItems.objects.create(
                    category=item.category,
                    product_items=item,
                    qty=0,
                    rate=out_amount.customer_outstanding.customer.rate,
                    invoice=invoice,
                    remarks='invoice genereted from backend reference no : ' + invoice.reference_no
                )

        self.stdout.write(self.style.SUCCESS('Successfully updated visit schedule for customers with visit_schedule="Saturday"'))