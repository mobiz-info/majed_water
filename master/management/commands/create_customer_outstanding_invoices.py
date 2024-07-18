import datetime
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser, Customers
from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice, InvoiceItems
from product.models import ProdutItemMaster

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        user = CustomUser.objects.get(username="S-23")
        oustandings = CustomerOutstanding.objects.filter(created_by=user.pk)
        
        for outstanding in oustandings:
            out_amounts = OutstandingAmount.objects.filter(customer_outstanding=outstanding)
            for out_amount in out_amounts:
            
                date_part = timezone.now().strftime('%Y%m%d')
                try:
                    invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                    last_invoice_number = invoice_last_no.invoice_no

                    # Validate the format of the last invoice number
                    parts = last_invoice_number.split('-')
                    if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                        prefix, old_date_part, number_part = parts
                        new_number_part = int(number_part) + 1
                        invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                    else:
                        # If the last invoice number is not in the expected format, generate a new one
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'
                except Invoice.DoesNotExist:
                    random_part = str(random.randint(1000, 9999))
                    invoice_number = f'WTR-{date_part}-{random_part}'
                
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
                    reference_no=f"custom_id{out_amount.customer_outstanding.customer.custom_id}"
                )
                outstanding.invoice_no = invoice.invoice_no
                outstanding.save()
                
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
                
            oustandings.update(invoice_no=invoice.invoice_no)

        self.stdout.write(self.style.SUCCESS('Successfully updated visit schedule for customers with visit_schedule="Saturday"'))