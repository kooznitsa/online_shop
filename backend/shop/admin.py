from django.contrib import admin

from .models import Category, Product

APP_ADMIN_URL = '/admin/shop/'

admin.site.site_header = 'Admin Panel'
admin.site.site_title = 'Shop admin'
admin.site.index_title = 'Shop administration'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name__iexact',)
    search_help_text = f'Search in: {", ".join(search_fields)}'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name__iexact',)
    search_help_text = f'Search in: {", ".join(search_fields)}'
