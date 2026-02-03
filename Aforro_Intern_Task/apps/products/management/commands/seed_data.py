import random
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Category, Product
from apps.stores.models import Store, Inventory

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Create Categories
        categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Toys', 'Sports', 'Beauty', 'Automotive', 'Garden', 'Music']
        cat_objs = []
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name)
            cat_objs.append(cat)
        self.stdout.write(f'Created {len(cat_objs)} categories.')

        # 2. Create Stores
        stores = []
        for i in range(20):
            store, _ = Store.objects.get_or_create(
                name=f'Store {i+1}',
                location=f'Location {i+1}'
            )
            stores.append(store)
        self.stdout.write(f'Created {len(stores)} stores.')

        # 3. Create Products (Batch create for speed)
        products = []
        for i in range(1000):
            products.append(Product(
                title=f'Product {i+1} - {random.choice(["Pro", "Max", "Lite", "Ultra"])}',
                description='Sample description for testing search functionality.',
                price=random.uniform(10.0, 500.0),
                category=random.choice(cat_objs)
            ))
        # Bulk create to save DB queries
        Product.objects.bulk_create(products) 
        all_products = list(Product.objects.all())
        self.stdout.write(f'Created {len(all_products)} products.')

        # 4. Create Inventory (Random stock for stores)
        inventory_items = []
        for store in stores:
            # Each store gets 300 random products
            store_products = random.sample(all_products, 300)
            for prod in store_products:
                inventory_items.append(Inventory(
                    store=store,
                    product=prod,
                    quantity=random.randint(0, 50) # Some will have 0 stock to test failures
                ))
        
        Inventory.objects.bulk_create(inventory_items, ignore_conflicts=True)
        self.stdout.write(f'Created {len(inventory_items)} inventory records.')
        
        self.stdout.write(self.style.SUCCESS('Data seeding complete!'))