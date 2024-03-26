import os
from typing import Union

from django.shortcuts import render, redirect, aget_object_or_404
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View

from coupons.forms import CouponApplyForm
from .cart import Cart
from .forms import CartAddProductForm
from shop.models import Product
from shop.recommender import Recommender

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

RedirectOrResponse = Union[HttpResponseRedirect, HttpResponse]


class CartDetail(View):
    async def post(self, request: ASGIRequest, product_id: int, method: str) -> RedirectOrResponse:
        cart = Cart(request)
        product = await aget_object_or_404(Product.objects.prefetch_related('category'), id=product_id)
        
        if method == 'cart_add':
            form = CartAddProductForm(request.POST)
            
            if form.is_valid():
                cd = form.cleaned_data
                await cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])

        elif method == 'cart_remove':
            await cart.remove(product)
        
        return redirect('cart:cart_detail')
   
    async def get(self, request: ASGIRequest) -> RedirectOrResponse:
        cart = Cart(request)

        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'override': True})

        coupon_apply_form = CouponApplyForm()

        r = Recommender()
        cart_products = [item['product'] for item in cart]
        if cart_products:
            recommended_products = r.suggest_products_for(cart_products, max_results=4)
        else:
            recommended_products = []

        context = {
            'cart': cart,
            'coupon_apply_form': coupon_apply_form,
            'recommended_products': recommended_products,
        }

        return render(request, 'cart/detail.html', context)
    