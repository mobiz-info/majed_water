from django.contrib import admin

from master.models import *

# Register your models here.
admin.site.register(CategoryMaster)
class EmiratesAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','name']
admin.site.register(EmirateMaster,EmiratesAdmin)