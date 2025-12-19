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

    # Calculate total per item
    for item in items:
        item.total = item.product.price * item.quantity

    # ✅ ONLY IN-STOCK ITEMS
    in_stock_items = items.filter(product__stock__gt=0)

    # ✅ Total ONLY from in-stock items
    total_amount = sum(
        item.product.price * item.quantity
        for item in in_stock_items
    )

    # ✅ Checkout allowed if at least one in-stock item exists
    can_checkout = in_stock_items.exists()

    return render(
        request,
        'cart_items.html',
        {
            'cart_items': items,          # show all (including out-of-stock)
            'total_amount': total_amount, # price of only in-stock items
            'can_checkout': can_checkout,
        }
    )


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
    if item.quantity < item.product.stock:
        item.quantity+=1
        item.save()
    else:
        messages.warning(
            request,
            "Out of stock. You cannot add more items."
        )
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
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'items': items})


def buy_now(request, id):
    product = get_object_or_404(Product, id=id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartProduct.objects.get_or_create(
        cart=cart,
        product=product
    )
    item.total = item.product.price * item.quantity
    total_amount = item.total
    return render(request, 'buy_now.html', {
        'item': item,
        'cart_items': [item], 
        'total_amount': total_amount
    })

def increase_qty_buy_now(request, id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartProduct, id=id, cart=cart)
    if item.quantity < item.product.stock:
        item.quantity+=1
        item.save()
    else:
        messages.warning(
            request,
            "Out of stock. You cannot add more items."
        )
    return redirect('buy_now',item.product.id)

def decrease_qty_buy(request, id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartProduct, id=id, cart=cart)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('buy_now',item.product.id)


