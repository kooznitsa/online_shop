from typing import Union

from django.shortcuts import render, redirect
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created

RedirectOrResponse = Union[HttpResponseRedirect, HttpResponse]


class OrderDetail(View):
    async def post(self, request: ASGIRequest) -> RedirectOrResponse:
        cart = Cart(request)
        form = OrderCreateForm(request.POST)
    
        if form.is_valid():
            order = form.save()
        
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            
            await cart.clear()
            
            # launch asynchronous task
            order_created.delay(order.id)
            
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect(reverse('payment:process'))
        
        context = {'cart': cart, 'form': form}

        return render(request, 'orders/order/create.html', context)
    
    async def get(self, request: ASGIRequest) -> RedirectOrResponse:
        cart = Cart(request)
        form = OrderCreateForm()

        context = {'cart': cart, 'form': form}

        return render(request, 'orders/order/create.html', context)
