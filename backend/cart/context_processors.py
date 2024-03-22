from django.core.handlers.asgi import ASGIRequest

from .cart import Cart


def cart(request: ASGIRequest) -> dict:
    return {'cart': Cart(request)}
