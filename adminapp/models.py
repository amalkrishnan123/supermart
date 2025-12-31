from django.db import models
from django.utils import timezone
from userapp.models import Customerdetails
import uuid

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=100) 
    is_available=models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name=models.CharField(max_length=100)
    is_available=models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=100,null=False) 
    price=models.IntegerField(null=False)
    image=models.ImageField(upload_to='product_images',null=False) 
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='categories')
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE,related_name='brands')
    created_at=models.DateTimeField(auto_now_add=True)
    stock=models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.name
   
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Customerdetails, on_delete=models.CASCADE, related_name='orders')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    order_id=models.CharField(max_length=8,unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Order #{self.id} - {self.user.user.username}"