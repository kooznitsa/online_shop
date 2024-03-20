from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetail.as_view(), name='cart_detail'),
    path('add/<int:product_id>/', views.CartDetail.as_view(), {'method': 'cart_add'}, name='cart_add'),
    path('remove/<int:product_id>/', views.CartDetail.as_view(), {'method': 'cart_remove'}, name='cart_remove'),
]
