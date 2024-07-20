from django.contrib import admin
from .models import Membership, Store, Product, Transaction

admin.site.register(Membership)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Transaction)
