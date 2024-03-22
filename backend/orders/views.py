import os
from typing import Union

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles import finders
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, aget_object_or_404
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from xhtml2pdf import pisa

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


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
        sUrl = os.environ.get('STATIC_URL')
        sRoot = os.environ.get('STATIC_ROOT')
        mUrl = os.environ.get('MEDIA_URL')
        mRoot = os.environ.get('MEDIA_ROOT')

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    if not os.path.isfile(path):
        raise RuntimeError(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


@method_decorator(staff_member_required, name='dispatch')
class AdminOrderPDF(View):
    async def get(self, request: ASGIRequest, order_id: int):
        order = await aget_object_or_404(Order, id=order_id)

        context = {'order': order}

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
        html = render_to_string('orders/order/pdf.html', context)

        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        
        return response
