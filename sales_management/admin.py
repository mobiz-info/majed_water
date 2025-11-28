import uuid
from django.contrib import admin
from . models import *

# Register your models here.
class CollectionPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'payment_method', 'amount_received', 'receipt_number', 'created_date')
    search_fields = ('customer__customer_name',)   # <-- Add this

admin.site.register(CollectionPayment, CollectionPaymentAdmin)
admin.site.register(CollectionItems)
admin.site.register(CollectionCheque)
admin.site.register(Receipt)