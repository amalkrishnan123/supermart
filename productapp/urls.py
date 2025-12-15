from .import views
from django.urls import path

urlpatterns = [
    path('cart_page',views.cart_page,name='view_cart'),
    path('addto_cart/<int:id>',views.add_to_cart,name='add_to_cart'),
    path('product_details/<int:id>', views.product_details, name='product_desc'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase_qty/<int:id>/', views.increase_qty, name='increase_qty'),
    path('decrease_qty/<int:id>/', views.decrease_qty, name='decrease_qty'),
    path('toggle_wishlist/<int:id>', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_page, name='view_wishlist'),
    
    
]
