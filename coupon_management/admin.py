from django.contrib import admin
from . models import *

# Register your models here.
# admin.site.register(NewCoupon)
admin.site.register(CouponLeaflet)
admin.site.register(FreeLeaflet)

@admin.register(NewCoupon)
class NewCouponAdmin(admin.ModelAdmin):
    # List page columns
    list_display = (
        'coupon_id',
        'coupon_type',
        'book_num',
        'no_of_leaflets',
        'valuable_leaflets',
        'free_leaflets',
        'branch_id',
        'coupon_method',
        'status',
        'created_date',
    )

    # Right sidebar filters
    list_filter = (
        'status',
        'coupon_method',
        'coupon_type',
        'branch_id',
        'created_date',
    )

    # Search bar
    search_fields = (
        'coupon_id',
        'book_num',
        'created_by',
       
    )

    # Ordering
    ordering = ('-created_date',)
