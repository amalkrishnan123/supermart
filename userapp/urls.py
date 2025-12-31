from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# from .forms import CustomPasswordResetForm


urlpatterns = [
    path('login/',views.login_page,name='login_view'),
    path('user_logout',views.logout_user,name='logout_view'),
    path('user_registration/',views.user_register,name='register'),
    path('user_register_page/',views.user_register,name='register_user'),
    path('logged_in_user_dash',views.user_dashboard,name='user_dashboard'),
    path('verify_otp/<int:user_id>',views.verify_otp,name='otp_verification'),
    path('password_reset',auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),name='password_reset'),
    path('password_reset_done',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
    path('password_reset_complete',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
    path('user_profile/',views.user_profile,name='profile'),
    path('user_address/',views.user_address,name='add_address'),
    path('user_edit_address/',views.edit_user_details,name='edit_address'),
    path('orders/',views.my_orders,name='my_order'),
    path('order_confirm',views.confirmation,name='order_confirm'),
    path('place-order/', views.place_order, name='place_order'),
    path('',views.user_main_page,name='main_home')
    


    

]
