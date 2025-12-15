from django.shortcuts import render,redirect
from .models import CartProduct,Cart,Wishlist
from adminapp.models import Product
from django.shortcuts import get_object_or_404
from django.contrib import messages


# Create your views here.
def product_details(request,id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    items = CartProduct.objects.filter(cart=cart)
    pro=CartProduct.objects.filter(product__id=id).first()
    search=request.GET.get('search')
    if search:
        product=Product.objects.filter(name__icontains=search,is_available=True)
    else:
        product=Product.objects.filter(is_available=True,id=id)
    return render(request,'product_details.html',{'product':product,'item':pro,'wishlist_ids': list(wishlist_ids)})

def cart_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartProduct.objects.filter(cart=cart)
    for item in items:
        item.total = item.product.price * item.quantity
    total_amount = sum(item.total for item in items)
    return render(request, 'cart_items.html', {'cart_items': items,'total_amount': total_amount})

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartProduct.objects.get_or_create(cart=cart,product=product)
    return redirect('product_desc',id)

def remove_from_cart(request, id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartProduct, id=id, cart=cart)
    item.delete()
    return redirect('view_cart')

def increase_qty(request, id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartProduct, id=id, cart=cart)
    item.quantity+=1
    item.save()
    return redirect('view_cart')

def decrease_qty(request, id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartProduct, id=id, cart=cart)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('view_cart')

def toggle_wishlist(request, id):
    if not request.user.is_authenticated:
        return redirect('login_view')
    product = get_object_or_404(Product, id=id)
    existing = Wishlist.objects.filter(user=request.user, product=product)
    if existing.exists():
        existing.delete()
        messages.info(request, "Removed from wishlist")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, "Added to wishlist")
    return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))

def wishlist_page(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'items': items})







