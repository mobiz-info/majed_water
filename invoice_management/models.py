import random
import uuid
from django.db import models

from accounts.models import CustomUser, Customers
from master.models import CategoryMaster, RouteMaster
from product.models import Product, ProdutItemMaster

# Create your models here.
INVOICE_TYPES = (
    ('cash_invoice', 'Cash Invoice'),
    ('credit_invoive', 'Credit Invoice'),
)

INVOICE_STATUS = (
    ('non_paid', 'Non Paid'),
    ('paid', 'Paid'),
)

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_no = models.CharField(max_length=200)
    invoice_no = models.CharField(max_length=200)
    invoice_type = models.CharField(max_length=200, choices=INVOICE_TYPES,default='cash_invoice')
    invoice_status = models.CharField(max_length=200, choices=INVOICE_STATUS,default='non_paid')
    created_date = models.DateTimeField()
    net_taxable = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    vat = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amout_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amout_recieved = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'invoice'
        verbose_name = ('Invoice')
        verbose_name_plural = ('Invoice')
    
    def __str__(self):
        return f'{self.id}'
    
    def invoice_items (self):
        items = InvoiceItems.objects.filter(invoice=self)
        return items
    
    def sub_total(self):
        total = 0
        
        items = InvoiceItems.objects.filter(invoice=self)
        for item in items:
            total += item.total_including_vat
        return total
    
    def total_qty(self):
        total = 0
        items = InvoiceItems.objects.filter(invoice=self)
        for item in items:
            total += item.qty
        return total
    
    def items_total_discount_amount(self):
        total = 0
        # Calculate the sub-total for SalesItems
        items =  InvoiceItems.objects.filter(invoice=self)
        for item in items:
            total += item.total_including_vat
        total = total - self.discount
        return total
    
class InvoiceItems(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_including_vat = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    remarks = models.TextField()
    is_deleted = models.BooleanField(default=False)
    
    category = models.ForeignKey(CategoryMaster, on_delete=models.CASCADE,null=True,blank=True)
    product_items = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'invoice_items'
        verbose_name = ('Invoice Items')
        verbose_name_plural = ('Invoice Items')
    
    def __str__(self):
        return str(self.invoice.invoice_no)
    
class InvoiceDailyCollection(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    salesman = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    created_date = models.DateTimeField()
    
    class Meta:
        db_table = 'invoice_dialy_collection'
        verbose_name = ('Invoice Dialy Collection')
        verbose_name_plural = ('Invoice Dialy Collection')
    
    def __str__(self):
        return str(self.invoice.invoice_no)
    
class SuspenseCollection(models.Model):
    created_date = models.DateTimeField()
    date = models.DateTimeField()
    salesman = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    route = models.ForeignKey(RouteMaster, on_delete=models.CASCADE)
    
    cash_sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    credit_sale_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense = models.DecimalField(max_digits=10, decimal_places=2)
    net_payeble_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    amount_balance = models.DecimalField(max_digits=10, decimal_places=2)
    reference_no = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'suspense_collection'
        verbose_name = ('Suspense Collection')
        verbose_name_plural = ('Suspense Collection')
    
    def __str__(self):
        return str(self.salesman)