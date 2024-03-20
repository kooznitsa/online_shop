import os

from django.shortcuts import render, redirect, aget_object_or_404
from django.views import View

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm

os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'


class CartDetail(View):
    async def post(self, request, product_id: int, method: str):
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
   
    async def get(self, request):
        cart = Cart(request)

        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'override': True})

        context = {'cart': cart}

        return render(request, 'cart/detail.html', context)
    