from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Web interface URLs
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('products/<str:product_id>/edit/', views.edit_product, name='edit_product'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    
    # API URLs
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<str:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('api/inventory/', views.api_inventory, name='api_inventory'),
    path('api/transactions/', views.api_transactions, name='api_transactions'),
    path('api/transactions/add/', views.api_add_transaction, name='api_add_transaction'),
] 