from django.core.management.base import BaseCommand
from django.db.models import Count

from client_management.models import CustomerCouponStock


class Command(BaseCommand):
    help = "Find customers who have more than one CustomerCouponStock record, grouped by coupon_method"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🔎 Customers with duplicate coupon stocks (grouped by method):"))

        duplicates = (
            CustomerCouponStock.objects
            .values("customer__custom_id", "coupon_method")
            .annotate(stock_count=Count("id"))
            .filter(stock_count__gt=1)
            .order_by("customer__custom_id", "coupon_method")
        )

        if not duplicates.exists():
            self.stdout.write(self.style.SUCCESS("✅ No duplicates found"))
            return

        for d in duplicates:
            customer_name = d["customer__custom_id"] or "Unnamed Customer"
            method = d["coupon_method"] or "N/A"
            stock_count = d["stock_count"]

            self.stdout.write(self.style.WARNING(
                f"⚠️ {customer_name} → {method} → {stock_count} stock records"
            ))


# from django.core.management.base import BaseCommand
# from django.db.models import Count

# from client_management.models import CustomerCouponStock


# class Command(BaseCommand):
#     help = "Delete CustomerCouponStock records with count=0 for customers who have duplicate stocks grouped by coupon_method"

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.MIGRATE_HEADING("🔎 Checking duplicate customer coupon stocks with count=0..."))

#         # Find customers + method with more than one stock
#         duplicates = (
#             CustomerCouponStock.objects
#             .values("customer_id", "coupon_method")
#             .annotate(stock_count=Count("id"))
#             .filter(stock_count__gt=1)
#         )

#         deleted_total = 0

#         for dup in duplicates:
#             customer_id = dup["customer_id"]
#             method = dup["coupon_method"]

#             # Get stocks for this customer & method
#             zero_stocks = CustomerCouponStock.objects.filter(
#                 customer_id=customer_id,
#                 coupon_method=method,
#                 count=0
#             )

#             if zero_stocks.exists():
#                 deleted_count = zero_stocks.count()
#                 deleted_total += deleted_count
#                 customer_name = zero_stocks.first().customer.customer_name

#                 self.stdout.write(self.style.WARNING(
#                     f"⚠️ Deleting {deleted_count} zero-stock entries for {customer_name} → {method}"
#                 ))

#                 zero_stocks.delete()

#         if deleted_total == 0:
#             self.stdout.write(self.style.SUCCESS("✅ No zero-stock duplicates found."))
#         else:
#             self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_total} zero-stock records."))
