from django.db import models
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=100) 
    is_available=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=50)
    price=models.IntegerField(null=False)
    image=models.ImageField(upload_to='product_images',null=False) 
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='categories')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
   
