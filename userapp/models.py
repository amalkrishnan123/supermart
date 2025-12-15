from django.db import models
from django.contrib.auth.models import User


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

