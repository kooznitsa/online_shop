from asgiref.sync import async_to_sync
import logging
import os

from celery import shared_task
from django.core.mail import send_mail

from .models import Order

info_logger = logging.getLogger('info_logger')


async def notify_customer(order_id: int) -> int:
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = await Order.objects.aget(id=order_id)
    subject = f'Order No {order.id}'
    message = (
        f'Dear {order.first_name},\n\n'
        f'You have successfully placed an order at Weasleys\' Wizard Wheezes! '
        f'Your order ID is {order.id}.'
    )
    
    mail_sent = send_mail(subject, message, os.environ.get('EMAIL_HOST_USER'), [order.email])

    info_logger.info(f'MAIL SENT: {mail_sent}, {order.id}')
    
    return mail_sent


@shared_task
def order_created(order_id: int) -> int:
    return async_to_sync(notify_customer)(order_id)
