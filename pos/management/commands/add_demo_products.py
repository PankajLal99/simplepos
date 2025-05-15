from django.core.management.base import BaseCommand
from pos.models import Product, Stock
import random

class Command(BaseCommand):
    help = 'Add realistic demo products with appropriate prices and stock.'

    def handle(self, *args, **kwargs):
        # List of realistic products with their price ranges
        products = [
            # Office Supplies
            {'name': 'A4 Paper (500 sheets)', 'price_range': (200, 300), 'maintain_stock': True, 'stock_range': (10, 50)},
            {'name': 'Ballpoint Pen (Pack of 10)', 'price_range': (50, 100), 'maintain_stock': True, 'stock_range': (20, 100)},
            {'name': 'Stapler', 'price_range': (150, 250), 'maintain_stock': True, 'stock_range': (5, 20)},
            {'name': 'Staples (Box of 1000)', 'price_range': (30, 50), 'maintain_stock': True, 'stock_range': (10, 50)},
            {'name': 'Paper Clips (Box of 100)', 'price_range': (20, 40), 'maintain_stock': True, 'stock_range': (15, 60)},
            
            # Electronics
            {'name': 'USB Flash Drive 32GB', 'price_range': (300, 500), 'maintain_stock': True, 'stock_range': (5, 20)},
            {'name': 'Wireless Mouse', 'price_range': (400, 800), 'maintain_stock': True, 'stock_range': (3, 15)},
            {'name': 'Keyboard', 'price_range': (500, 1200), 'maintain_stock': True, 'stock_range': (2, 10)},
            {'name': 'HDMI Cable', 'price_range': (200, 400), 'maintain_stock': True, 'stock_range': (8, 30)},
            {'name': 'USB-C Cable', 'price_range': (150, 300), 'maintain_stock': True, 'stock_range': (10, 40)},
            
            # Snacks & Beverages
            {'name': 'Mineral Water (500ml)', 'price_range': (10, 20), 'maintain_stock': True, 'stock_range': (50, 200)},
            {'name': 'Chips (Regular Pack)', 'price_range': (10, 20), 'maintain_stock': True, 'stock_range': (30, 100)},
            {'name': 'Chocolate Bar', 'price_range': (20, 40), 'maintain_stock': True, 'stock_range': (40, 150)},
            {'name': 'Biscuits (Pack of 10)', 'price_range': (30, 50), 'maintain_stock': True, 'stock_range': (20, 80)},
            {'name': 'Soft Drink (330ml)', 'price_range': (20, 35), 'maintain_stock': True, 'stock_range': (40, 120)},
            
            # Cleaning Supplies
            {'name': 'Hand Sanitizer (100ml)', 'price_range': (50, 100), 'maintain_stock': True, 'stock_range': (15, 50)},
            {'name': 'Tissue Paper (Pack of 6)', 'price_range': (100, 150), 'maintain_stock': True, 'stock_range': (10, 40)},
            {'name': 'Hand Soap (250ml)', 'price_range': (80, 120), 'maintain_stock': True, 'stock_range': (8, 30)},
            {'name': 'Cleaning Wipes (Pack of 50)', 'price_range': (150, 200), 'maintain_stock': True, 'stock_range': (5, 20)},
            {'name': 'Air Freshener', 'price_range': (100, 200), 'maintain_stock': True, 'stock_range': (5, 25)},
            
            # Services (No Stock)
            {'name': 'Photocopy (Black & White)', 'price_range': (1, 2), 'maintain_stock': False},
            {'name': 'Photocopy (Color)', 'price_range': (5, 10), 'maintain_stock': False},
            {'name': 'Printing (Black & White)', 'price_range': (2, 5), 'maintain_stock': False},
            {'name': 'Printing (Color)', 'price_range': (10, 20), 'maintain_stock': False},
            {'name': 'Lamination (A4)', 'price_range': (10, 20), 'maintain_stock': False},
        ]

        for product_data in products:
            price = round(random.uniform(*product_data['price_range']), 2)
            product = Product.objects.create(
                name=product_data['name'],
                price=price,
                maintain_stock=product_data['maintain_stock']
            )
            
            if product.maintain_stock:
                stock_quantity = random.randint(*product_data['stock_range'])
                stock = Stock.objects.create(product=product, current_quantity=stock_quantity)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {product.name} (₹{price}) - Stock: {stock_quantity}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {product.name} (₹{price}) - No Stock Management'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('All demo products added successfully!')) 