from django.shortcuts import render,redirect
from .models import CartProduct,Cart,Wishlist
from adminapp.models import Product,Category,Brand
from django.shortcuts import get_object_or_404
from django.contrib import messages


# Create your views here.
def product_details(request, id):
    product = Product.objects.filter(id=id, is_available=True).first()
    cart_item = None
    wishlist_ids = []
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )
        cart_item = CartProduct.objects.filter(
            cart=cart,
            product_id=id
        ).first()

    return render(
        request,
        'product_details.html',
        {
            'product': product,
            'item': cart_item,
            'wishlist_ids': wishlist_ids,
        }
    )


def cart_page(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    cart = Cart.objects.get(user=request.user)
    cart_items = CartProduct.objects.filter(
        cart=cart
    ).select_related(
        'product', 'product__category', 'product__brand'
    )

    # SEARCH (cart only)
    search = request.GET.get('search')
    if search:
        cart_items = cart_items.filter(
            product__name__icontains=search
        )

    # CATEGORY FILTER
    category = request.GET.get('category')
    if category:
        cart_items = cart_items.filter(
            product__category__id=category
        )

    # BRAND FILTER
    brand = request.GET.get('brand')
    if brand:
        cart_items = cart_items.filter(
            product__brand__id=brand
        )

    # PRICE FILTER
    price = request.GET.get('price')
    if price == '1':
        cart_items = cart_items.filter(product__price__gte=500, product__price__lte=1500)
    elif price == '2':
        cart_items = cart_items.filter(product__price__gte=1500, product__price__lte=2500)
    elif price == '3':
        cart_items = cart_items.filter(product__price__gte=2500, product__price__lte=3500)
    elif price == '4':
        cart_items = cart_items.filter(product__price__gt=3500)

    total_amount = sum(item.total for item in cart_items)
    can_checkout = cart_items.filter(product__stock__gt=0).exists()

    return render(request, 'cart_items.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'can_checkout': can_checkout,
        'cat': Category.objects.all(),
        'brand': Brand.objects.all(),
    })


def add_to_cart(request, id):
    if not request.user.is_authenticated:
        return redirect('login_view')
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartProduct.objects.get_or_create(cart=cart,product=product)
    return redirect('product_desc',id)

def remove_from_cart(request, id):
    if not request.user.is_authenticated:
        return redirect('login_view')
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
    # Base queryset: ONLY wishlist items of logged-in user
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related(
        'product', 'product__category', 'product__brand'
    )

    # SEARCH (wishlist only)
    search = request.GET.get('search')
    if search:
        items = items.filter(product__name__icontains=search)

    # CATEGORY FILTER
    category = request.GET.get('category')
    if category:
        items = items.filter(product__category__id=category)

    # BRAND FILTER
    brand = request.GET.get('brand')
    if brand:
        items = items.filter(product__brand__id=brand)

    # PRICE FILTER
    price = request.GET.get('price')
    if price == '1':
        items = items.filter(product__price__gte=500, product__price__lte=1500)
    elif price == '2':
        items = items.filter(product__price__gte=1500, product__price__lte=2500)
    elif price == '3':
        items = items.filter(product__price__gte=2500, product__price__lte=3500)
    elif price == '4':
        items = items.filter(product__price__gt=3500)

    return render(
        request,
        'wishlist.html',
        {
            'items': items,
            'cat': Category.objects.all(),
            'brand': Brand.objects.all(),
        }
    )


def buy_now(request, id):
    if not request.user.is_authenticated:
        return redirect('login_view')
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


