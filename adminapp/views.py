from django.shortcuts import render,redirect
from .forms import Product_form,Category_form
from .models import Product,Category
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from userapp.models import Customerdetails
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def admin_dashboard(request):
    form=Customerdetails.objects.all()
    return render(request,'admin_dashboard.html',{'form':form})

@login_required
def admin_product_page(request):
    product_list=Product.objects.all().order_by('-id')
    paginator=Paginator(product_list,3)
    page_no=request.GET.get('page')
    page=paginator.get_page(page_no)
    return render(request,'product_page.html',{'product_list':page})

@login_required
def admin_add_product(request):
    if request.method=='POST':
        product=Product_form(request.POST,request.FILES)
        if product.is_valid():
            product.save()
            return redirect('all_products')
    else:
        product=Product_form()        
    return render(request,'admin_add_product.html',{'form':product})

@login_required
def admin_edit_product(request,id):
    edit=Product.objects.get(id=id)
    if request.method=='POST':
        edit_product=Product_form(request.POST,request.FILES,instance=edit)
        if edit_product.is_valid():
            edit_product.save()
            return redirect('all_products')
    else:
        edit_product=Product_form(instance=edit)
    return render(request,'admin_edit_product.html',{'form':edit_product})

@login_required
def admin_delete_product(request,id):
    user=get_object_or_404(Product,id=id)
    user.delete()
    return redirect('all_products')

@login_required
def admin_category_page(request):
    product_categories=Category.objects.all()
    return render(request,'category_page.html',{'category':product_categories})

@login_required
def admin_add_category(request):
    if request.method=='POST':
        category=Category_form(request.POST)
        if category.is_valid():
            category.save()
            return redirect('all_category')
    else:
        category=Category_form()
    return render(request,'admin_add_category.html',{'form':category})

@login_required
def admin_edit_category(request,id):
    category=get_object_or_404(Category,id=id)
    if request.method=='POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        if category.name!=name:
            category.name=name
        if category.description!=description:
            category.description=description
        category.save() 
        return redirect('all_category')   
    return render(request,'category_page.html')

@login_required
def block_product(request,id):
    product=get_object_or_404(Product,id=id)
    product.is_available=False
    product.save()
    messages.success(request,'product blocked successfully')
    return redirect('all_products')

@login_required
def unblock_product(request,id):
    product=get_object_or_404(Product,id=id)
    product.is_available=True
    product.save()
    messages.success(request,'product unblocked')
    return redirect('all_products')

@login_required
def admin_logout(request):
    logout(request)
    return redirect('login_view')

@login_required
def admin_block_user(request,id):
    block=get_object_or_404(Customerdetails,id=id)
    block.is_active=False
    block.save()
    return redirect('admin_dash')
    
@login_required
def admin_unblock_user(request,id):
    block=get_object_or_404(Customerdetails,id=id)
    block.is_active=True
    block.save()
    return redirect('admin_dash')

@login_required
def admin_delete_category(request,id):
    user=get_object_or_404(Category,id=id)
    user.delete()
    return redirect('all_category')

def block_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_available=False
    category.save()
    messages.success(request,'category has been blocked')
    return redirect('all_category')

def unblock_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_available=True
    category.save()
    messages.success(request,'category has been unblocked')
    return redirect('all_category')


    

