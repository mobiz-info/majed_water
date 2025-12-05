from decimal import Decimal
from django.core.management.base import BaseCommand

from django.db.models import Sum, F, DecimalField

from accounts.models import Customers
from invoice_management.models import Invoice
from client_management.models import CustomerOutstandingReport


class Command(BaseCommand):
    help = "Fix all customer outstanding reports by recalculating pending invoice amounts"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("============== FIX OUTSTANDING REPORT STARTED =============="))

        customers = Customers.objects.all()

        for customer in customers:
            # --------------------------------------------------------
            # 1️⃣ Calculate pending invoice amount for this customer
            # --------------------------------------------------------
            result = Invoice.objects.filter(
                customer=customer,
                is_deleted=False
            ).aggregate(
                pending=Sum(
                    F("amout_total") - F("amout_recieved"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )

            pending = result["pending"] or Decimal("0.00")

            self.stdout.write(f"\nCustomer: {customer.customer_name} (ID: {customer.pk})")
            self.stdout.write(f"Pending invoice amount: {pending}")

            # --------------------------------------------------------
            # 2️⃣ Update/Create Outstanding Report
            # --------------------------------------------------------
            report, created = CustomerOutstandingReport.objects.update_or_create(
                customer=customer,
                product_type="amount",
                defaults={"value": pending},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"➡ Created OutstandingReport = {pending}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"➡ Updated OutstandingReport → {report.value}"))

        self.stdout.write(self.style.WARNING("\n============== FIX OUTSTANDING REPORT COMPLETED =============="))
