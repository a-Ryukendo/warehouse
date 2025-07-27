from django.contrib import admin
from .models import Product, StockTransaction, StockDetail, InventoryBalance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'unit', 'created_at']
    search_fields = ['product_id', 'name', 'description']
    list_filter = ['unit', 'created_at']
    ordering = ['product_id']


class StockDetailInline(admin.TabularInline):
    model = StockDetail
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'total_amount']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'transaction_type', 'reference_no', 'transaction_date', 'total_items']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['reference_no', 'notes']
    inlines = [StockDetailInline]
    date_hierarchy = 'transaction_date'
    
    def total_items(self, obj):
        return obj.details.count()
    total_items.short_description = 'Total Items'


@admin.register(StockDetail)
class StockDetailAdmin(admin.ModelAdmin):
    list_display = ['detail_id', 'transaction', 'product', 'quantity', 'unit_price', 'total_amount']
    list_filter = ['product', 'transaction__transaction_type']
    search_fields = ['product__name', 'product__product_id']


@admin.register(InventoryBalance)
class InventoryBalanceAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_quantity', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['product__name', 'product__product_id']
    readonly_fields = ['last_updated']
