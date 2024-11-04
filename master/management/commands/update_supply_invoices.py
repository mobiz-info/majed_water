import datetime
import random

from django.db.models import Q
from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from client_management.models import CustomerSupply, CustomerSupplyItems, DialyCustomers, InactiveCustomers
from invoice_management.models import Invoice, InvoiceDailyCollection, InvoiceItems
from sales_management.models import Receipt

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        date = datetime.datetime.strptime("2024-10-02", '%Y-%m-%d').date()
        invoice_nos  = Invoice.objects.filter(created_date__date__lte=date,is_deleted=False).values_list("invoice_no")
        
        supplies = CustomerSupply.objects.filter(created_date__date__lte=date).exclude(invoice_no__in=invoice_nos)
        for supply in supplies:
            if supply.invoice_no != None and supply.customer.sales_type != "FOC":
                if not Invoice.objects.filter(invoice_no=supply.invoice_no,is_deleted=False).exists():
                    # Create the invoice
                    invoice = Invoice.objects.create(
                        invoice_no=supply.invoice_no,
                        created_date=supply.created_date,
                        net_taxable=supply.net_payable,
                        vat=supply.vat,
                        discount=supply.discount,
                        amout_total=supply.subtotal,
                        amout_recieved=supply.amount_recieved,
                        customer=supply.customer,
                        reference_no="generated from command"
                    )
                    
                    if supply.customer.sales_type == "CREDIT":
                        invoice.invoice_type = "credit_invoive"
                    if invoice.amout_total == invoice.amout_recieved:
                        invoice.invoice_status = "paid"
                    invoice.save()

                    # Create invoice items
                    for item in CustomerSupplyItems.objects.filter(customer_supply=supply):
                        
                        InvoiceItems.objects.create(
                            category=item.product.category,
                            product_items=item.product,
                            qty=item.quantity,
                            rate=item.amount,
                            invoice=invoice,
                            remarks='invoice genereted from supply items reference no : ' + invoice.reference_no
                        )
                        # print("invoice generate")
                    InvoiceDailyCollection.objects.create(
                        invoice=invoice,
                        created_date=supply.created_date,
                        customer=invoice.customer,
                        salesman=supply.customer.sales_staff,
                        amount=invoice.amout_recieved,
                    )

                    invoice_numbers = []
                    invoice_numbers.append(invoice.invoice_no)
                    
                    date_part = supply.created_date.strftime('%Y%m%d')
                    try:
                        # Get the last receipt number
                        reciept_last_no = Receipt.objects.all().latest('created_date')
                        last_reciept_number = reciept_last_no.receipt_number

                        # Validate the format of the last receipt number
                        parts = last_reciept_number.split('-')
                        if len(parts) == 3 and parts[0] == 'RCT' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            r_new_number_part = int(number_part) + 1
                            receipt_number = f'{prefix}-{date_part}-{r_new_number_part:04d}'
                        else:
                            # If the last receipt number is not in the expected format, generate a new one
                            receipt_number = f'RCT-{date_part}-{random.randint(1000, 9999)}'
                    except Receipt.DoesNotExist:
                        # First receipt of the day, generate new format
                        receipt_number = f'RCT-{date_part}-{random.randint(1000, 9999)}'

                    # Check for uniqueness
                    while Receipt.objects.filter(receipt_number=receipt_number).exists():
                        receipt_number = f'RCT-{date_part}-{random.randint(1000, 9999)}'
                        
                    receipt = Receipt.objects.create(
                        transaction_type="supply",
                        instance_id=str(supply.id),  
                        amount_received=supply.amount_recieved,
                        receipt_number=receipt_number,
                        customer=supply.customer,
                        invoice_number=",".join(invoice_numbers)
                    )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {supply.invoice_no}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
