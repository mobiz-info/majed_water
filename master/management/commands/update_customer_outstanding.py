import random
from datetime import datetime
from django.utils import timezone
from django.db import transaction
import pandas as pd
from decimal import Decimal
from accounts.models import CustomUser, Customers
from client_management.models import CustomerOutstanding, OutstandingAmount, CustomerOutstandingReport
from invoice_management.models import Invoice, InvoiceItems
from product.models import ProdutItemMaster

# Read the Excel file
file_path = '/home/ra/Downloads/S-41 Credit export software.xlsx'
data = pd.read_excel(file_path)
print("File path:", file_path)
print("DataFrame columns:", data.columns)

# Strip any leading/trailing whitespace from column names
data.columns = data.columns.str.strip()
print("Stripped DataFrame columns:", data.columns)

# Verify that 'amount' column exists
if 'amount' not in data.columns:
    raise KeyError("Column 'amount' not found in the DataFrame. Available columns: " + ", ".join(data.columns))

# Assuming the excel columns are named as follows:
# 'customer_name', 'product_type', 'amount', 'created_by', 'modified_by'

@transaction.atomic
def populate_models_from_excel(data):
    user = CustomUser.objects.get(username="zeeshan")
    for index, row in data.iterrows():
        customer_id = row['customer_id']
        customer_name = row['customer_name']
        amount = Decimal(row['amount'])
        str_date = str(row['date'])
        
        if isinstance(str_date, str):
            str_date = str_date.split()[0]  # Take only the date part if it includes time
        date = datetime.strptime(str_date, '%Y-%m-%d')
        
        # Get or create customer
        try:
            customer = Customers.objects.get(custom_id=customer_id)
        except Customers.DoesNotExist:
            print(f"Customer {customer_name} does not exist.")
            continue
        
        # outstanding_in = CustomerOutstanding.objects.filter(customer=customer,product_type='amount')
        # for i in outstanding_in:
        #     Invoice.objects.filter(invoice_no=i.invoice_no).delete()
        # outstanding_in.delete()
        # CustomerOutstandingReport.objects.filter(customer=customer,product_type='amount').delete()

        customer_outstanding = CustomerOutstanding.objects.create(
            customer=customer,
            product_type='amount',
            created_by=user.id,
            modified_by=user.id,
            created_date=date,
        )

        # Create OutstandingAmount
        outstanding_amount = OutstandingAmount.objects.create(
            customer_outstanding=customer_outstanding,
            amount=amount
        )

        # Update or create CustomerOutstandingReport
        if (instances:=CustomerOutstandingReport.objects.filter(customer=customer,product_type='amount')).exists():
            report = instances.first()
        else:
            report = CustomerOutstandingReport.objects.create(customer=customer,product_type='amount')

        report.value += amount
        report.save()
        
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
            created_date=outstanding_amount.customer_outstanding.created_date,
            net_taxable=outstanding_amount.amount,
            vat=0,
            discount=0,
            amout_total=outstanding_amount.amount,
            amout_recieved=0,
            customer=outstanding_amount.customer_outstanding.customer,
            reference_no=f"custom_id{outstanding_amount.customer_outstanding.customer.custom_id}"
        )
        customer_outstanding.invoice_no = invoice.invoice_no
        customer_outstanding.save()
        
        if outstanding_amount.customer_outstanding.customer.sales_type == "CREDIT":
            invoice.invoice_type = "credit_invoive"
            invoice.save()

        # Create invoice items
        item = ProdutItemMaster.objects.get(product_name="5 Gallon")
        InvoiceItems.objects.create(
            category=item.category,
            product_items=item,
            qty=0,
            rate=outstanding_amount.customer_outstanding.customer.rate,
            invoice=invoice,
            remarks='invoice genereted from backend reference no : ' + invoice.reference_no
        )

        print(f"Processed row {index + 1} for customer {customer_name}")

# Execute the function
populate_models_from_excel(data)
