from adminapp.models import Category,Product
from rest_framework import serializers

class Category_serial(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'
        

class Product_serial(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'
        
