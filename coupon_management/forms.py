from django import forms
from django.forms import ModelForm
from .models import *

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

class CreateCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields=['coupon_type_id','coupon_method','book_num','value_starting_no','value_ending_no','free_starting_no','free_ending_no','branch_id','status']
        widgets = {
            'coupon_type_id': forms.Select(attrs={'class': 'form-control'}),
            'coupon_method': forms.Select(attrs={'class': 'form-control'}),
            'book_num': forms.TextInput(attrs={'class': 'form-control'}),
            'value_starting_no': forms.TextInput(attrs={'class': 'form-control'}),
            'value_ending_no': forms.TextInput(attrs={'class': 'form-control'}),
            'free_starting_no': forms.TextInput(attrs={'class': 'form-control'}),
            'free_ending_no': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_id': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
      
class EditCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields=['coupon_type_id','book_num','value_starting_no','value_ending_no','free_starting_no','free_ending_no','branch_id','status']
        widgets = {
            'coupon_type_id': forms.Select(attrs={'class': 'form-control'}),
            'book_num': forms.TextInput(attrs={'class': 'form-control'}),
            'value_starting_no': forms.TextInput(attrs={'class': 'form-control'}),
            'value_ending_no': forms.TextInput(attrs={'class': 'form-control'}),
            'free_starting_no': forms.TextInput(attrs={'class': 'form-control'}),
            'free_ending_no': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_id': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
        
class CouponRequestForm(forms.ModelForm):
    class Meta:
        model = CouponRequest
        fields=['quantity','coupon_type_id','branch_id','status',]
        widgets = {
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'coupon_type_id': forms.Select(attrs={'class': 'form-control'}),
            'branch_id': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

class AssignStaffCouponForm(forms.ModelForm):
    class Meta:
        model = AssignStaffCoupon
        fields = [ 'alloted_quantity']

        widgets = {
            
            'alloted_quantity': forms.TextInput(attrs={'class': 'form-control'}),

        }
class AssignStaffCouponDetailsForm(forms.ModelForm):
    class Meta:
        model = AssignStaffCouponDetails
        fields = [ 'to_customer','coupon']

        widgets = {
            
            'to_customer': forms.Select(attrs={'class': 'form-control'}),
            'coupon': forms.Select(attrs={'class': 'form-control'}),


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