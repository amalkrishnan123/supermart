from django.shortcuts import render,redirect
from .forms import Product_form,Category_form,Brand_form
from .models import Product,Category,Brand,Order
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from userapp.models import Customerdetails
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Sum,Avg,Count
from django.core.paginator import Paginator
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def admin_only(fun):
    @login_required
    def wrapper(request,*args,**kwargs):
        if not request.user.is_staff:
            return redirect('login_view')
        return fun(request,*args,**kwargs)
    return wrapper

# Create your views here.
@admin_only
@login_required
def admin_dashboard(request):

    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'latest')
    status = request.GET.get('status')

    users = Customerdetails.objects.select_related('user').exclude(user__is_superuser=True)

    # STATUS FILTER
    if status == "active":
        users = users.filter(is_active=True)

    elif status == "blocked":
        users = users.filter(is_active=False)

    # SEARCH
    if search:
        users = users.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(mobile__icontains=search)
        )

    # SORTING
    if sort == "latest":
        users = users.order_by('-id')

    elif sort == "oldest":
        users = users.order_by('id')

    elif sort == "year":
        users = users.order_by('-user__date_joined')

    elif sort == "month":
        users = users.order_by('-user__date_joined')

    # PAGINATION
    paginator = Paginator(users, 3)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    context = {
        'form': users,
        'search': search,
        'sort': sort,
        'status': status
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
@admin_only
def admin_product_page(request):
    product_list=Product.objects.all().order_by('-id')
    paginator=Paginator(product_list,6)
    page_no=request.GET.get('page')
    page=paginator.get_page(page_no)
    return render(request,'product_page.html',{'product_list':page})

@login_required
@admin_only
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
@admin_only
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
@admin_only
def admin_delete_product(request,id):
    user=get_object_or_404(Product,id=id)
    user.delete()
    return redirect('all_products')

@login_required
@admin_only
def block_product(request,id):
    product=get_object_or_404(Product,id=id)
    product.is_available=False
    product.save()
    messages.success(request,'product blocked successfully')
    return redirect('all_products')

@login_required
@admin_only
def unblock_product(request,id):
    product=get_object_or_404(Product,id=id)
    product.is_available=True
    product.save()
    messages.success(request,'product unblocked')
    return redirect('all_products')

@login_required
@admin_only
def admin_category_page(request):

    product_categories = Category.objects.all().order_by('-id')

    paginator = Paginator(product_categories, 3)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'category_page.html',
        {
            'category': page_obj
        }
    )

@login_required
@admin_only
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
@admin_only
def admin_edit_category(request,id):
    category=get_object_or_404(Category,id=id)
    if request.method=='POST':
        name=request.POST.get('name')
        if category.name!=name:
            category.name=name
        category.save() 
        return redirect('all_category')   
    return render(request,'category_page.html')

@login_required
@admin_only
def admin_delete_category(request,id):
    user=get_object_or_404(Category,id=id)
    user.delete()
    return redirect('all_category')

@login_required
@admin_only
def block_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_available=False
    category.save()
    messages.success(request,'category has been blocked')
    return redirect('all_category')

@login_required
@admin_only
def unblock_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.is_available=True
    category.save()
    messages.success(request,'category has been unblocked')
    return redirect('all_category')

@login_required
@admin_only
def admin_brand_page(request):

    category_id = request.GET.get('category')
    blocked=request.GET.get('is_available')
    brands = Brand.objects.all().order_by('-id')
    if blocked:
        brands=brands.filter(is_available=False)

    if category_id:
        brands = brands.filter(
            brands__category_id=category_id
        ).distinct()

    paginator = Paginator(brands, 5)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_available=True)

    return render(
        request,
        'brand_page.html',
        {
            'brand': page_obj,
            'categories': categories,
            'selected_category': category_id
        }
    )

