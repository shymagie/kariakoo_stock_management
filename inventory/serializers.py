from rest_framework import serializers
from .models import Membership, Store, Product, Transaction

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'



class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'image', 'owner']



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'initial_quantity', 'buying_price', 'selling_price', 'reorder_level', 'image']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'product', 'transaction_type', 'buying_price', 'selling_price', 'quantity', 'date']
