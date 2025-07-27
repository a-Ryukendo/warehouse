from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Product(models.Model):
    """Product master table (prodmast) - stores product details"""
    product_id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20, default='PCS')  # Pieces, KG, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product_id} - {self.name}"
    
    class Meta:
        db_table = 'prodmast'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class StockTransaction(models.Model):
    """Stock main table (stckmain) - stores transaction details"""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUST', 'Adjustment'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.transaction_date.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        db_table = 'stckmain'
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'


class StockDetail(models.Model):
    """Stock detail table (stckdetail) - stores product details within each transaction"""
    detail_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(StockTransaction, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.detail_id} - {self.product.name} - Qty: {self.quantity}"
    
    class Meta:
        db_table = 'stckdetail'
        verbose_name = 'Stock Detail'
        verbose_name_plural = 'Stock Details'


class InventoryBalance(models.Model):
    """Helper model to track current inventory balance for each product"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - Current Stock: {self.current_quantity}"
    
    class Meta:
        verbose_name = 'Inventory Balance'
        verbose_name_plural = 'Inventory Balances'
