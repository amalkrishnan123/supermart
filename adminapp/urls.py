from django.urls import path
from . import views


urlpatterns = [
    path('admin_dashboard/',views.admin_dashboard,name='admin_dash'),
    path('product_page/',views.admin_product_page,name='all_products'),
    path('add_product/',views.admin_add_product,name='add_product'),
    path('category_page/',views.admin_category_page,name='all_category'),
    path('add_category/',views.admin_add_category,name='add_category'),
    path('admin_edit_category/<int:id>',views.admin_edit_category,name='edit_category'),
    path('edit_product/<int:id>',views.admin_edit_product,name='edit_product'),
    path('delete_product/<int:id>',views. admin_delete_product,name='delete_products'),
    path('block_product/<int:id>',views.block_product,name='block_products'),
    path('unblock_product/<int:id>',views.unblock_product,name='unblock_products'),
    path('logout_admin/',views.admin_logout,name='logout_admin'),
    path('block_user/<int:id>',views.admin_block_user,name='blockuser'),
    path('unblock_user/<int:id>',views.admin_unblock_user,name='unblockuser'),
    path('delete_category/<int:id>',views.admin_delete_category,name='delete_category'),
    path('block_category/<int:id>',views.block_category,name='block_category'),
    path('unblock_category/<int:id>',views.unblock_category,name='unblock_category'),

    
]
