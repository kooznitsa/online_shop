from decimal import Decimal
import os
from typing import Union

from django.shortcuts import redirect, render, reverse, aget_object_or_404
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
import stripe

from orders.models import Order

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe.api_version = os.environ.get('STRIPE_API_VERSION')

RedirectOrResponse = Union[HttpResponseRedirect, HttpResponse]


class PaymentProcess(View):
    async def post(self, request: ASGIRequest) -> RedirectOrResponse:
        order_id = request.session.get('order_id', None)
        order = await aget_object_or_404(Order, id=order_id)

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': request.build_absolute_uri(reverse('payment:completed')),
            'cancel_url': request.build_absolute_uri(reverse('payment:canceled')),
            'line_items': [],
        }

        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'gbp',
                    'product_data': {'name': item.product.name},
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(**session_data)

        return redirect(session.url, code=303)

    async def get(self, request: ASGIRequest) -> RedirectOrResponse:
        order_id = request.session.get('order_id', None)
        order = await aget_object_or_404(Order, id=order_id)

        return render(request, 'payment/process.html', locals())
    

class PaymentCompleted(View):
    async def get(self, request: ASGIRequest) -> RedirectOrResponse:
        return render(request, 'payment/completed.html')
    

class PaymentCanceled(View):
    async def get(self, request: ASGIRequest) -> RedirectOrResponse:
        return render(request, 'payment/canceled.html')
    