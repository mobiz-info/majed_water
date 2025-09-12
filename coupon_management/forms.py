from django import forms
from django.forms import ModelForm

from accounts.models import CustomUser, Customers
from .models import *
from client_management.models import CustomerCoupon, CustomerCouponItems

class CreateCouponTypeForm(forms.ModelForm):
    class Meta:
        model=CouponType
        fields=['coupon_type_name','no_of_leaflets','valuable_leaflets','free_leaflets',]
        widgets = {
            'coupon_type_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'no_of_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'valuable_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'free_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }


class EditCouponTypeForm(forms.ModelForm):
    class Meta:
        model=CouponType
        fields=['coupon_type_name','no_of_leaflets','valuable_leaflets','free_leaflets',]
        widgets = {
            'coupon_type_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true','readonly': 'readonly'}),
            'no_of_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'valuable_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'free_leaflets': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

#-----------------------------New Coupon FORM---------------------------------
        
class CreateNewCouponForm(forms.ModelForm):
    class Meta:
        model = NewCoupon
        fields=['coupon_type','book_num','no_of_leaflets','valuable_leaflets','free_leaflets','branch_id','status']
        widgets = {
            'coupon_type': forms.Select(attrs={'class': 'form-control'}),
            'book_num': forms.TextInput(attrs={'class': 'form-control'}),
            'no_of_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'valuable_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'free_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_id': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EditNewCouponForm(forms.ModelForm):
    class Meta:
        model = NewCoupon
        fields=['coupon_type','book_num','no_of_leaflets','valuable_leaflets','free_leaflets','branch_id','status']
        widgets = {
            'coupon_type': forms.Select(attrs={'class': 'form-control'}),
            'book_num': forms.TextInput(attrs={'class': 'form-control'}),
            'no_of_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'valuable_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'free_leaflets': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_id': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class CustomerCouponForm(forms.ModelForm):
    class Meta:
        model = CustomerCoupon
        fields = [
            'payment_type','amount_recieved','grand_total','discount','net_amount','total_payeble','balance','reference_number','coupon_method','invoice_no',
        ]
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'amount_recieved': forms.NumberInput(attrs={'class': 'form-control'}),
            'grand_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_payeble': forms.NumberInput(attrs={'class': 'form-control'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'coupon_method': forms.Select(attrs={'class': 'form-control'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class CouponReassignForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customers.objects.filter(is_deleted=False),
        label="Customer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    salesman = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        required=False,
        label="Salesman",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    coupon = forms.ModelChoiceField(
        queryset=NewCoupon.objects.none(),
        label="Un-issued Coupon",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only un-issued coupons
        customer_coupon_item_coupon_ids = (
            CustomerCouponItems.objects.all().values_list("coupon__pk", flat=True)
        )
        coupon_stock = CouponStock.objects.filter(coupon_stock="customer").exclude(
            couponbook__pk__in=customer_coupon_item_coupon_ids
        )
        self.fields["coupon"].queryset = NewCoupon.objects.filter(
            pk__in=coupon_stock.values_list("couponbook__pk", flat=True)
        ).order_by("-created_date")
