from datetime import datetime
import pandas as pd
from decimal import Decimal
from django.db import transaction
from accounts.models import CustomUser, Customers
from client_management.models import CustomerOutstanding, OutstandingAmount, CustomerOutstandingReport

# Read the Excel file
file_path = '/home/ra/Downloads/outstanding_update_date_wise.xlsx'
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
    user = CustomUser.objects.get(username="SW-40")
    for index, row in data.iterrows():
        customer_name = row['customer_name']
        amount = Decimal(row['amount'])
        str_date = str(row['date'])
        date = datetime.strptime(str_date, '%d-%m-%Y')
        
        # Get or create customer
        try:
            customer = Customers.objects.get(customer_name=customer_name)
        except Customers.DoesNotExist:
            print(f"Customer {customer_name} does not exist.")
            continue

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

        print(f"Processed row {index + 1} for customer {customer_name}")

# Execute the function
populate_models_from_excel(data)