@login_required
@admin_only
def admin_add_brand(request):
    if request.method=='POST':
        brand=Brand_form(request.POST)
        if brand.is_valid():
            brand.save()
            return redirect('all_brand')
    else:
        brand=Brand_form()
    return render(request,'admin_add_brand.html',{'form':brand})

@login_required
@admin_only
def admin_edit_brand(request,id):
    brand=get_object_or_404(Brand,id=id)
    if request.method=='POST':
        name=request.POST.get('name')
        if brand.name!=name:
            brand.name=name
        brand.save() 
        return redirect('all_brand')   
    return render(request,'brand_page.html')

@login_required
@admin_only
def admin_delete_brand(request,id):
    user=get_object_or_404(Brand,id=id)
    user.delete()
    return redirect('all_brand')

@login_required
@admin_only
def block_brand(request,id):
    brand=get_object_or_404(Brand,id=id)
    brand.is_available=False
    brand.save()
    messages.success(request,'brand has been blocked')
    return redirect('all_brand')

@login_required
@admin_only
def unblock_brand(request,id):
    brand=get_object_or_404(Brand,id=id)
    brand.is_available=True
    brand.save()
    messages.success(request,'brand has been unblocked')
    return redirect('all_brand')

@login_required
@admin_only
def admin_logout(request):
    logout(request)
    return redirect('login_view')

@login_required
@admin_only
def admin_block_user(request,id):
    block=get_object_or_404(Customerdetails,id=id)
    block.is_active=False
    block.save()
    return redirect('users')
    
@login_required
@admin_only
def admin_unblock_user(request,id):
    block=get_object_or_404(Customerdetails,id=id)
    block.is_active=True
    block.save()
    return redirect('users')

@login_required
@admin_only
def admin_orders(request):

    orders = Order.objects.select_related(
        'user__user', 'product'
    ).all().order_by('-id')

    status = request.GET.get('status')

    if status == "pending":
        orders = orders.filter(status="pending")

    elif status == "confirmed":
        orders = orders.filter(status="confirmed")

    elif status == "shipped":
        orders = orders.filter(status="shipped")

    elif status == "delivered":
        orders = orders.filter(status="delivered")

    elif status == "cancelled":
        orders = orders.filter(status="cancelled")

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_order_page.html', {
        'user': page_obj,
        'status': status
    })

@login_required
@admin_only
def admin_update_status(request, order_id, status):

    order = get_object_or_404(Order, id=order_id)

    order.status = status
    order.save()

    order_time = timezone.localtime(order.created_at)
    formatted_time = order_time.strftime("%d %B %Y, %I:%M %p")

    user_email = order.user.user.email
    username = order.user.user.username

    # -------------------------
    # SHIPPED EMAIL
    # -------------------------
    if status == "shipped":

        subject = "Your Order Has Been Shipped"

        message = f"""
Hello {username},

Good news! Your order has been shipped.

Order ID: {order.order_id}
Amount:{order.total_amount}
Product: {order.product.name}
Quantity: {order.quantity}
Order Date: {formatted_time}

Your package is on the way 🚚

Thank you for shopping with us.

E-commerce Team
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )

    # -------------------------
    # DELIVERED EMAIL
    # -------------------------
    elif status == "delivered":

        subject = "Your Order Has Been Delivered"

        message = f"""
Hello {username},

Your order has been successfully delivered.

Order ID: {order.order_id}
Product: {order.product.name}
Quantity: {order.quantity}
Amount:{order.total_amount}

We hope you enjoy your purchase!

Thank you for shopping with us.

E-commerce Team
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )

    messages.success(request, 'Status updated')
    return redirect('admin_order_page')


