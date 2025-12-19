from django.forms import ModelForm
from .models import Category,Product,Brand
class Category_form(ModelForm):
    class Meta:
        model=Category
        fields='__all__'

class Product_form(ModelForm):
    class Meta:
        model=Product
        fields='__all__'

class Brand_form(ModelForm):
    class Meta:
        model=Brand
        fields='__all__'
    
