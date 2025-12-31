from django.urls import path
from . import views


urlpatterns = [
    path('admin_dashboard/',views.admin_dashboard,name='admin_dash'),
    path('product_page/',views.admin_product_page,name='all_products'),
    path('edit_product/<int:id>',views.admin_edit_product,name='edit_product'),
    path('add_product/',views.admin_add_product,name='add_product'),
    path('delete_product/<int:id>',views. admin_delete_product,name='delete_products'),
    path('block_product/<int:id>',views.block_product,name='block_products'),
    path('unblock_product/<int:id>',views.unblock_product,name='unblock_products'),
    path('category_page/',views.admin_category_page,name='all_category'),
    path('add_category/',views.admin_add_category,name='add_category'),
    path('admin_edit_category/<int:id>',views.admin_edit_category,name='edit_category'),
    path('delete_category/<int:id>',views.admin_delete_category,name='delete_category'),
    path('block_category/<int:id>',views.block_category,name='block_category'),
    path('unblock_category/<int:id>',views.unblock_category,name='unblock_category'),
    path('brand_page/',views.admin_brand_page,name='all_brand'),
    path('admin_add_brand/',views.admin_add_brand,name='add_brand'),
    path('admin_edit_brand/<int:id>',views.admin_edit_brand,name='edit_brand'),
    path('delete_brand/<int:id>',views.admin_delete_brand,name='delete_brand'),
    path('block_brand/<int:id>',views.block_brand,name='block_brand'),
    path('unblock_brand/<int:id>',views.unblock_brand,name='unblock_brand'),
    path('block_user/<int:id>',views.admin_block_user,name='blockuser'),
    path('unblock_user/<int:id>',views.admin_unblock_user,name='unblockuser'),
    path('logout_admin/',views.admin_logout,name='logout_admin'),
    path('admin_orders/',views.admin_orders,name='admin_order_page'),
    path('admin_update_status/<int:id>/<int:pro_id>/<str:status>/',views.admin_update_status,name='admin_status_update'),
    

    
]
