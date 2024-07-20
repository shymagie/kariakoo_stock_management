from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.crypto import get_random_string
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from oauth2_provider.models import AccessToken, Application
from django.db.models import Sum, F
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
import requests

from .models import Membership, Store, Product, Transaction
from .serializers import MembershipSerializer, StoreSerializer, ProductSerializer, TransactionSerializer

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        return Store.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['owner'] = request.user.id
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def store_statistics(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        statistics = {
            'totalUnitsInStock': store.total_units_in_stock(),
            'totalInventoryValue': store.total_inventory_value(),
            'totalSellingStockValue': store.total_selling_stock_value(),
        }
        return Response(statistics)
    except Store.DoesNotExist:
        return Response({'error': 'Store not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['store'] = request.data.get('store')
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Create the initial transaction
        product = serializer.instance
        Transaction.objects.create(
            product=product,
            transaction_type='opening',
            buying_price=product.buying_price,
            selling_price=product.selling_price,
            quantity=product.initial_quantity
        )
        return Response(serializer.data, status=201)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    client_id = settings.GOOGLE_CLIENT_ID
    scope = "openid email profile"
    response_type = "code"
    
    url = (f"{GOOGLE_AUTH_URL}?response_type={response_type}&client_id={client_id}"
           f"&redirect_uri={redirect_uri}&scope={scope}")
    
    return redirect(url)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_callback(request):
    id_token = request.data.get('token')
    if not id_token:
        return Response({'error': 'No id_token provided'}, status=400)

    response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}')
    if response.status_code != 200:
        return Response({'error': 'Invalid id_token'}, status=400)

    user_info = response.json()
    email = user_info.get('email')
    if not email:
        return Response({'error': 'Email not available in id_token'}, status=400)

    user, _ = User.objects.get_or_create(username=email, defaults={'email': email})

    application = Application.objects.get(name="stoo yangu")
    expires = timezone.now() + timedelta(seconds=36000)
    unique_token = get_random_string(30)
    access_token = AccessToken.objects.create(user=user, application=application, token=unique_token, expires=expires, scope='read write')

    return Response({'access_token': access_token.token})
