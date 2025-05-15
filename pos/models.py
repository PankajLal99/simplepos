from django.db import models
from django.utils import timezone
import uuid

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, editable=False)
    barcode = models.CharField(max_length=50, unique=True, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    maintain_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        if not self.barcode:
            self.barcode = f"BAR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Stock(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    current_quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.current_quantity}"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True, null=True)  # For invoice number or other reference
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'IN':
            self.stock.current_quantity += self.quantity
        else:
            self.stock.current_quantity -= self.quantity
        self.stock.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.quantity} units"

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    round_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_items = models.ManyToManyField(Product, through='InvoiceItem')

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        # Calculate round off
        if self.total_amount is not None:
            rounded = round(self.total_amount)
            self.round_off = rounded - float(self.total_amount)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
        # Update stock if product maintains stock
        if self.product.maintain_stock:
            stock, created = Stock.objects.get_or_create(product=self.product)
            StockTransaction.objects.create(
                stock=stock,
                transaction_type='OUT',
                quantity=self.quantity,
                reference=self.invoice.invoice_number,
                notes=f"Sold in invoice {self.invoice.invoice_number}"
            )

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"
