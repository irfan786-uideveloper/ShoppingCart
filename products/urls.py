from django.urls import path
from .views import *

urlpatterns = [
    path("",index,name="index"),
    path("shopping_cart",Shopping_cart,name="shopping_cart"),
    path('remove-from-cart/<int:id>/', remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:product_id>/',add_to_cart,name='add_to_cart'),
    path('register/',registerpage,name='register'),
    path('login/',loginpage,name='login'),
    path('logout/',logoutUser,name='logout'),
    path('account/',accountSettings,name="account"),
    path('checkout/',checkout_Page,name='checkout'),
    path('success/',payment_success,name='success'),
    path('orders/',user_orders,name='orders'),
    path('increase_cart_item/<int:cart_item_id>/', increment_cart_item, name='increase_cart_item'),
    path('decrease_cart_item/<int:cart_item_id>/',decrement_cart_item,name='decrement_cart_item'),
    path('admin_dashboard',admin_dashboard_view,name='admin_dashboard'),
    path('view_customer',view_customer_view,name='view_customer'),
    path('admin_view_booking_view',admin_view_booking_view,name='admin_view_booking_view')

    # path('pdf/',pdf,name='pdf'),
]
