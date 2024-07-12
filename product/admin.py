from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(ProdutItemMaster)
admin.site.register(Product)
admin.site.register(ProductStock)
admin.site.register(Product_Default_Price_Level)
admin.site.register(Staff_Orders)
admin.site.register(ScrapStock)
admin.site.register(WashingStock)
admin.site.register(WashedProductTransfer)
admin.site.register(WashedUsedProduct)
admin.site.register(ScrapcleanedStock)