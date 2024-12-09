from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from accounts.models import *
from coupon_management.models import COUPON_METHOD_CHOICES, Coupon, CouponLeaflet, CouponType, FreeLeaflet, NewCoupon
from product.models import *
from django.http import HttpResponse
from django.db.models import Count,Sum

COUPON_TYPE = (
    ('cash_coupon','Cash Coupon'),
    ('credit_coupon','Credit Coupon'),
)

PAYMENT_METHOD = (
    ('cash','Cash'),
    ('cheque','Cheque'),
)

DEPOSIT_TYPES = (
    ('deposit', 'Deposit'),
    ('non_deposit', 'Non Deposit'),
)

PRODUCT_TYPES = (
    ('amount','Amount'),
    ('emptycan','Emptycan'),
    ('coupons','Coupons'),
)

CUSTOMER_ORDER_PAYMENT_OPTION = (
    ('online','Online Payment'),
    ('cod','Cash on delivery'),
)

CUSTOMER_ORDER_STATUS = (
    ('pending','Pending'),
    ('approve','Approved'),
    ('deliverd','Deliverd'),
    ('reject','Reject'),
)

class CustodyCustom(models.Model):
    custody_custom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE,null=True,blank=True)
    agreement_no = models.CharField(max_length=20, null=True, blank=True)
    total_amount = models.IntegerField(blank=True,null=True)
    deposit_type = models.CharField(max_length=20,choices=DEPOSIT_TYPES,null=True,blank=True)
    reference_no = models.CharField(max_length=100)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ('created_date',)

    def __str__(self):
        return str(self.custody_custom_id)
    
class CustodyCustomItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custody_custom = models.ForeignKey(CustodyCustom, on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey('product.ProdutItemMaster', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(blank=True,null=True)
    serialnumber = models.CharField(max_length=20, null=True, blank=True)
    amount = models.IntegerField(blank=True,null=True)
    can_deposite_chrge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    five_gallon_water_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ('custody_custom__created_date',)

    def __str__(self):
        return str(self.id)
    
class CustomerCustodyStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE,null=True,blank=True)
    agreement_no = models.CharField(max_length=400, null=True, blank=True)
    deposit_type = models.CharField(max_length=20,choices=DEPOSIT_TYPES,null=True,blank=True)
    reference_no = models.CharField(max_length=100)
    product = models.ForeignKey('product.ProdutItemMaster', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(blank=True,null=True)
    serialnumber = models.CharField(max_length=400, null=True, blank=True)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    can_deposite_chrge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    five_gallon_water_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.id)

    

class CustodyCustomDeposit(models.Model):
    DEPOSIT_TYPES = [
        ('cash', 'Cash Deposit'),
        ('cheque', 'Cheque Deposit'),
        ('other', 'Other Deposit'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custody_custom = models.ForeignKey(CustodyCustom,on_delete=models.CASCADE,null=True,blank=True)
    deposit_type = models.CharField(max_length=10, choices=DEPOSIT_TYPES)
    deposit_form_number = models.CharField(max_length=100,)

    
class CustomerReturnReason(models.Model):
    reason_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason =models.CharField(max_length=300)
   
    
    class Meta:
        db_table = 'customer_return_reason'
        verbose_name = ('Customer Return Reason')
        verbose_name_plural = ('Customer Return Reason')
    
    def _str_(self):
        return str(self.pk)
    

class CustomerReturn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE,null=True,blank=True)
    agreement_no = models.CharField(max_length=500, null=True, blank=True)
    reference_no = models.CharField(max_length=100, null=True, blank=True)
    deposit_type = models.CharField(max_length=20,choices=DEPOSIT_TYPES,null=True,blank=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)


    def _str_(self):
        return str(self.id)

class CustomerReturnItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_return = models.ForeignKey(CustomerReturn, on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey('product.ProdutItemMaster', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(blank=True,null=True)
    serialnumber = models.CharField(max_length=520, null=True, blank=True)
    amount = models.IntegerField(blank=True,null=True)

    def _str_(self):
        return str(self.id)
    
class CustomerReturnStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE,null=True,blank=True)
    agreement_no = models.CharField(max_length=500, null=True, blank=True)
    deposit_type = models.CharField(max_length=20,choices=DEPOSIT_TYPES,null=True,blank=True)
    reference_no = models.CharField(max_length=100)
    product = models.ForeignKey('product.ProdutItemMaster', on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(blank=True,null=True)
    serialnumber = models.CharField(max_length=500, null=True, blank=True)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    class Meta:
        ordering = ('id',)

    def __str__(self):
        return str(self.id)


def generate_pay_order(request, custody_item_id):
    custody_item = CustodyCustomItems.objects.get(custody_item_id=custody_item_id)
    # Check if deposit type is set and generate pay order accordingly
    if custody_item.deposit_type:
        # Generate pay order logic based on the deposit type
        # This is just a placeholder example
        pay_order_content = f"Pay Order for {custody_item.deposit_type} deposit"
        return HttpResponse(pay_order_content)
    else:
        return HttpResponse("No deposit type set. Cannot generate pay order.")


def generate_invoice(request, custody_item_id):
    custody_item = CustodyCustomItems.objects.get(custody_item_id=custody_item_id)
    if custody_item.deposit_type:
        invoice_content = f"Invoice for {custody_item.deposit_type} deposit"
        return HttpResponse(invoice_content)
    else:
        return HttpResponse("No deposit type set. Cannot generate invoice.")

class Customer_Inhand_Coupons(models.Model):
    cust_inhand_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.SET_NULL, null=True, blank=True,related_name='cust_coupon')
    no_of_coupons = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.CharField(max_length=20,  blank=True)
    created_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        ordering = ('customer',)

    def __str__(self):
        return str(self.customer)
    

class Vacation(models.Model):
    vacation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete = models.SET_NULL, null = True)
    start_date = models.DateField()
    end_date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    class Meta:
        ordering = ('start_date',)
    def __str__(self):
        return self.customer
    
@receiver(post_save, sender=Vacation)
def delete_expired_vacations(sender, instance, created, **kwargs):
    if not created:
        today = date.today()
        if instance.end_date < today:
            instance.delete()
            
class CustomerCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE,related_name="customercoupon")
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    
    payment_type = models.CharField(max_length=100,choices=PAYMENT_METHOD,null=True,blank=True)
    amount_recieved = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_payeble = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=100)
    coupon_method = models.CharField(max_length=10,choices=COUPON_METHOD_CHOICES,default='manual')
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    class Meta:
        ordering = ('-created_date',)
    def __str__(self):
        return str(self.customer)
    
    def get_coupon_rates(self):
        return list(CustomerCouponItems.objects.filter(customer_coupon=self).values_list('rate', flat=True))
    
    def display_coupon_rates(self):
        rates = self.get_coupon_rates()
        return ", ".join(str(rate) for rate in rates) if rates else "No coupon rates available"

    
class CustomerCouponItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_coupon = models.ForeignKey(CustomerCoupon,on_delete = models.CASCADE, null=True, blank=True)
    coupon = models.ForeignKey(NewCoupon,on_delete = models.CASCADE, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ('-customer_coupon__created_date',)
    def __str__(self):
        return str(self.customer_coupon.customer)
    
    # Function to get count of used coupon leaflets
    def get_used_leaflets(self):
        """Returns the count of used coupon leaflets for this sale."""
        valueable_leaf = CouponLeaflet.objects.filter(coupon=self.coupon, used=True).count()
        free_leaf = FreeLeaflet.objects.filter(coupon=self.coupon, used=True).count()
        return valueable_leaf + free_leaf

    # Function to get count of unused coupon leaflets
    def get_unused_leaflets(self):
        """Returns the count of unused coupon leaflets for this sale."""
        valueable_leaf = CouponLeaflet.objects.filter(coupon=self.coupon, used=False).count()
        free_leaf = FreeLeaflet.objects.filter(coupon=self.coupon, used=False).count()
        return valueable_leaf + free_leaf

    
    def get_available_coupon_count(self):
        valueable_leaf = CouponLeaflet.objects.filter(coupon=self.coupon, used=False).count()
        free_leaf = FreeLeaflet.objects.filter(coupon=self.coupon, used=False).count()
        return valueable_leaf + free_leaf
    
    def customer_leafs(self):
        leafs = CouponLeaflet.objects.filter(coupon=self.coupon,used=False)
        return leafs
    
    def get_per_leaf_rate(self):
        try:
            valuable_leaflets = int(self.coupon.valuable_leaflets)  # Ensure this field exists in NewCoupon
            if valuable_leaflets > 0:
                return self.rate / valuable_leaflets
        except (ValueError, ZeroDivisionError):
            return None
        return None
    
class CustomerCouponStock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_type_id = models.ForeignKey(CouponType, on_delete=models.CASCADE)
    coupon_method = models.CharField(max_length=10,choices=COUPON_METHOD_CHOICES,default='manual')
    customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE)
    count = models.PositiveIntegerField()
   
    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.customer.customer_name)
    
        # Function to get the total sold coupon books count by type (manual and digital)
    @classmethod
    def get_sold_coupons_by_type(cls):
        # Get sold coupons grouped by coupon_type and coupon_method
        sold_coupons = NewCoupon.objects.filter(status=True).values('coupon_type__coupon_type_name', 'coupon_method').annotate(sold_count=Count('coupon_id'))
        
        result = {}
        total_manual = 0
        total_digital = 0
        
        for coupon in sold_coupons:
            coupon_type_name = coupon['coupon_type__coupon_type_name']
            coupon_method = coupon['coupon_method']
            sold_count = coupon['sold_count']
            
            # Initialize dictionary for each coupon type
            if coupon_type_name not in result:
                result[coupon_type_name] = {'digital': 0, 'manual': 0}
            
            # Increment the count based on the coupon method
            result[coupon_type_name][coupon_method] += sold_count
            
            # Update the totals
            if coupon_method == 'manual':
                total_manual += sold_count
            elif coupon_method == 'digital':
                total_digital += sold_count
        
        # Add total manual and digital coupons sold across all coupon types
        result['total'] = {'manual': total_manual, 'digital': total_digital}

        return result
    
class ChequeCouponPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_coupon = models.ForeignKey(CustomerCoupon,on_delete = models.CASCADE, null=True, blank=True)
    
    bank = models.CharField(max_length=200)
    cheque = models.CharField(max_length=200)
    cheque_no = models.CharField(max_length=200)
    date = models.DateField()
   
    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.id)
    
class CustomerOutstanding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE, null=True, blank=True)
    product_type = models.CharField(max_length=200, choices=PRODUCT_TYPES)
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField()
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.product_type)
    
    def get_outstanding_count(self):
        if self.product_type == 'amount':
            return OutstandingAmount.objects.filter(customer_outstanding=self).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        if self.product_type == 'coupons':
            return OutstandingCoupon.objects.filter(customer_outstanding=self).aggregate(total_count=Sum('count'))['total_count'] or 0
        if self.product_type == 'emptycan':
            return OutstandingProduct.objects.filter(customer_outstanding=self).aggregate(total_empty_bottle=Sum('empty_bottle'))['total_empty_bottle'] or 0

class OutstandingAmount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_outstanding = models.ForeignKey(CustomerOutstanding, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.id)

class OutstandingProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_outstanding = models.ForeignKey(CustomerOutstanding, on_delete=models.CASCADE)
    empty_bottle = models.IntegerField(default=0)

    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.empty_bottle)
    
class OutstandingCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon_type = models.ForeignKey(CouponType,on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    customer_outstanding = models.ForeignKey(CustomerOutstanding, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.coupon_type)
    
class CustomerOutstandingReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_type = models.CharField(max_length=200, choices=PRODUCT_TYPES)
    value = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return str(self.id)


class CustomerSupply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE)
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    net_payable = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    vat = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    amount_recieved = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    collected_empty_bottle = models.PositiveIntegerField(default=0)
    allocate_bottle_to_pending = models.PositiveIntegerField(default=0)
    allocate_bottle_to_custody = models.PositiveIntegerField(default=0)
    allocate_bottle_to_paid = models.PositiveIntegerField(default=0)
    allocate_bottle_to_free = models.PositiveIntegerField(default=0)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    
    created_by = models.CharField(max_length=30, blank=True)
    created_date = models.DateTimeField()
    modified_by = models.CharField(max_length=20, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
    
    is_edited = models.BooleanField(default=False)
    outstanding_amount_added = models.BooleanField(default=False)
    outstanding_coupon_added = models.BooleanField(default=False)
    outstanding_bottle_added = models.BooleanField(default=False)
    van_stock_added = models.BooleanField(default=False)
    van_foc_added = models.BooleanField(default=False)
    van_emptycan_added = models.BooleanField(default=False)
    custody_added = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-created_date',)
    def __str__(self):
        return str(self.customer)
    
    def get_total_supply_qty(self):
        return CustomerSupplyItems.objects.filter(customer_supply=self).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
    
    def total_coupon_recieved(self):
        value_leaf = CustomerSupplyCoupon.objects.filter(customer_supply=self).aggregate(Count('leaf'))['leaf__count']
        value_leaf += CustomerSupplyCoupon.objects.filter(customer_supply=self).aggregate(Count('free_leaf'))['free_leaf__count']
        return {
            "manual_coupon": value_leaf,
            "digital_coupon": CustomerSupplyDigitalCoupon.objects.filter(customer_supply=self).aggregate(total_count=Sum('count'))['total_count'] or 0
        }
            

class CustomerSupplyItems(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        customer_supply = models.ForeignKey(CustomerSupply,on_delete = models.CASCADE)
        product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
        quantity = models.PositiveIntegerField()
        amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

        class Meta:
            ordering = ('-id',)
            
        def __str__(self):
            return str(self.customer_supply)
        
        def leaf_count(self):
            return CustomerSupplyCoupon.objects.filter(customer_supply=self.customer_supply).aggregate(Count('leaf'))['leaf__count']
        
class CustomerSupplyCoupon(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        customer_supply = models.ForeignKey(CustomerSupply,on_delete = models.CASCADE)
        leaf = models.ManyToManyField(CouponLeaflet)
        free_leaf = models.ManyToManyField(FreeLeaflet)

        class Meta:
            ordering = ('-id',)
            
        def __str__(self):
            return str(self.customer_supply)
        
class CustomerSupplyDigitalCoupon(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        customer_supply = models.ForeignKey(CustomerSupply,on_delete = models.CASCADE)
        count = models.PositiveIntegerField()

        class Meta:
            ordering = ('-id',)
            
        def __str__(self):
            return str(self.customer_supply)
        
class CustomerSupplyStock(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
        customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE)
        stock_quantity = models.PositiveIntegerField(default=0)  

        class Meta:
            ordering = ('-id',)
            
        def __str__(self):
            return str(self.product)
        
class Competitors(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        competitor_name=models.CharField(max_length=30, blank=True)
        
        class Meta:
            ordering = ('-id',)
            
class MarketShare(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
        customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE)
        competitor=models.ForeignKey(Competitors,on_delete = models.CASCADE)
        quantity=models.PositiveIntegerField(default=0)
        price = models.PositiveIntegerField(default=0)
        
        created_by = models.CharField(max_length=30, blank=True)
        created_date = models.DateTimeField(auto_now_add=True)
        modified_by = models.CharField(max_length=20, null=True, blank=True)
        modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
        
        class Meta:
            ordering = ('-id',)
            
        def __str__(self):
            return str(self.product)
        
        
class CustomerOrders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True, blank=True)
    delivery_date = models.DateField()
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=10,choices=CUSTOMER_ORDER_STATUS)
    
    created_by = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=200, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer}"
    
class CustomerOrdersItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_order = models.ForeignKey(CustomerOrders, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.DecimalField(default=1, max_digits=10, decimal_places=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product} - Quantity: {self.quantity}"
        
# class CustomerOrders(models.Model):
#         id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#         product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
#         customer = models.ForeignKey('accounts.Customers',on_delete = models.CASCADE)
#         quantity = models.DecimalField(default=0, max_digits=10, decimal_places=2)
#         amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
#         gand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
#         delivery_date = models.DateField()
#         payment_option = models.CharField(max_length=10,choices=CUSTOMER_ORDER_PAYMENT_OPTION)
#         order_status = models.CharField(max_length=10,choices=CUSTOMER_ORDER_STATUS)
        
#         created_by = models.CharField(max_length=100, blank=True)
#         created_date = models.DateTimeField(auto_now_add=True)
#         modified_by = models.CharField(max_length=20, null=True, blank=True)
#         modified_date = models.DateTimeField(auto_now=True ,blank=True, null=True)
        
#         class Meta:
#             ordering = ('-created_date',)
            
#         def __str__(self):
#             return str(self.product)



class NonVisitReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason_text = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.reason_text


class NonvisitReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('accounts.Customers', on_delete=models.CASCADE)
    salesman = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    reason = models.ForeignKey(NonVisitReason, on_delete=models.CASCADE)
    supply_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f'{self.customer} - {self.salesman} - {self.reason}'
    
class CustomerCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True, blank=True)
    delivery_date = models.DateField()
    grand_total = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    order_status = models.BooleanField(default=False)
    
    created_by = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=200, null=True, blank=True)
    modified_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer}"
    
class CustomerCartItems(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_cart = models.ForeignKey(CustomerCart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.DecimalField(default=1, max_digits=10, decimal_places=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product} - Quantity: {self.quantity}"
    

class DialyCustomers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    route = models.ForeignKey('master.RouteMaster', on_delete=models.CASCADE)
    qty = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    is_emergency = models.BooleanField(default=False)
    is_supply = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.customer.customer_name} - Quantity: {self.qty}"
    

class InactiveCustomers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    inactive_days = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.customer.customer_name} - In Active Days: {self.inactive_days}"
    
class EligibleCustomerConditions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.ForeignKey(ProdutItemMaster, on_delete=models.CASCADE)
    moq = models.PositiveIntegerField(default=0)
    days = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.category_name.product_name}"