from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.db import models
from django.contrib import messages
from .forms import CreateUserForm,CustomerForm,OrderForm
from django.contrib.auth.models import Group
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate
from django.conf import settings
from django.forms import inlineformset_factory
import razorpay

from django.http import HttpResponseRedirect
# Create your views here.
def index(request):
    products=Product.objects.all()
    categories=Category.objects.all()
    categoryID=request.GET.get('category')
    if categoryID:
        products=Product.get_all_products_by_categoryid(categoryID)
    else:
        products=Product.get_all_products()
    context={'products':products,'categories':categories}
    return render(request,"accounts/index.html",context)


#Orders Page
def user_orders(request,):
    orders=Order.objects.filter(user=request.user)
    order_count=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context={'orders':orders,'delivered':delivered,'pending':pending,
             'order_count':order_count}
    return render(request,'accounts/orders.html',context)


#--------------Admin Functionalities Start----------------#
@admin_only
def admin_dashboard_view(request):
    customercount=Customer.objects.all().count()
    productcount=Product.objects.all().count()
    ordercount=Order.objects.all().count()
    orders=Order.objects.all()
    customers=Customer.objects.all()
    ordered_products=[]
    ordered_bys=[]
    user=request.user
    ordered_productd=0
    customer_id=0
    for order in orders:
        for product in order.product.all():
            ordered_productd+=product.id
        for customer in customers:
            customer_id+=customer.id
        # print(ordered_productd)
        ordered_product=Product.objects.all().filter(id=ordered_productd)
        ordered_by=Customer.objects.all().filter(id=customer_id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    context={'total_orders':ordercount,'Total_customers':customercount,
             'productcount':productcount,'data':zip(ordered_products,ordered_bys,orders)}
    return render(request,'accounts/admin_dashboard.html',context)

# admin view customer table
def view_customer_view(request):
    customers=Customer.objects.all()
    context={'customers':customers}
    return render(request,'accounts/view_customer.html',context)

def admin_view_booking_view(request):
    orders=Order.objects.all()
    customers=Customer.objects.all()
    ordered_products=[]
    ordered_bys=[]
    user=request.user
    ordered_productd=0
    customer_id=0
    for order in orders:
        for product in order.product.all():
            ordered_productd+=product.id
        for customer in customers:
            customer_id+=customer.id
        # print(ordered_productd)
        ordered_product=Product.objects.all().filter(id=ordered_productd)
        ordered_by=Customer.objects.all().filter(id=customer_id)
        print(ordered_by)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'accounts/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})

#--------------Admin Functionalities Ends----------------#

#--------------Cart Functionalities Start----------------#

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product=Product.objects.get(id=product_id)
    user=request.user
    cart ,_=Cart.objects.get_or_create(user=user)
    cart_items=CartItems.objects.create(cart=cart,product=product)
    cart_items.save()
    return redirect('index')

@login_required(login_url='login')
def Shopping_cart(request):
    # customer=Customer.objects.get(id=id)
    products=Product.objects.all()
    cart,_=Cart.objects.get_or_create(user=request.user)
    cart_items=CartItems.objects.filter(cart=cart)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    context={'products':products,'cart_items':cart_items,
             "total_price": total_price}
    return render(request,"accounts/Shopping_Cart.html",context)

def increment_cart_item(request,cart_item_id):
    cart_item=get_object_or_404(CartItems, id=cart_item_id)
    cart_item.quantity+=1
    print(cart_item)
    cart_item.save()
    return redirect('shopping_cart')

def decrement_cart_item(request, cart_item_id):
    cart_item=get_object_or_404(CartItems, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('shopping_cart')

def remove_from_cart(request,id):
    cart_item=CartItems.objects.get(id=id)
    cart_item.delete()
    return redirect('shopping_cart')

#--------------Cart Functionalities End----------------#

#Register and Login
@unauthenticated_user
def registerpage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form=CreateUserForm()
        if request.method=='POST':
            form=CreateUserForm(request.POST)
            if form.is_valid():
                user=form.save()
                username=form.cleaned_data.get('username')
                group=Group.objects.get(name='customer')
                user.groups.add(group)
                Customer.objects.create(user=user,name=user.username,email=user.email)
                messages.success(request,'User Successfully created for '+username)
                return redirect('register')

    context={'form':form}
    return render(request,'accounts/register.html',context)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



@unauthenticated_user
def loginpage(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                # User is an admin, redirect to admin login page
                return redirect('admin_dashboard')
            else:
                # User is a regular user, redirect to dashboard
                return redirect('/')
        else:
            messages.error(request,"Username or password error")
            return redirect('login')
    return render(request,'accounts/login.html')

def logoutUser(request):
    logout(request)
    return redirect('index')

# @login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    if request.method=='POST':
        form=CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()
    context={'form':form}
    return render(request,'accounts/account_settings.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def checkout_Page(request):
    razor_pay_key_id="rzp_test_6uUIvIpmLGcMfk"
    key_secret="6HgQkTbgSUxU9kNAU5SVpOSD"
    cart,_=Cart.objects.get_or_create(user=request.user)
    cart_items=CartItems.objects.filter(cart=cart)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    amount=(total_price*100)
    client=razorpay.Client(auth=(razor_pay_key_id,key_secret))
    payment=client.order.create({'amount':amount,'currency':'INR','payment_capture':1})
    user=request.user
    customer=Customer.objects.filter(user=user)
    context={'customer':customer,'payment':payment,'cart_items':cart_items,'total_price':total_price}
    print('******Payment Details********')
    print(payment)
    print('**************')
    return render(request,'accounts/checkout.html',context)


def payment_success(request):
    if request.method=='POST':
        print("Payment Successfully Done")
    cart = Cart.objects.get(user=request.user)
    cart_items=CartItems.objects.filter(cart=cart)
    total_amount = sum(item.product.price * item.quantity for item in cart_items.all())
    print(cart)
    print(total_amount)
        # Create an order
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status="Pending"
    )
    # Add products to the order
    order.product.set([item.product for item in cart_items.all()])
    #Clear the user's cart
    cart.delete()
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    slr = seller.objects.all()
    context={'slr':slr,'cart_items':cart_items,'total_price':total_price}
    return render(request,'accounts/pdf.html',context)

# def pdf(request):
#     slr = seller.objects.all()
#     return render(request,'accounts/pdf.html',{'seller':slr})