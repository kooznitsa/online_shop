import csv
import datetime
from itertools import chain

from django.contrib import admin
from django.core.handlers.asgi import ASGIRequest
from django.http import StreamingHttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def order_payment(obj: Order) -> str:
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ''

order_payment.short_description = 'Stripe payment'


def order_detail(obj: Order) -> str:
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj: Order) -> str:
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')

order_pdf.short_description = 'Invoice'


class Echo:
    @staticmethod
    def write(value: str) -> str:
        return value


def export_to_csv(modeladmin, request: ASGIRequest, queryset: list[Order]) -> StreamingHttpResponse:
    echo_buffer = Echo()
    opts = modeladmin.model._meta

    writer = csv.writer(echo_buffer, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    columns = writer.writerow([field.verbose_name for field in fields])
    rows = (
        writer.writerow([getattr(obj, field.name) for field in fields]) 
        for obj in queryset
    )

    response = StreamingHttpResponse(chain(columns, rows), content_type='text/csv')
    filename = f'{opts.verbose_name}-{datetime.datetime.now().timestamp()}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
       
    return response

export_to_csv.short_description = 'Export to CSV'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 
        'city', 'paid', order_payment, 'created', 'updated', order_detail, order_pdf,
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
