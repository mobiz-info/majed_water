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