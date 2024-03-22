from asgiref.sync import async_to_sync
from io import BytesIO
import os

from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import aget_object_or_404
from xhtml2pdf import pisa

from orders.models import Order
from orders.views import link_callback


async def send_pdf(order_id: int) -> None:
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    order = await aget_object_or_404(Order, id=order_id)
    context = {'order': order}

    subject = f'Weasleys\' Wizard Wheezes — Invoice No {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(
        subject,
        message,
        os.environ.get('EMAIL_HOST_USER'),
        [order.email],
    )

    html = render_to_string('orders/order/pdf.html', context)
    
    out = BytesIO()

    pisa.CreatePDF(html, dest=out, link_callback=link_callback)
    
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    
    email.send()


@shared_task
def payment_completed(order_id: int) -> None:
    return async_to_sync(send_pdf)(order_id)
