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
from adminapp.models import Product,Order,Category,Brand,Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.db.models import Avg,Count
from adminapp.tasks import main_fun
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay,json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.utils import timezone

def block_check(view_func):
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated:
            customer = Customerdetails.objects.filter(user=request.user).first()

            if customer and not customer.is_active:
                logout(request)
                messages.error(request, "User is blocked. Please contact admin.")
                return redirect('login_view')

        return view_func(request, *args, **kwargs)

    return wrapper


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

    if request.method == 'POST':

        form = UserForm(request.POST)

        if form.is_valid():

            otp = otp_generation()

            # store form data in session
            request.session['register_data'] = {
                "username": form.cleaned_data['username'],
                "email": form.cleaned_data['email'],
                "password": form.cleaned_data['password1'],
                "mobile": form.cleaned_data['mobile']
            }

            request.session['otp'] = otp
            request.session['otp_created_at'] = str(timezone.now())

            email = form.cleaned_data['email']

            main_fun.delay(email, otp)

            return redirect('otp_verification')

    else:
        form = UserForm()

    return render(request, 'user_register.html', {'form': form})

def verify_otp(request):

    otp_session = request.session.get("otp")
    register_data = request.session.get("register_data")
    otp_created_at = request.session.get("otp_created_at")

    remaining_seconds = 120

    if otp_created_at:
        otp_created_at = datetime.fromisoformat(otp_created_at)
        expiry_time = otp_created_at + timedelta(minutes=2)
        remaining_time = expiry_time - timezone.now()

        if remaining_time.total_seconds() > 0:
            remaining_seconds = int(remaining_time.total_seconds())
        else:
            remaining_seconds = 0

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        if remaining_seconds <= 0:
            messages.error(request, "OTP expired. Please resend OTP.")

        elif entered_otp == otp_session:

            # create user only now
            user = User.objects.create_user(
                username=register_data["username"],
                email=register_data["email"],
                password=register_data["password"]
            )

            Customerdetails.objects.create(
                user=user,
                mobile=register_data["mobile"]
            )

            # clear session
            del request.session["otp"]
            del request.session["register_data"]
            del request.session["otp_created_at"]

            messages.success(request, "Account created successfully")

            return redirect("login_view")

        else:
            messages.error(request, "Invalid OTP")

    context = {
        "remaining_seconds": remaining_seconds
    }

    return render(request, "verify_otp.html", context)



def resend_otp(request):

    register_data = request.session.get("register_data")

    if not register_data:
        return redirect("register_user")

    new_otp = otp_generation()

    request.session["otp"] = new_otp
    request.session["otp_created_at"] = str(timezone.now())

    email = register_data["email"]

    main_fun.delay(email, new_otp)

    messages.success(request, "New OTP sent")

    return redirect("otp_verification")
@never_cache
def login_page(request):

    if request.method == 'POST':

        login_input = request.POST.get('username')
        password = request.POST.get('password')

        # check if input is email
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            username = login_input

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:

            login(request, user)

            if user.is_superuser:
                return redirect('admin_dash')
            else:
                return redirect('user_dashboard')

        else:
            messages.error(request, 'Invalid username/email or password')

    return render(request, 'home_page.html')


@block_check
@never_cache
@login_required(login_url='login_view')
def user_dashboard(request):
    if request.user.is_superuser:
        return redirect('users')
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
    # Wishlist products
    wishlist_ids = list(
        Wishlist.objects.filter(user=request.user)
        .values_list('product_id', flat=True)
    )
    categories = Category.objects.filter(is_available=True)
    products = Product.objects.select_related('brand','category').filter(
    is_available=True,
    brand__is_available=True,
    category__is_available=True)
    # ---------------- CATEGORY FILTER ----------------
    category = request.GET.get('category')

    if category:
        products = products.filter(category_id=category)

        # get brands only from products of selected category
        brands = Brand.objects.filter(
            id__in=Product.objects.filter(category_id=category)
            .values_list('brand_id', flat=True)
        ).distinct()

    else:
        brands = Brand.objects.none()  # hide brand filter when all categories
    # ---------------- BRAND FILTER ----------------
    brand = request.GET.get('brand')

    if brand:
        products = products.filter(brand_id=brand)

    # ---------------- PRICE SORT ----------------
    price = request.GET.get('price')

    if price == "low":
        products = products.order_by("price")

    elif price == "high":
        products = products.order_by("-price")

    # ---------------- SEARCH ----------------
    search = request.GET.get('search')

    if search:
        products = products.filter(name__icontains=search)

    # ---------------- RATINGS ----------------
    products = products.annotate(
    avg_rate=Avg('reviews__rating'),
    count=Count('reviews__rating', distinct=True)).distinct()

    # ---------------- PAGINATION ----------------
    paginator = Paginator(products, 8)

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
    
