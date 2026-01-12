from django.db import models
from django.contrib.auth.models import User
import adminapp



class CustomerAddress(models.Model):
    address=models.TextField()
    pincode=models.CharField(max_length=6)
    district=models.CharField(max_length=50)
    state=models.CharField(max_length=20)

    def __str__(self):
        return f'{self.address}{self.district}'

class Customerdetails(models.Model):
    mobile=models.CharField(max_length=10,unique=True)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    otp=models.CharField(max_length=6,null=True,blank=True)
    address=models.ForeignKey(CustomerAddress,on_delete=models.CASCADE,null=True, blank=True)
    password_length = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class ReviewModel(models.Model):
    rating=models.PositiveIntegerField(null=True, blank=True)
    review=models.TextField(null=True, blank=True)
    product=models.ForeignKey('adminapp.Product',on_delete=models.CASCADE,related_name='reviews')
    customer=models.ForeignKey('userapp.Customerdetails',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('product','customer')
    def __str__(self):
        return f'{self.review}-{self.product}-{self.customer}'



