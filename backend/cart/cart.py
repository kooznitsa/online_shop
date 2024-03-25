from asgiref.sync import async_to_sync

from decimal import Decimal
from typing import Generator

from django.conf import settings
from django.core.handlers.asgi import ASGIRequest

from coupons.models import Coupon
from shop.models import Product


class Cart:
    def __init__(self, request: ASGIRequest) -> None:
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
        # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    async def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        await self.save()
        
    async def save(self) -> None:
        """
        Mark the session as "modified" to make sure it gets saved.
        """
        self.session.modified = True

    async def remove(self, product: Product) -> None:
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
        
        await self.save()


    def __iter__(self) -> Generator:
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> Decimal:
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self) -> Decimal:
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())


    async def clear(self) -> None:
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        await self.save()

    @property
    def coupon(self) -> list[Coupon]:
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None
    
    def get_discount(self) -> Decimal:
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self) -> Decimal:
        return self.get_total_price() - self.get_discount()
