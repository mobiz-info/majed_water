

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from client_management.models import CustomerCredit
from invoice_management.models import Invoice
from accounts.models import Customers
from decimal import Decimal
from django.db import transaction
from datetime import date
from django.db.models import F


def rebuild_customer_outstanding(customer_code, outstanding_amount):
    """
    Rebuild invoices for a single customer based on outstanding amount

    :param customer_code: Customers.custom_id
    :param outstanding_amount: Decimal or number
    """

    outstanding_amount = Decimal(outstanding_amount or 0)

    customer = Customers.objects.filter(custom_id=str(customer_code).strip()).first()
    if not customer:
        print(f"❌ Customer not found: {customer_code}")
        return False

    print(
        f"\n🔄 Rebuilding customer {customer.custom_id} | "
        f"Outstanding = {outstanding_amount}"
    )

    # -------------------------------------------------
    # NEGATIVE = CUSTOMER CREDIT
    # -------------------------------------------------
    if outstanding_amount < 0:
        credit_amount = abs(outstanding_amount)

        invoices = Invoice.objects.filter(
            customer=customer,
            is_deleted=False
        )

        with transaction.atomic():
            # Mark all invoices PAID
            for inv in invoices:
                inv.amout_recieved = inv.amout_total
                inv.invoice_status = "paid"
                inv.save(update_fields=["amout_recieved", "invoice_status"])

            # Save credit
            CustomerCredit.objects.create(
                customer=customer,
                amount=credit_amount,
                source="manual_rebuild",
                remark="Imported negative outstanding"
            )

        print(f"✅ Credit added: {credit_amount}")
        return True

    # -------------------------------------------------
    # POSITIVE OUTSTANDING
    # -------------------------------------------------
    invoices = Invoice.objects.filter(
        customer=customer,
        is_deleted=False,
        invoice_status="non_paid"
    ).order_by("-created_date")

    if not invoices.exists():
        print(f"⚠ No unpaid invoices for customer {customer_code}")
        return False

    remaining_unpaid = outstanding_amount

    with transaction.atomic():

        for inv in invoices:
            invoice_total = Decimal(inv.amout_total or 0)

            if remaining_unpaid <= 0:
                # fully paid
                inv.amout_recieved = invoice_total
                inv.invoice_status = "paid"

            elif remaining_unpaid >= invoice_total:
                # fully unpaid
                inv.amout_recieved = Decimal("0.00")
                inv.invoice_status = "non_paid"
                remaining_unpaid -= invoice_total

            else:
                # partially paid
                inv.amout_recieved = invoice_total - remaining_unpaid
                inv.invoice_status = "non_paid"
                remaining_unpaid = Decimal("0.00")

            inv.save(update_fields=["amout_recieved", "invoice_status"])

    print(
        f"✔ Customer {customer_code} updated | "
        f"Remaining outstanding = {outstanding_amount}"
    )
    return True


rebuild_customer_outstanding("3309", 2527)