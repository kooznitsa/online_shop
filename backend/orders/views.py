from django.shortcuts import render
from django.views import View

from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created


class OrderDetail(View):
    async def post(self, request):
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
            
        context = {'order': order}

        return render(request, 'orders/order/created.html', context)
    
    async def get(self, request):
        cart = Cart(request)
        form = OrderCreateForm()

        context = {'cart': cart, 'form': form}

        return render(request, 'orders/order/create.html', context)
