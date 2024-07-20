
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F

class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.CharField(max_length=50)
    stores_allowed = models.IntegerField()

    def __str__(self):
        return f'{self.user.username} - {self.tier}'



class Store(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='store_images/', null=True, blank=True)
    owner = models.ForeignKey(User, related_name='stores', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def total_units_in_stock(self):
        return self.product_set.aggregate(total_units=Sum('initial_quantity'))['total_units'] or 0

    def total_inventory_value(self):
        return self.product_set.aggregate(total_value=Sum(F('initial_quantity') * F('buying_price')))['total_value'] or 0

    def total_selling_stock_value(self):
        return self.product_set.aggregate(total_value=Sum(F('initial_quantity') * F('selling_price')))['total_value'] or 0

    def low_stock_products(self):
        return self.product_set.filter(initial_quantity__lte=F('reorder_level'))



class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    initial_quantity = models.IntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # New attribute

    def __str__(self):
        return self.name


class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)  # e.g., 'opening', 'stock_in', 'stock_out'
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - {self.transaction_type}'
