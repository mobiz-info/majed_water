
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice
from accounts.models import Customers
from decimal import Decimal
from django.db import transaction
from django.utils.timezone import make_aware
from datetime import datetime

# def rebuild_customer_invoices(customer_code, outstanding_amount):
#     """
#     Rebuild invoices for ONE customer using outstanding amount.
    
#     Logic:
#     - Sum invoice totals
#     - paid_amount = total - outstanding
#     - Apply payments FIFO (oldest invoices first)
#     """

#     outstanding_amount = Decimal(outstanding_amount)

#     customer = Customers.objects.filter(custom_id=customer_code).first()
#     if not customer:
#         print(f"❌ Customer not found: {customer_code}")
#         return False

#     invoices = Invoice.objects.filter(
#         customer=customer,
#         is_deleted=False
#     ).order_by("created_date")

#     if not invoices.exists():
#         print(f"⚠ No invoices for customer {customer_code}")
#         return False

#     invoice_total_sum = sum(
#         Decimal(inv.amout_total or 0) for inv in invoices
#     )

#     paid_amount = invoice_total_sum - outstanding_amount
#     remaining_paid = paid_amount

#     print("\n🔄 Rebuilding invoices")
#     print("Customer:", customer.customer_name)
#     print("Total invoice amount:", invoice_total_sum)
#     print("Outstanding:", outstanding_amount)
#     print("Paid amount to distribute:", paid_amount)

#     with transaction.atomic():
#         for inv in invoices:
#             invoice_total = Decimal(inv.amout_total or 0)

#             if remaining_paid <= 0:
#                 inv.amout_recieved = Decimal("0.00")
#             else:
#                 receive_now = min(invoice_total, remaining_paid)
#                 inv.amout_recieved = receive_now
#                 remaining_paid -= receive_now

#             inv.invoice_status = (
#                 "paid"
#                 if inv.amout_recieved == invoice_total
#                 else "non_paid"
#             )

#             inv.save(update_fields=["amout_recieved", "invoice_status"])

#             print(
#                 f"Invoice {inv.invoice_no} | "
#                 f"Total={invoice_total} | "
#                 f"Received={inv.amout_recieved} | "
#                 f"Status={inv.invoice_status}"
#             )

#     print("✅ Rebuild completed\n")
#     return True

# rebuild_customer_invoices("3404", 1310)


# ROUTE_NAME = "V-5"   # or use route_id
# START_DATE = make_aware(datetime(2025, 1, 1))
# END_DATE = make_aware(datetime(2025, 12, 18, 22, 59, 59))

# # -------------------------------------------------
# # GET CUSTOMERS IN ROUTE
# # -------------------------------------------------
# customers = Customers.objects.filter(
#     routes__route_name=ROUTE_NAME,
#     is_deleted=False
# )

# if not customers.exists():
#     print(f"❌ No customers found for route {ROUTE_NAME}")
#     exit()

# print(f"\nProcessing route: {ROUTE_NAME}")
# print(f"Period: {START_DATE.date()} to {END_DATE.date()}")
# print(f"Total customers: {customers.count()}\n")

# updated_count = 0
# skipped_count = 0

# # -------------------------------------------------
# # PROCESS EACH CUSTOMER
# # -------------------------------------------------
# for customer in customers:

#     invoices = Invoice.objects.filter(
#         customer=customer,
#         created_date__range=(START_DATE, END_DATE),
#         invoice_type = "credit_invoice",
#         is_deleted=False
#     )

#     if not invoices.exists():
#         continue

#     for inv in invoices:

#         invoice_total = Decimal(inv.amout_total or 0)

#         co = CustomerOutstanding.objects.filter(
#             customer=customer,
#             invoice_no=inv.invoice_no,
#             product_type="amount"
#         ).first()

#         if not co:
#             skipped_count += 1
#             continue

#         oa = OutstandingAmount.objects.filter(
#             customer_outstanding=co
#         ).first()

#         if not oa:
#             skipped_count += 1
#             continue

#         # ✅ ONLY UPDATE OutstandingAmount.amount
#         if Decimal(oa.amount) != invoice_total:
#             oa.amount = invoice_total
#             oa.save(update_fields=["amount"])
#             updated_count += 1
#             print(
#                 f"🔧 {customer.custom_id} | "
#                 f"{inv.invoice_no} → {invoice_total}"
#             )

# # -------------------------------------------------
# # DONE
# # -------------------------------------------------
# print("\n🎉 FINISHED")
# print(f"✅ Updated OutstandingAmount rows: {updated_count}")
# print(f"⚠️ Skipped (missing data): {skipped_count}\n")


start_date = make_aware(datetime(2025, 1, 1))
end_date = make_aware(datetime(2025, 12, 18, 23, 59, 59))

route = "van21"

invoices = Invoice.objects.filter(
    created_date__range=(start_date, end_date),
    customer__routes__route_name=route,
    is_deleted=False
)

updated_count = 0

for inv in invoices:

    invoice_amount = inv.amout_total or 0
    invoice_no = inv.invoice_no
    customer = inv.customer

    # Fetch existing CustomerOutstanding (NO CREATE)
    outstanding = CustomerOutstanding.objects.filter(
        customer=customer,
        invoice_no=invoice_no,
        product_type="amount"
    ).first()

    if not outstanding:
        continue  # skip if header not exist

    # Fetch existing OutstandingAmount rows
    outstanding_row = OutstandingAmount.objects.filter(
        customer_outstanding=outstanding
    ).first()

    if not outstanding_row:
        continue  # skip if no amount row exists

    # Compare and update
    if float(outstanding_row.amount) != float(invoice_amount):

        old_amount = outstanding_row.amount
        outstanding_row.amount = invoice_amount
        outstanding_row.save()

        updated_count += 1

        print(
            f"Updated {invoice_no}: {old_amount} → {invoice_amount}"
        )

print(
    f"\nFinished! Updated {updated_count} outstanding amount records for route all."
)