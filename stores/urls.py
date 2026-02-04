from django.urls import path
from . import views
from orders.views import StoreOrderListAPIView

urlpatterns = [
    path('stores/<int:store_id>/orders/', StoreOrderListAPIView.as_view()),
]
