from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser,Group,Permission

from coupon_management.models import Coupon
from master.models import *
from product.models import ProdutItemMaster

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('Branch User', 'Branch User'),
        ('Driver', 'Driver'),
        ('Salesman', 'Salesman'),
        ('Supervisor', 'Supervisor'),
        ('Manager', 'Manager'),
        ('Customer Care', 'Customer Care'),
        ('Accounts', 'Accounts'),
        ('store_keeper', 'Store Keeper'),
    )
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, null=True, blank=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='user_branch')
    designation_id = models.ForeignKey('master.DesignationMaster', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='user_designation')
    staff_id = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    blood_group = models.CharField(max_length=16, null=True, blank=True)
    permanent_address = models.TextField(null=True,blank=True)
    present_address = models.TextField(null=True,blank=True)
    labour_card_no = models.CharField(max_length=1024, null=True, blank=True)
    labour_card_expiry = models.DateTimeField( null=True, blank=True)
    driving_licence_no = models.CharField(max_length=1024, null=True, blank=True)
    driving_licence_expiry = models.DateTimeField( null=True, blank=True)
    licence_issued_by = models.ForeignKey('master.EmirateMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='licence_emirate')
    visa_issued_by = models.ForeignKey('master.EmirateMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='user_emirate')
    visa_no = models.CharField(max_length=50, null=True, blank=True)
    visa_expiry = models.DateTimeField( null=True, blank=True)
    emirates_id_no = models.CharField(max_length=50, null=True, blank=True)
    emirates_expiry = models.DateTimeField(null=True, blank=True)
    health_card_no = models.CharField(max_length=50, null=True, blank=True)
    health_card_expiry = models.DateTimeField(null=True, blank=True)
    base_salary = models.CharField(max_length=50, null=True, blank=True)
    wps_percentage = models.CharField(max_length=50, null=True, blank=True)
    wps_ref_no = models.CharField(max_length=50, null=True, blank=True)
    insurance_no = models.CharField(max_length=50, null=True, blank=True)
    insurance_expiry = models.DateTimeField(null=True, blank=True)
    insurance_company = models.CharField(max_length=50, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')
    user_management = models.BooleanField(default=True)
    product_management = models.BooleanField(default=True)
    masters = models.BooleanField(default=True)
    van_management = models.BooleanField(default=True)
    coupon_management = models.BooleanField(default=True)
    client_management = models.BooleanField(default=True)
    nationality = models.TextField(null=True,blank=True)
    visa_type = models.CharField(max_length=50, null=True, blank=True)
    joining_date = models.DateTimeField(null=True, blank=True)
    passport_expiry = models.DateTimeField(null=True, blank=True)
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    #class Meta:
    #    ordering = ('username',)

    def __str__(self):
       return str(self.username)
    
    def get_fullname(self):
        return f'{self.first_name} {self.last_name}'
    
# Create your models here.
class Customers(models.Model):
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=250, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    custom_id = models.CharField(max_length=250, null=True, blank=True)
    customer_name = models.CharField(max_length=250, null=True, blank=True)
    building_name = models.CharField(max_length=250, null=True, blank=True)
    door_house_no =  models.CharField(max_length=250, null=True, blank=True)
    floor_no = models.CharField(max_length=250, null=True, blank=True)
    sales_staff = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='customer_staff')
    routes = models.ForeignKey('master.RouteMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='customer_route')
    location = models.ForeignKey('master.LocationMaster', on_delete=models.SET_NULL, null=True, blank=False)
    emirate = models.ForeignKey('master.EmirateMaster', on_delete=models.SET_NULL, null=True, blank=False)
    mobile_no = models.CharField(max_length=250, null=True, blank=True)
    whats_app = models.CharField(max_length=250, null=True, blank=True)
    email_id = models.CharField(max_length=250, null=True, blank=True)
    gps_latitude = models.CharField(max_length=100, null=True, blank=True)
    gps_longitude = models.CharField(max_length=100, null=True, blank=True)
    CUSTOMER_TYPE_CHOICES = (
        ('HOME', 'HOME'),
        ('CORPORATE', 'CORPORATE'),
        ('SHOP', 'SHOP')
    )
    SALES_TYPE_CHOICES = (
        ('CASH COUPON', 'CASH COUPON'),
        ('FOC', 'FOC'),
        ('CASH', 'CASH'),
        ('CREDIT', 'CREDIT')
    )
    customer_type = models.CharField(max_length=100, choices=CUSTOMER_TYPE_CHOICES, null=True, blank=True)
    sales_type = models.CharField(max_length=100, choices=SALES_TYPE_CHOICES, null=True, blank=True)
    no_of_bottles_required = models.IntegerField(null=True,blank=True)
    max_credit_limit = models.IntegerField(null=True,blank=True)
    credit_days = models.IntegerField(null=True,blank=True)
    no_of_permitted_invoices = models.IntegerField(null=True,blank=True)
    trn = models.CharField(max_length=100, null=True, blank=True)
    billing_address = models.CharField(max_length=100, null=True, blank=True)
    preferred_time = models.CharField(max_length=100, null=True, blank=True)
    branch_id = models.ForeignKey('master.BranchMaster', on_delete=models.SET_NULL, null=True, blank=True,related_name='branch_customer')
    is_active = models.BooleanField(default=True)
    visit_schedule = models.JSONField(null=True,blank=True)
    is_editable = models.BooleanField(default=True)
    user_id = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,related_name='user_sign')
    rate = models.CharField(max_length=100, null=True, blank=True)
    coupon_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.customer_name)
    
    def get_water_rate(self):
        from decimal import Decimal

        if Decimal(self.rate) > 0:
            rate = Decimal(self.rate)
        else:
            rate = Decimal(ProdutItemMaster.objects.get(product_name="5 Gallon").rate)
        return rate
        # if int(self.rate) > 0 :
        #     rate = self.rate
        # else:
        #     rate = ProdutItemMaster.objects.get(product_name="5 Gallon").rate
        # return rate

class Staff_Day_of_Visit(models.Model):
    visit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=False)
    # customer = models.OneToOneField(Customers, on_delete=models.CASCADE, related_name='staff_day_of_visit')

    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    week1 = models.BooleanField(default=False)
    week2 = models.BooleanField(default=False)
    week3 = models.BooleanField(default=False)
    week4 = models.BooleanField(default=False)
    week5 = models.BooleanField(default=False)

