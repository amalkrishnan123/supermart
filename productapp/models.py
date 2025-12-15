from django.db import models

from adminapp.models import Product
from django.contrib.auth.models import User

class Cart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    total=models.DecimalField(max_digits=5,decimal_places=2,default=0)

    def __str__(self):
        return f"{self.user.username}"

class CartProduct(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cart.user.username}-{self.product.name}"
    
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)



