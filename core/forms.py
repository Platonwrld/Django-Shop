from secrets import choice
from django import forms 
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForms(forms.Form):

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
    }))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Email',
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Street Address',
    }))
    street_address_optional = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Optional Address',
    }))
    country = CountryField(blank_label='select country').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'
    }))
    same_billing_address = forms.BooleanField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Billing Address',
    })) #
    save_info = forms.BooleanField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Save',
    }))
    payment_options = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)