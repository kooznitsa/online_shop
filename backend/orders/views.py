from typing import Union

from django.contrib.admin.views.decorators import staff_member_required
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, aget_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .models import Order, OrderItem
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


@method_decorator(staff_member_required, name='dispatch')
class AdminOrderDetail(View):
    async def get(self, request: ASGIRequest, order_id: int) -> RedirectOrResponse:
        order = await aget_object_or_404(Order, id=order_id)

        context = {'order': order}

        return render(request, 'admin/orders/order/detail.html', context)
    