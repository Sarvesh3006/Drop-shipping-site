# myapp/forms.py
from django import forms

class TextBoxForm(forms.Form):
    text_input = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Whats in your mind!!!'}))
class AddNumbersForm(forms.Form):
    num1 = forms.DecimalField(label='Number 1')
    num2 = forms.DecimalField(label='Number 2')


class BuyButton(forms.Form):
    quantity = forms.DecimalField(label='quantity')


class DashboardFilter(forms.Form):
    from_date=forms.DateField(label='from_date')
    to_date=forms.DateField(label='to_date')
    to_date=forms.DateField(label='to_date')