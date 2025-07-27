from django import forms
from django.core.validators import MinValueValidator
from .models import Product, StockTransaction, StockDetail


class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'description', 'unit']
        widgets = {
            'product_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter product description'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PCS, KG, LTR'}),
        }
    
    def clean_product_id(self):
        product_id = self.cleaned_data['product_id']
        if not product_id:
            raise forms.ValidationError("Product ID is required.")
        return product_id.upper()
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError("Product name is required.")
        return name.strip()


class StockTransactionForm(forms.ModelForm):
    """Form for creating stock transactions"""
    
    class Meta:
        model = StockTransaction
        fields = ['transaction_type', 'reference_no', 'notes', 'transaction_date']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'reference_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reference number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter transaction notes'}),
            'transaction_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default transaction date to current time
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['transaction_date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')


class StockDetailForm(forms.ModelForm):
    """Form for individual stock detail items"""
    
    class Meta:
        model = StockDetail
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity
    
    def clean_unit_price(self):
        unit_price = self.cleaned_data['unit_price']
        if unit_price < 0:
            raise forms.ValidationError("Unit price cannot be negative.")
        return unit_price


class StockDetailFormSet(forms.BaseFormSet):
    """Formset for multiple stock detail items"""
    
    def clean(self):
        super().clean()
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) for form in self.forms):
            raise forms.ValidationError("At least one item is required.")
        
        # Check for duplicate products
        products = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                product = form.cleaned_data.get('product')
                if product in products:
                    raise forms.ValidationError("Duplicate products are not allowed.")
                products.append(product)


# Create formset for stock details
StockDetailFormSet = forms.formset_factory(
    StockDetailForm,
    formset=StockDetailFormSet,
    extra=1,
    can_delete=True
) 