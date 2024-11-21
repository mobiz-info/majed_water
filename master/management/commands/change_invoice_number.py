import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers
from client_management.models import CustomerOutstanding
from invoice_management.models import Invoice

class Command(BaseCommand):
    help = 'Add credit invoice type based on customer'

    def handle(self, *args, **kwargs):
        invoices = Invoice.objects.filter(invoice_no="WTR-20240923-7698")
        
        for invoice in invoices:
            date_part = invoice.created_date.strftime('%Y%m%d')
            
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
            
            if (outstanding_instances:=CustomerOutstanding.objects.filter(customer=invoice.customer,invoice_no=invoice.invoice_no)).exists():
                outstanding = outstanding_instances.first()
                outstanding.invoice_no = invoice_number
                outstanding.save()
            
            invoice.invoice_no = invoice_number
            
            if invoice.amout_total == invoice.amout_recieved:
                invoice.invoice_status = "paid"
            else:
                invoice.invoice_status = "non_paid"
            
            if invoice.customer.sales_type=="CREDIT":
                invoice.invoice_type="credit_invoive"
                
            invoice.is_deleted = False
            invoice.save()

            self.stdout.write(self.style.WARNING('Successfully'))
            
        self.stdout.write(self.style.SUCCESS('Successfully updated into credit invoice'))