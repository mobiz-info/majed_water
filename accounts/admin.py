from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name')
    ordering = ('-id',)
admin.site.register(CustomUser,CustomUserAdmin)

class CustomersAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'created_date', 'custom_id','visit_schedule')
    ordering = ('-created_date',)
admin.site.register(Customers,CustomersAdmin)
