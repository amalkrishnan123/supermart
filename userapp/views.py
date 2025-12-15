from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . forms import UserForm
from .models import Customerdetails,CustomerAddress
from productapp.models import Wishlist
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from adminapp.models import Product
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache


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
            subject='verification for supermarket'
            message=f'welcome to online supermarket..please verify the otp is {otp}'
            email=form.cleaned_data['email']
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
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
    # if request.user.is_authenticated:
    #     return redirect('user_dashboard')
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
@login_required
def user_dashboard(request):
    cust=Customerdetails.objects.filter(user=request.user).first()
    wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    if cust is None:
        cust = Customerdetails.objects.create(
            user=request.user,
            mobile="",
            otp=None,
            is_active=True
        )
    if cust.is_active==False:
        return redirect('login_view')
    search=request.GET.get('search')
    if search:
        product=Product.objects.filter(name__icontains=search,is_available=True)
        paginator=Paginator(product,6)
        page_no=request.GET.get('page')
        page=paginator.get_page(page_no)
    else:
        product=Product.objects.filter(is_available=True).order_by('-created_at')
        paginator=Paginator(product,6)
        page_no=request.GET.get('page')
        page=paginator.get_page(page_no)
    return render(request,'user_dashboard.html',{'product':page,'wishlist_ids':list(wishlist_ids)})

@never_cache
def logout_user(request):
    logout(request)
    return redirect('login_view')

def user_address(request):
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




