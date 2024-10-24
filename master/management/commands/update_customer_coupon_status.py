from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from client_management.models import CustomerCouponItems
from coupon_management.models import CouponLeaflet, CouponStock, NewCoupon
from van_management.models import VanCouponStock

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        coupons = NewCoupon.objects.all()
        
        for coupon in coupons:
            coupon_status = CouponStock.objects.get(couponbook=coupon)
            if CustomerCouponItems.objects.filter(coupon=coupon).exists():
                coupon_status.coupon_stock = "customer"
                
            elif VanCouponStock.objects.filter(coupon=coupon).exists():
                coupon_status.coupon_stock = "van"
            
            else:
                coupon_status.coupon_stock = "company"
            
            valuable_leafs = CouponLeaflet.objects.filter(coupon=coupon,used=False).count()
            free_leafs = CouponLeaflet.objects.filter(coupon=coupon,used=False).count()
            total_leaf_count = valuable_leafs + free_leafs
            if total_leaf_count == 0:
                coupon.status = True
                
                coupon_status.coupon_stock = "used"

            coupon.save()
            coupon_status.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated coupon {coupon.book_num}'))
            
        self.stdout.write(self.style.WARNING(f'Successfully updated All Coupons'))
