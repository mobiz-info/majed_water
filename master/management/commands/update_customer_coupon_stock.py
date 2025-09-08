from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from accounts.models import Customers
from client_management.models import CustomerCouponItems, CustomerCouponStock
from coupon_management.models import CouponLeaflet, CouponType, FreeLeaflet, NewCoupon

class Command(BaseCommand):
    help = "Recalculate coupon stock per customer based on unused leaflets (used=False)."

    def handle(self, *args, **options):
        self.stdout.write("Resetting all coupon stock counts to 0...")

        # Reset all stocks
        CustomerCouponStock.objects.update(count=0)

        self.stdout.write("Recalculating stock from leaflets...")

        for customer in Customers.objects.all():
            # Get all coupons assigned to this customer (via items or relation)
            customer_coupons = NewCoupon.objects.filter(
                customercouponitems__customer_coupon__customer=customer
            ).distinct()

            for coupon in customer_coupons:
                # Count unused valuable leaflets
                valuable_unused = CouponLeaflet.objects.filter(
                    coupon=coupon, used=False
                ).count()

                # Count unused free leaflets
                free_unused = FreeLeaflet.objects.filter(
                    coupon=coupon, used=False
                ).count()

                # Total available leaflets for this coupon book
                total_available = valuable_unused + free_unused

                if total_available > 0:
                    stock_obj, created = CustomerCouponStock.objects.get_or_create(
                        coupon_type_id=coupon.coupon_type,
                        coupon_method=coupon.coupon_method,
                        customer=customer,
                        defaults={"count": total_available},
                    )
                    if not created:
                        stock_obj.count += total_available
                        stock_obj.save()

                    self.stdout.write(
                        f"Updated stock for {customer} → "
                        f"{coupon.coupon_type} ({coupon.coupon_method}) = {total_available}"
                    )

        self.stdout.write(self.style.SUCCESS("Coupon stock recalculated successfully ✅"))