from typing import Union

from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from .models import Coupon
from .forms import CouponApplyForm

RedirectOrResponse = Union[HttpResponseRedirect, HttpResponse]


class CouponDetail(View):
    async def post(self, request: ASGIRequest) -> RedirectOrResponse:
        now = timezone.now()
        form = CouponApplyForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = await Coupon.objects.aget(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True,
                )
                request.session['coupon_id'] = coupon.id
            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
        
        return redirect('cart:cart_detail')
