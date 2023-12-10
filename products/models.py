from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.

class Customer(models.Model):
    user=models.OneToOneField(User,blank=True,null=True,on_delete=models.CASCADE,related_name='customer')
    name=models.CharField(max_length=200,null=True)
    phone=models.CharField(max_length=200,null=True)
    email=models.EmailField(max_length=200,null=True)
    profile_pic=models.ImageField(default="profilePic1.png",null=True,blank=True)

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name=models.CharField(max_length=30)
    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name=models.CharField(max_length=50)
    price=models.IntegerField(default=0)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,default=1)
    description=models.CharField(max_length=100,null=True,blank=True,default='')
    image=models.ImageField(upload_to='products')


    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_all_products():
        return Product.objects.all

    @staticmethod
    def get_products_by_id(product_id):
        return Product.objects.filter(id=product_id)

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products()



class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cart')
    # quantity = models.IntegerField(default=1)

class CartItems(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_items')
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True,related_name='product')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product}"
    # @staticmethod
    # def calculate_total_price_for_product(self, product):
    #     return product.price * self.product.filter(id=product.id).count()

class Order(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class seller(models.Model):
    name = models.CharField(max_length=50,default="SHAIK IRFAN")
    address = models.CharField(max_length=150,default="Hitech City, Hyderabad")
    phone = models.IntegerField(default='+91 8686927216')
    date = models.DateField(default=datetime.datetime.today)