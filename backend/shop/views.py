from typing import Union

from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, aget_object_or_404
from django.views import View

from cart.forms import CartAddProductForm
from .models import Category, Product
from .recommender import Recommender

RedirectOrResponse = Union[HttpResponseRedirect, HttpResponse]


class ProductList(View):
    async def get(self, request: ASGIRequest, category_slug: str | None = None) -> RedirectOrResponse:
        category = None
        categories = [category async for category in Category.objects.all()]
        products = [product async for product in Product.objects.filter(available=True)]
        
        if category_slug:
            category = await aget_object_or_404(Category, slug=category_slug)
            products = [product async for product in Product.objects.filter(category=category)]

        context = {
            'category': category,
            'categories': categories,
            'products': products,
        }
        
        return render(request, 'shop/product/list.html', context)


class ProductDetail(View):
    async def get(self, request: ASGIRequest, id: int, slug: str) -> RedirectOrResponse:
        product = await aget_object_or_404(
            Product.objects.prefetch_related('category'), 
            id=id, slug=slug, available=True,
        )
        cart_product_form = CartAddProductForm()

        r = Recommender()
        recommended_products = r.suggest_products_for([product], 4)

        context = {
            'product': product, 
            'cart_product_form': cart_product_form,
            'recommended_products': recommended_products,
        }
        
        return render(request, 'shop/product/detail.html', context)
