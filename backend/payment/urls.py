from django.urls import path

from . import views
from . import webhooks

app_name = 'payment'

urlpatterns = [
    path('process/', views.PaymentProcess.as_view(), name='process'),
    path('completed/', views.PaymentCompleted.as_view(), name='completed'),
    path('canceled/', views.PaymentCanceled.as_view(), name='canceled'),
    path('webhook/', webhooks.StripeWebhook.as_view(), name='stripe-webhook'),
]
