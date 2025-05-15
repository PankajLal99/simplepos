from django.contrib import admin
from .models import Product, Invoice, InvoiceItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('created_at',)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'total_amount', 'created_at')
    search_fields = ('invoice_number',)
    list_filter = ('date', 'created_at')
    inlines = [InvoiceItemInline]
