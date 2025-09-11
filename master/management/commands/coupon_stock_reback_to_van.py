from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers
from client_management.models import CustomerCouponItems
from coupon_management.models import CouponStock
from invoice_management.models import Invoice

class Command(BaseCommand):
    help = 'Add credit invoice type based on customer'

    def handle(self, *args, **kwargs):
        customer_coupon_item_coupon_ids = CustomerCouponItems.objects.all().values_list("coupon__pk")
        coupon_stock = CouponStock.objects.exclude(couponbook__pk__in=customer_coupon_item_coupon_ids)
        for i in coupon_stock:
           print(i.couponbook.book_num)

        self.stdout.write(self.style.SUCCESS('Successfully updated into credit invoice'))