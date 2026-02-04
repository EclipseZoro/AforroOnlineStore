from django.urls import path
from .views import StoreInventoryListAPIView
from orders.views import StoreOrderListAPIView

urlpatterns = [
    path('stores/<int:store_id>/orders/', StoreOrderListAPIView.as_view()),
    path('stores/<int:store_id>/inventory/', StoreInventoryListAPIView.as_view()),
]
