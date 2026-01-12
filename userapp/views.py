from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . forms import UserForm
from .models import Customerdetails,CustomerAddress,ReviewModel
from productapp.models import Wishlist,CartProduct
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from adminapp.models import Product,Order,Category,Brand
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.db.models import Q
from adminapp.tasks import main_fun

# Create your views here.
def otp_generation():
    otp=random.randint(100000,999999)
    return str(otp)

@never_cache
@login_required
def user_profile(request):
    dots = "•" * request.user.customerdetails.password_length
    profile=Customerdetails.objects.get(user=request.user)
    print(profile)
    return render(request,'user_profile.html',{'profile':profile,'dots':dots})

@never_cache
def user_register(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password1')
            user=form.save()
            otp=otp_generation()
            cust=Customerdetails.objects.create(user=user,mobile=form.cleaned_data['mobile'],otp=otp,password_length=len(raw_password))
            email=form.cleaned_data['email']
            print('hii',email,otp)
            main_fun.delay(email,otp)
            return redirect('otp_verification',user_id=cust.user.id)   
    else:
        form=UserForm()
    return render(request,'user_register.html',{'form':form})

def verify_otp(request,user_id):
    if request.method=='POST':
        customer=get_object_or_404(Customerdetails,user__id=user_id)
        otp=request.POST.get('otp1')
        if otp==customer.otp:
            customer.otp=None
            customer.save()
            messages.success(request,'your account have been created successfully')    
            return redirect('user_dashboard')
        else:
            messages.error(request,'invalid otp')
            return redirect('register_user')
        
    return render(request,'verify_otp.html')

@never_cache
def login_page(request):
    if request.method=='POST':
        name=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=name,password=password)
        if user is not None and user.is_active==True:
            login(request,user)
            if user.is_superuser:
                return redirect('admin_dash')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request,'invalid username or password')
    return render(request,'home_page.html')

@never_cache
@login_required(login_url='login_view')
def user_dashboard(request):

    cust, created = Customerdetails.objects.get_or_create(
        user=request.user,
        defaults={
            'mobile': '',
            'otp': None,
            'is_active': True
        }
    )

    if not cust.is_active:
        return redirect('login_view')

    wishlist_ids = list(
        Wishlist.objects.filter(user=request.user)
        .values_list('product_id', flat=True)
    )

    categories = Category.objects.all()
    brands = Brand.objects.all()

    products = Product.objects.filter(is_available=True)

    # -------- FILTERS (CHAINED) --------
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__id=brand)

    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)

    price = request.GET.get('price')
    if price == '1':
        products = products.filter(price__gte=500, price__lte=1500)
    elif price == '2':
        products = products.filter(price__gte=1500, price__lte=2500)
    elif price == '3':
        products = products.filter(price__gte=2500, price__lte=3500)
    elif price == '4':
        products = products.filter(price__gt=3500)

    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)

    products = products.order_by('-created_at')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'user_dashboard.html',
        {
            'product': page,
            'wishlist_ids': wishlist_ids,
            'cat': categories,
            'brand': brands,
        }
    )

@never_cache
def logout_user(request):
    logout(request)
    return redirect('user_dashboard')

def user_address(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    if request.user.is_authenticated:
        if request.method=='POST':
            address=request.POST.get('address')
            pincode=request.POST.get('pincode')
            district=request.POST.get('district')
            state=request.POST.get('state')
            user=CustomerAddress.objects.create(address=address,pincode=pincode,district=district,state=state)
            customer=Customerdetails.objects.get(user=request.user)
            customer.address=user
            customer.save()
            return redirect('profile')
        
@never_cache
@login_required        
def edit_user_details(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    customer=Customerdetails.objects.get(user=request.user)
    address=customer.address
    user=request.user
    if request.method=='POST':
        user.username=request.POST.get('username')
        user.email=request.POST.get('email')
        new_password=request.POST.get('password')
        if new_password:
            user.set_password(new_password)
            customer.password_length = len(new_password)
            customer.save()
        user.save()
        update_session_auth_hash(request, user)
        customer.mobile = request.POST.get('mobile')
        customer.save()
        if address is None:
            address = CustomerAddress.objects.create(
                address=request.POST.get('address'),
                pincode=request.POST.get('pincode'),
                district=request.POST.get('district'),
                state=request.POST.get('state')
            )
            customer.address = address
            customer.save()
        else:
            address.address = request.POST.get('address')
            address.pincode = request.POST.get('pincode')
            address.district = request.POST.get('district')
            address.state = request.POST.get('state')
            address.save()
        return redirect('profile')
    return render(request,'edit_address.html',{'address':address,'customer':customer})

@login_required
def my_orders(request):
    customer = get_object_or_404(Customerdetails, user=request.user)
    orders = Order.objects.filter(user=customer).select_related('product', 'product__category', 'product__brand').order_by('-created_at')
    # SEARCH (ordered product name)
    search = request.GET.get('search')
    if search:
        orders = orders.filter(product__name__icontains=search)
    # CATEGORY FILTER
    category = request.GET.get('category')
    if category:
        orders = orders.filter(product__category__id=category)
    # BRAND FILTER
    brand = request.GET.get('brand')
    if brand:
        orders = orders.filter(product__brand__id=brand)
    # STATUS FILTER
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    return render(request,'my_orders.html',
        {
            'orders': orders,
            'cat': Category.objects.all(),
            'brand': Brand.objects.all(),
        })
        
@login_required
def confirmation(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    cart_items = CartProduct.objects.filter(cart__user=request.user)
    details=get_object_or_404(Customerdetails,user=request.user)
    return render(request,'order_confirmation.html',{'details':details})

#this is for product purchase from cart side
@login_required
def place_order(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    if request.method == "POST":
        customer = get_object_or_404(Customerdetails, user=request.user)
        cart_items = CartProduct.objects.filter(cart__user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')
        for item in cart_items:
            Order.objects.create(
                user=customer,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total_amount=item.product.price * item.quantity,
                status='pending')
            item.product.stock-=item.quantity
            item.product.save()
        # clear cart after placing order
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('my_order')
    
def user_main_page(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.filter(is_available=True)
    # ---------- FILTERS ----------
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__id=brand)
    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)
    price = request.GET.get('price')
    if price == '1':
        products = products.filter(price__gte=500, price__lte=1500)
    elif price == '2':
        products = products.filter(price__gte=1500, price__lte=2500)
    elif price == '3':
        products = products.filter(price__gte=2500, price__lte=3500)
    elif price == '4':
        products = products.filter(price__gt=3500)
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    # ---------- ORDER ----------
    products = products.order_by('-created_at')
    # ---------- PAGINATION ----------
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # ------- WISHLIST ----------
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('product_id', flat=True))
    return render(request,
        'user_main_home.html',
        {
            'product': page,
            'cat': categories,
            'brand': brands,
            'wishlist_ids': wishlist_ids,
        }
    )
    
def review_fun(request,id):
    user=get_object_or_404(Customerdetails,user=request.user)
    product=get_object_or_404(Product,id=id)
    existing_review = ReviewModel.objects.get(
        product=product,
        customer=user
    )
    if request.method=='POST':
        rating=request.POST.get('rating')
        review=request.POST.get('review')
        ReviewModel.objects.update_or_create(
            product=product,
            customer=user,
            defaults={
                'rating': rating if rating else None,
                'review': review if review else ''
            }
        )
        return redirect('my_order')
    return render(request,'review.html',{'product':product,'existing_review':existing_review})





