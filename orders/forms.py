from django import forms
from .models import ShippingAddress, Order

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'address', 'city', 'state', 'postal_code', 'country', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'})
        }

class OrderCreateForm(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    save_address = forms.BooleanField(required=False, initial=False)
    set_default = forms.BooleanField(required=False, initial=False)