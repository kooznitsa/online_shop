from django.urls import path

from . import views

app_name = 'coupons'

urlpatterns = [
    path('apply/', views.CouponDetail.as_view(), name='apply'),
]
