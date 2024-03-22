import logging
import os

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import stripe

from orders.models import Order

error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('info_logger')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):
    async def post(self, request):
        event = None
        payload = request.body.decode('utf-8')
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                os.environ.get('STRIPE_WEBHOOK_SECRET'),
            )
        except ValueError as e:
            # Invalid payload
            error_logger.error(f'WEBHOOK INVALID PAYLOAD: {e}')
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            error_logger.error(f'WEBHOOK INVALID SIGNATURE: {e}')
            return HttpResponse(status=400)
        except Exception as e:
            error_logger.error(f'WEBHOOK UNKNOWN ERR: {e}')

        if event.type == 'checkout.session.completed':
            session = event.data.object
            if session.mode == 'payment' and session.payment_status == 'paid':
                try:
                    order = await Order.objects.aget(id=session.client_reference_id)
                    info_logger.info(f'ORDER: {order}')
                except Order.DoesNotExist:
                    return HttpResponse(status=404)
                # mark order as paid
                order.paid = True

                # store Stripe payment ID
                order.stripe_id = session.payment_intent

                order.save()
        
        return HttpResponse(status=200)
    