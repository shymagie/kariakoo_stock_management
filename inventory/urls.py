from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'memberships', MembershipViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/social/google/', google_login, name='google_login'),
    path('auth/social/google/callback/', google_callback, name='google_callback'),
    path('stores/<int:store_pk>/products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='store-products'),
    path('stores/<int:store_id>/statistics/', store_statistics, name='store_statistics'),
]
