# import random
# from datetime import datetime
# from django.utils import timezone
# from django.db import transaction
# import pandas as pd
# from decimal import Decimal
# from accounts.models import CustomUser, Customers
# from client_management.models import CustodyCustom, CustodyCustomItems, CustomerOutstanding, OutstandingAmount, CustomerOutstandingReport
# from invoice_management.models import Invoice, InvoiceItems
# from product.models import ProdutItemMaster

# # Read the Excel file
# file_path = '/home/ra/Downloads/v16credit.xlsx'
# data = pd.read_excel(file_path)
# print("File path:", file_path)
# print("DataFrame columns:", data.columns)

# # Strip any leading/trailing whitespace from column names
# data.columns = data.columns.str.strip()
# print("Stripped DataFrame columns:", data.columns)

# # Verify that 'amount' column exists
# if 'amount' not in data.columns:
#     raise KeyError("Column 'amount' not found in the DataFrame. Available columns: " + ", ".join(data.columns))

# # Assuming the excel columns are named as follows:
# # 'customer_name', 'product_type', 'amount', 'created_by', 'modified_by'

# @transaction.atomic
# def populate_models_from_excel(data):
#     user = CustomUser.objects.get(username="Ramsad")
#     for index, row in data.iterrows():
#         customer_id = row['customer_id']
#         customer_name = row['customer_name']
#         amount = Decimal(row['amount'])
#         str_date = str(row['date'])
        
#         if isinstance(str_date, str):
#             str_date = str_date.split()[0]  # Take only the date part if it includes time
#         date = datetime.strptime(str_date, '%Y-%m-%d')
        
#         # Get or create customer
#         try:
#             customer = Customers.objects.get(custom_id=customer_id)
#         except Customers.DoesNotExist:
#             print(f"Customer {customer_name} does not exist.")
#             continue

#         CustodyCustom.objects.create(
#             created_by=user,
#             created_date=datetime.today(),
#             modified_by=user,
#             modified_date=datetime.today(),
#             customer=customer
#         )
        
#         custody_item = CustodyCustomItems.objects.create(
#             product
#             quantity
#             serialnumber
#             amount
#         )
            

#             # Update or create CustomerCustodyStock
#             if CustomerCustodyStock.objects.filter(customer=custody_custom_data.customer, product=item.product).exists():
#                 stock_instance = CustomerCustodyStock.objects.get(customer=custody_custom_data.customer, product=item.product)
#                 stock_instance.quantity += item.quantity
#                 stock_instance.serialnumber = (stock_instance.serialnumber + ',' + item.serialnumber) if stock_instance.serialnumber else item.serialnumber
#                 stock_instance.agreement_no = (stock_instance.agreement_no + ',' + item.agreement_no) if stock_instance.agreement_no else item.agreement_no
#                 stock_instance.save()
#             else:
#                 CustomerCustodyStock.objects.create(
#                     customer=custody_custom_data.customer,
#                     agreement_no=custody_custom_data.agreement_no,
#                     deposit_type=custody_custom_data.deposit_type,
#                     reference_no=custody_custom_data.reference_no,
#                     product=item.product,
#                     quantity=item.quantity,
#                     serialnumber=item.serialnumber,
#                     amount=item.amount,
#                     can_deposite_chrge=item.can_deposite_chrge,
#                     five_gallon_water_charge=item.five_gallon_water_charge,
#                     amount_collected=custody_custom_data.amount_collected
#                 )
#         print(f"Processed row {index + 1} for customer {customer_name}")

# # Execute the function
# populate_models_from_excel(data)