@block_check
def user_main_page(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
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
    products = products.annotate(
        avg_rate=Avg('reviews__rating'),count=Count('reviews__rating')
        ).order_by('-created_at')
    # ---------- PAGINATION ----------
    paginator = Paginator(products, 10)
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
@login_required
def review_fun(request,id):
    user=get_object_or_404(Customerdetails,user=request.user)
    product=get_object_or_404(Product,id=id)
    existing_review = ReviewModel.objects.filter(
        product=product,
        customer=user
    ).first()
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


@login_required
def cancel_order(request, order_id):
    if request.method == "POST":
        customer = get_object_or_404(Customerdetails, user=request.user)
        order = get_object_or_404(Order, id=order_id, user=customer)

        # Allow cancel except delivered and cancelled
        if order.status not in ['delivered', 'cancelled']:
            order.status = 'cancelled'
            order.save()

    return redirect('my_order')

# userapp/views.py
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
@login_required
def create_payment(request):

    payment_mode = request.session.get('payment_mode')
    userobj = get_object_or_404(Customerdetails, user=request.user)

    if payment_mode == 'single_item':

        data = request.session.get('single_item_data', {})

        if not data:
            return JsonResponse({"error": "Invalid single item session"}, status=400)

        total_amount = data['total']


    elif payment_mode == 'full_cart':

        cart_items = CartProduct.objects.filter(cart__user=request.user)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

    else:
        return JsonResponse({"error": "No payment mode selected"}, status=400)

    amount_in_paise = int(total_amount * 100)

    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    Payment.objects.create(
        user=userobj,
        razorpay_order_id=razorpay_order['id'],
        amount=amount_in_paise,
        status="PENDING"
    )

    request.session["razorpay_order_id"] = razorpay_order["id"]
    request.session.modified = True

    return JsonResponse({
        "order_id": razorpay_order["id"],
        "amount": amount_in_paise,
        "key": settings.RAZORPAY_KEY_ID,
        "currency": "INR"
    })


@csrf_exempt
@login_required
def verify_payment(request):

    data = json.loads(request.body)

    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_signature = data.get("razorpay_signature")

    try:

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        client.utility.verify_payment_signature(params_dict)

        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)

        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = "SUCCESS"
        payment.save()

        customer = Customerdetails.objects.get(user=request.user)

        payment_mode = request.session.get("payment_mode")

        subject = "Order Confirmation"

        # -------------------------
        # SINGLE ITEM ORDER
        # -------------------------

        if payment_mode == "single_item":

            data = request.session.get("single_item_data", {})
            cart_item_id = data.get("cart_item_id")

            cart_item = CartProduct.objects.get(
                id=cart_item_id,
                cart__user=request.user
            )

            product = cart_item.product

            order = Order.objects.create(
                user=customer,
                product=product,
                quantity=cart_item.quantity,
                price=product.price,
                total_amount=product.price * cart_item.quantity,
                status="confirmed"
            )

            # Update stock
            product.stock -= cart_item.quantity
            product.save()

            # Convert to Indian time
            order_time = timezone.localtime(order.created_at)
            formatted_time = order_time.strftime("%d %B %Y, %I:%M %p")

            message = f"""
Hello {request.user.username},

Your order has been placed successfully.

Order ID: {order.order_id}
Product: {order.product.name}
Quantity: {order.quantity}
Date & Time: {formatted_time}
Total Amount: ₹{order.total_amount}

Thank you for shopping with us.

E-commerce Team
"""

            # Remove item from cart
            CartProduct.objects.filter(
                id=cart_item_id,
                cart__user=request.user
            ).delete()

        # -------------------------
        # FULL CART ORDER
        # -------------------------

        elif payment_mode == "full_cart":

            cart_items = CartProduct.objects.filter(cart__user=request.user)

            order_details = ""
            total_amount = 0
            orders = []

            for item in cart_items:

                product = item.product

                if product.stock < item.quantity:
                    return JsonResponse({
                        "status": "failed",
                        "message": "Stock insufficient"
                    })

                order = Order.objects.create(
                    user=customer,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    total_amount=product.price * item.quantity,
                    status="confirmed"
                )

                orders.append(order)

                product.stock -= item.quantity
                product.save()

                total_amount += order.total_amount

                order_details += f"""
Product: {product.name}
Order ID: {order.order_id}
Quantity: {order.quantity}
Amount: ₹{order.total_amount}
-----------------------
"""

            # Convert IST time
            order_time = timezone.localtime(orders[0].created_at)
            formatted_time = order_time.strftime("%d %B %Y, %I:%M %p")

            message = f"""
Hello {request.user.username},

Your cart order has been placed successfully.

Order Details
-----------------------
{order_details}

Total Amount Paid: ₹{total_amount}

Date & Time: {formatted_time}

Thank you for shopping with us.

Ecommerce Team
"""

            # Clear cart
            CartProduct.objects.filter(cart__user=request.user).delete()

        # -------------------------
        # SEND EMAIL
        # -------------------------

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )

        return JsonResponse({
            "status": "success",
            "redirect_url": "/orders/"
        })

    except Exception as e:
        print(e)
        return JsonResponse({"status": "failed"})



# ───────────────────────────────────────────────
# 1. Proceed to Checkout – whole cart
# ───────────────────────────────────────────────
@login_required
def proceed_full_cart_checkout(request):

    cart_items = CartProduct.objects.filter(cart__user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('view_cart')

    request.session['payment_mode'] = 'full_cart'

    total = sum(item.product.price * item.quantity for item in cart_items)
    request.session['expected_total'] = float(total)

    return redirect('order_confirm')

# ───────────────────────────────────────────────
# 2. Buy Now – single item from cart
# ───────────────────────────────────────────────
@login_required
def buy_now_single_item(request, item_id):

    cart_item = get_object_or_404(CartProduct, id=item_id, cart__user=request.user)

    if cart_item.product.stock < cart_item.quantity:
        messages.error(request, f"Only {cart_item.product.stock} available.")
        return redirect('view_cart')

    request.session['payment_mode'] = 'single_item'

    request.session['single_item_data'] = {
        'cart_item_id': cart_item.id,
        'product_id': cart_item.product.id,
        'quantity': cart_item.quantity,
        'price': float(cart_item.product.price),
        'total': float(cart_item.product.price * cart_item.quantity),
    }

    return redirect('order_confirm')












