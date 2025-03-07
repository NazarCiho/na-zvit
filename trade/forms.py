from django import forms
from .models import Transaction, Order

class MarketOrderForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.00000001',
                'class': 'form-control',
                'required': True
            }),
        }

class LimitOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['amount', 'limit_price']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.00000001',
                'class': 'form-control',
                'required': True
            }),
            'limit_price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'required': True
            }),
        } 