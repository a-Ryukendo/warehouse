from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, Q
import json
from decimal import Decimal

from .models import Product, StockTransaction, StockDetail, InventoryBalance
from .forms import ProductForm, StockTransactionForm


def index(request):
    """Main dashboard view"""
    # Get current inventory balances
    inventory_balances = InventoryBalance.objects.select_related('product').all()
    
    # Get recent transactions
    recent_transactions = StockTransaction.objects.select_related().prefetch_related('details__product').order_by('-transaction_date')[:10]
    
    # Get summary statistics
    total_products = Product.objects.count()
    total_transactions = StockTransaction.objects.count()
    total_value = sum(balance.current_quantity * Decimal('0') for balance in inventory_balances)  # Placeholder for actual value calculation
    
    context = {
        'inventory_balances': inventory_balances,
        'recent_transactions': recent_transactions,
        'total_products': total_products,
        'total_transactions': total_transactions,
        'total_value': total_value,
    }
    return render(request, 'inventory/index.html', context)


def product_list(request):
    """List all products"""
    products = Product.objects.all().order_by('product_id')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/product_list.html', {'page_obj': page_obj})


def product_detail(request, product_id):
    """Show product details and transaction history"""
    product = get_object_or_404(Product, product_id=product_id)
    
    # Get inventory balance
    balance, created = InventoryBalance.objects.get_or_create(product=product)
    
    # Get transaction history for this product
    transactions = StockDetail.objects.filter(product=product).select_related('transaction').order_by('-transaction__transaction_date')
    
    context = {
        'product': product,
        'balance': balance,
        'transactions': transactions,
    }
    return render(request, 'inventory/product_detail.html', context)


def add_product(request):
    """Add new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Add Product'})


def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('inventory:product_detail', product_id=product.product_id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'Edit Product'})


def transaction_list(request):
    """List all transactions"""
    transactions = StockTransaction.objects.select_related().prefetch_related('details__product').order_by('-transaction_date')
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/transaction_list.html', {'page_obj': page_obj})


def transaction_detail(request, transaction_id):
    """Show transaction details"""
    transaction_obj = get_object_or_404(StockTransaction, transaction_id=transaction_id)
    details = transaction_obj.details.select_related('product').all()
    
    # Calculate total amount
    total_amount = sum(detail.total_amount for detail in details)
    
    context = {
        'transaction': transaction_obj,
        'details': details,
        'total_amount': total_amount,
    }
    return render(request, 'inventory/transaction_detail.html', context)


def add_transaction(request):
    """Add new stock transaction"""
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction_obj = form.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('inventory:transaction_detail', transaction_id=transaction_obj.transaction_id)
    else:
        form = StockTransactionForm()
    
    return render(request, 'inventory/transaction_form.html', {'form': form, 'title': 'Add Transaction'})


def inventory_report(request):
    """Generate inventory report"""
    balances = InventoryBalance.objects.select_related('product').all().order_by('product__name')
    
    # Filter by search query
    search_query = request.GET.get('search', '')
    if search_query:
        balances = balances.filter(
            Q(product__name__icontains=search_query) | 
            Q(product__product_id__icontains=search_query)
        )
    
    context = {
        'balances': balances,
        'search_query': search_query,
    }
    return render(request, 'inventory/inventory_report.html', context)


# API Views
@csrf_exempt
@require_http_methods(["GET"])
def api_products(request):
    """API endpoint to get all products"""
    products = Product.objects.all()
    data = [{
        'product_id': p.product_id,
        'name': p.name,
        'description': p.description,
        'unit': p.unit,
        'created_at': p.created_at.isoformat(),
    } for p in products]
    return JsonResponse({'products': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_product_detail(request, product_id):
    """API endpoint to get product details"""
    try:
        product = Product.objects.get(product_id=product_id)
        balance, created = InventoryBalance.objects.get_or_create(product=product)
        
        data = {
            'product_id': product.product_id,
            'name': product.name,
            'description': product.description,
            'unit': product.unit,
            'current_quantity': float(balance.current_quantity),
            'last_updated': balance.last_updated.isoformat(),
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def api_inventory(request):
    """API endpoint to get current inventory"""
    balances = InventoryBalance.objects.select_related('product').all()
    data = [{
        'product_id': b.product.product_id,
        'product_name': b.product.name,
        'current_quantity': float(b.current_quantity),
        'unit': b.product.unit,
        'last_updated': b.last_updated.isoformat(),
    } for b in balances]
    return JsonResponse({'inventory': data})


@csrf_exempt
@require_http_methods(["POST"])
def api_add_transaction(request):
    """API endpoint to add a new transaction"""
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            # Create transaction
            transaction_obj = StockTransaction.objects.create(
                transaction_type=data['transaction_type'],
                reference_no=data.get('reference_no', ''),
                notes=data.get('notes', ''),
                transaction_date=data.get('transaction_date', timezone.now())
            )
            
            # Create transaction details
            for item in data['items']:
                product = Product.objects.get(product_id=item['product_id'])
                StockDetail.objects.create(
                    transaction=transaction_obj,
                    product=product,
                    quantity=Decimal(str(item['quantity'])),
                    unit_price=Decimal(str(item.get('unit_price', 0)))
                )
                
                # Update inventory balance
                balance, created = InventoryBalance.objects.get_or_create(product=product)
                if data['transaction_type'] == 'IN':
                    balance.current_quantity += Decimal(str(item['quantity']))
                elif data['transaction_type'] == 'OUT':
                    balance.current_quantity -= Decimal(str(item['quantity']))
                balance.save()
        
        return JsonResponse({'success': True, 'transaction_id': transaction_obj.transaction_id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def api_transactions(request):
    """API endpoint to get transactions"""
    transactions = StockTransaction.objects.select_related().prefetch_related('details__product').order_by('-transaction_date')
    
    data = []
    for t in transactions:
        transaction_data = {
            'transaction_id': t.transaction_id,
            'transaction_type': t.transaction_type,
            'reference_no': t.reference_no,
            'notes': t.notes,
            'transaction_date': t.transaction_date.isoformat(),
            'items': []
        }
        
        for detail in t.details.all():
            transaction_data['items'].append({
                'product_id': detail.product.product_id,
                'product_name': detail.product.name,
                'quantity': float(detail.quantity),
                'unit_price': float(detail.unit_price),
                'total_amount': float(detail.total_amount),
            })
        
        data.append(transaction_data)
    
    return JsonResponse({'transactions': data})
