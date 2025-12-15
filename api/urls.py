from .import views
from django.urls import path
from. views import Category_list,Category_alter,Product_view,Product_alter

urlpatterns = [
    path('api_category/',views.category_api,name='category'),
    path('api_product/',views.product_api,name='product'),
    path("class-category/", Category_list.as_view(), name="category_list_create"),
    path('class-categories/<int:pk>/', Category_alter.as_view(),name='category_alter'),
    path('product-view-create/',Product_view.as_view(),name='product_side'),
    path('product-alter/<int:pk>/',Product_alter.as_view(),name='product_alter'),
]
