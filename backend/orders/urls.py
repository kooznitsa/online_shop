from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.OrderDetail.as_view(), name='order_create'),
    path('admin/order/<int:order_id>/', views.AdminOrderDetail.as_view(), name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf/', views.AdminOrderPDF.as_view(), name='admin_order_pdf'),
]