def statistics(request):

    # -----------------------
    # Dashboard Cards
    # -----------------------
    totalusers = Customerdetails.objects.exclude(user__is_superuser=True).count()
    products = Product.objects.count()
    total_orders = Order.objects.count()

    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    active_user = Customerdetails.objects.filter(
        is_active=True
    ).exclude(user__is_superuser=True).count()

    blocked_users = Customerdetails.objects.filter(
        is_active=False
    ).exclude(user__is_superuser=True).count()

    pending_orders = Order.objects.filter(
        status__in=['confirmed', 'shipped']
    ).count()

    delivered_orders = Order.objects.filter(status='delivered').count()


    # -----------------------
    # Date Filter
    # -----------------------
    filter_type = request.GET.get('filter', '30days')
    today = timezone.now()

    if filter_type == "7days":
        start_date = today - timedelta(days=7)
        date_trunc = TruncDay
        label_format = "%d %b"
    elif filter_type == "30days":
        start_date = today - timedelta(days=30)
        date_trunc = TruncDay
        label_format = "%d %b"
    else:
        start_date = today - timedelta(days=365)
        date_trunc = TruncMonth
        label_format = "%b"

    filtered_orders = Order.objects.filter(created_at__gte=start_date)


    # -----------------------
    # Sales Overview (Line Chart)
    # -----------------------
    sales_data = filtered_orders.filter(status='delivered').annotate(
        period=date_trunc('created_at')
    ).values('period').annotate(
        revenue=Sum('total_amount')
    ).order_by('period')

    sale_labels = [i['period'].strftime(label_format) for i in sales_data]
    sale_values = [float(i['revenue']) if i['revenue'] else 0 for i in sales_data]


    # -----------------------
    # Order Status Distribution (Pie Chart)
    # -----------------------
    status_data = filtered_orders.values('status').annotate(
        count=Count('id')
    )

    status_labels = [i['status'] for i in status_data]
    status_counts = [i['count'] for i in status_data]


    # -----------------------
    # Top Selling Products (Bar Chart)
    # -----------------------
    top_products = filtered_orders.filter(status='delivered').values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    product_labels = [i['product__name'] for i in top_products]
    product_sales = [i['total_sold'] for i in top_products]


    # -----------------------
    # Context
    # -----------------------
    context = {
        'totalusers': totalusers,
        'products': products,
        'orders': total_orders,
        'revenue': total_revenue,
        'active_user': active_user,
        'blocked_users': blocked_users,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,

        # Charts
        'sale_labels': sale_labels,
        'sale_values': sale_values,

        'status_labels': status_labels,
        'status_counts': status_counts,

        'product_labels': product_labels,
        'product_sales': product_sales,

        'filter_type': filter_type
    }

    return render(request, 'statistics_page.html', context)



def download_sales_report(request):

    filter_type = request.GET.get("filter", "30days")

    today = timezone.now()

    if filter_type == "7days":
        start_date = today - timedelta(days=7)
        report_title = "Last 7 Days Sales Report"

    elif filter_type == "30days":
        start_date = today - timedelta(days=30)
        report_title = "Last 30 Days Sales Report"

    else:
        start_date = today - timedelta(days=365)
        report_title = "Yearly Sales Report"


    orders = Order.objects.filter(
        status="delivered",
        created_at__gte=start_date
    )

    total_orders = orders.count()
    total_revenue = orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0


    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # Company Title
    elements.append(Paragraph("My E-Commerce Store", styles["Title"]))
    elements.append(Spacer(1,10))

    # Report Title
    elements.append(Paragraph(report_title, styles["Heading2"]))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles["Normal"]
    ))

    elements.append(Spacer(1,20))


    # Summary
    elements.append(Paragraph(f"Total Orders: {total_orders}", styles["Normal"]))
    elements.append(Paragraph(f"Total Revenue: ₹{total_revenue}", styles["Normal"]))

    elements.append(Spacer(1,20))


    # Table Header
    data = [
        ["Order ID", "Date", "User", "Email", "Product", "Qty", "Amount"]
    ]


    for order in orders:
        data.append([
            order.order_id,
            order.created_at.strftime("%d-%m-%Y"),
            order.user.user.username,
            order.user.user.email,
            order.product.name,
            order.quantity,
            order.total_amount
        ])


    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)

    pdf.build(elements)

    return response
    

