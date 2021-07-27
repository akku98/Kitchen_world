from random import choices
from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import fields
from django.forms.fields import CharField, IntegerField
from localflavor.in_.in_states import STATE_CHOICES
from .models import UserAddress

class user_form(forms.Form):  #forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}), max_length=50, required=True,error_messages={'required': 'Please enter first name!'}) 
    first_name = forms.CharField(max_length=50, required=True,error_messages={'required': 'Please enter first name!'})
    last_name = forms.CharField( max_length=50, required=True,error_messages={'required': 'Please enter first name!'})
    user_name = forms.CharField(max_length=50, required=True,error_messages={'required': 'Please enter username!'}) 
    user_email = forms.EmailField(error_messages={'required': 'Please enter you email !'})
    user_pass = forms.CharField( widget=forms.PasswordInput,max_length=10, required=True,error_messages={'required': 'Please enter password!'})  

class LoginForm(forms.Form):
    username = forms.CharField( max_length=50, required=True,error_messages={'required': 'Please enter username!'})   
    password =  forms.CharField(widget=forms.PasswordInput,max_length=10, required=True,error_messages={'required': 'Please enter password!'}) 

class ContactForm(forms.Form):
    uname = forms.CharField( max_length=50, required=True) 
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=12, required=True) 
    desc = forms.CharField(widget=forms.Textarea, error_messages={'required': 'Please enter message!'}) 

class UserAddressForm(forms.ModelForm) :
    CHOICES = [('Billing_Address',"Billing Address"),('Shipping_Address','Shipping Address')]
    address_type = forms.ChoiceField(choices=CHOICES, required=True)
    class Meta:
        model = UserAddress
        
        fields = [
            "address",                     #fields = '__all__'   to show all the fields
            "address2", 
            "city",
            "state", 
            "country",
            "pincode",
            "phoneno" 
            
        ]
       
""" class UserAddressForm(forms.Form) :
    address = forms.CharField(max_length=120, required=True)    
    address2 = forms.CharField(max_length=120) 
    city = forms.CharField(max_length=50 , required=True)
    state = forms.ChoiceField(choices=STATE_CHOICES, required=True)
    country = forms.CharField(max_length=120, required=True)
    pincode = forms.CharField(max_length=6, required=True)
    phoneno = forms.CharField(max_length=12, required=True)
    default_shipping = forms.BooleanField()
    default_billing = forms.BooleanField() """