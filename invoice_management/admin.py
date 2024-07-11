from django.contrib import admin
from .models import *

# Register your models here.
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer','reference_no','invoice_no','invoice_type','invoice_status','created_date','net_taxable','vat','discount','amout_total','amout_recieved')
    ordering = ("-created_date",)
admin.site.register(Invoice,InvoiceAdmin)

class InvoiceItemsAdmin(admin.ModelAdmin):
    list_display = ('invoice','product_items','qty','rate')
admin.site.register(InvoiceItems,InvoiceItemsAdmin)

admin.site.register(SuspenseCollection)