class Attendance_Log(models.Model):
    attendance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.CharField(max_length=250, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    punch_in_date = models.DateField(auto_now_add=True, null=True, blank=True)
    punch_in_time = models.TimeField(auto_now=True, null=True, blank=True)
    punch_out_date = models.DateField(null=True, blank=True)
    punch_out_time = models.TimeField(null=True, blank=True)
    staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='staff_attendance_log')

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return str(self.punch_in_date) + "/" + str(self.staff)
    

class UserOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True, blank=True,)
    mobile = models.CharField(max_length=250, null=True, blank=True)
    otp = models.CharField(max_length=6)
    expire_time = models.CharField(max_length=1024, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True, blank=True, related_name='created_by')
    created_on = models.DateTimeField(auto_now=True)


class Send_Notification(models.Model):
    device_token = models.CharField(null=True,max_length=1024)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True)
    created_on = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    noticication_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now=True)
    device_token = models.CharField(null=True,max_length=1024)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True)
    title = models.CharField(null=True,max_length=1024)
    body = models.CharField(null=True,max_length=1024)


    class Meta:
        ordering = ('-created_on',)
        
class LocationUpdate(models.Model):
    location_update_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    van = models.ForeignKey('van_management.Van', on_delete=models.CASCADE,null=True, blank=True,)
    salesman = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='LocationUpdate_Salesman')
    location = models.CharField(max_length=255, null=True, blank=True)  
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    battery_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f'{self.van} - {self.salesman} - {self.location}'
    

class CustomerRateHistory(models.Model):
    rate_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True, blank=True)
    previous_rate = models.CharField(max_length=100, null=True, blank=True)
    new_rate = models.CharField(max_length=100, null=True, blank=True)
    created_date = models.DateTimeField(default=datetime.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,null=True, blank=True, related_name='new_customer_rate')

    class Meta:
        ordering = ('-created_date',)

    def __str__(self):
        return f"{self.customer.customer_name} - {self.created_date}"
