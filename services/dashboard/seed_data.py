import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from models import Base

# Categories data
categories = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Home & Kitchen", "description": "Home appliances and kitchen supplies"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Books", "description": "Books, e-books, and audiobooks"},
    {"name": "Beauty", "description": "Beauty and personal care products"}
]

# Products data
products = [
    # Electronics
    {"name": "Smartphone X", "description": "Latest smartphone with advanced features", "price": 799.99, "sku": "ELEC-001", "category_id": 1},
    {"name": "Laptop Pro", "description": "High-performance laptop for professionals", "price": 1299.99, "sku": "ELEC-002", "category_id": 1},
    {"name": "Wireless Earbuds", "description": "Premium wireless earbuds with noise cancellation", "price": 149.99, "sku": "ELEC-003", "category_id": 1},
    {"name": "Smart Watch", "description": "Fitness tracker and smartwatch in one", "price": 199.99, "sku": "ELEC-004", "category_id": 1},
    {"name": "4K TV", "description": "55-inch 4K Ultra HD Smart TV", "price": 499.99, "sku": "ELEC-005", "category_id": 1},
    
    # Home & Kitchen
    {"name": "Coffee Maker", "description": "Programmable coffee maker with thermal carafe", "price": 89.99, "sku": "HOME-001", "category_id": 2},
    {"name": "Air Fryer", "description": "Digital air fryer for healthier cooking", "price": 129.99, "sku": "HOME-002", "category_id": 2},
    {"name": "Robot Vacuum", "description": "Smart robot vacuum with mapping technology", "price": 349.99, "sku": "HOME-003", "category_id": 2},
    {"name": "Blender", "description": "High-speed blender for smoothies and more", "price": 79.99, "sku": "HOME-004", "category_id": 2},
    {"name": "Toaster Oven", "description": "Convection toaster oven with multiple functions", "price": 119.99, "sku": "HOME-005", "category_id": 2},
    
    # Clothing
    {"name": "Men's Jeans", "description": "Slim-fit jeans for men", "price": 49.99, "sku": "CLOTH-001", "category_id": 3},
    {"name": "Women's Dress", "description": "Casual summer dress", "price": 59.99, "sku": "CLOTH-002", "category_id": 3},
    {"name": "Running Shoes", "description": "Performance running shoes", "price": 89.99, "sku": "CLOTH-003", "category_id": 3},
    {"name": "Winter Jacket", "description": "Waterproof winter jacket with hood", "price": 129.99, "sku": "CLOTH-004", "category_id": 3},
    {"name": "T-Shirt Pack", "description": "Pack of 3 cotton t-shirts", "price": 24.99, "sku": "CLOTH-005", "category_id": 3},
    
    # Books
    {"name": "Bestseller Novel", "description": "Latest bestselling fiction novel", "price": 14.99, "sku": "BOOK-001", "category_id": 4},
    {"name": "Cookbook", "description": "International cuisine cookbook", "price": 29.99, "sku": "BOOK-002", "category_id": 4},
    {"name": "Business Strategy", "description": "Book on modern business strategies", "price": 19.99, "sku": "BOOK-003", "category_id": 4},
    {"name": "Self-Help Guide", "description": "Popular self-improvement book", "price": 12.99, "sku": "BOOK-004", "category_id": 4},
    {"name": "Children's Book", "description": "Illustrated children's story book", "price": 9.99, "sku": "BOOK-005", "category_id": 4},
    
    # Beauty
    {"name": "Face Cream", "description": "Hydrating face cream for all skin types", "price": 24.99, "sku": "BEAUTY-001", "category_id": 5},
    {"name": "Shampoo", "description": "Moisturizing shampoo for dry hair", "price": 12.99, "sku": "BEAUTY-002", "category_id": 5},
    {"name": "Makeup Set", "description": "Complete makeup kit with case", "price": 49.99, "sku": "BEAUTY-003", "category_id": 5},
    {"name": "Perfume", "description": "Luxury perfume with floral scent", "price": 69.99, "sku": "BEAUTY-004", "category_id": 5},
    {"name": "Men's Grooming Kit", "description": "Complete grooming kit for men", "price": 39.99, "sku": "BEAUTY-005", "category_id": 5}
]

# Initial inventory data for all products
inventory_data = {
    "ELEC-001": 50,
    "ELEC-002": 30,
    "ELEC-003": 100,
    "ELEC-004": 75,
    "ELEC-005": 20,
    "HOME-001": 40,
    "HOME-002": 35,
    "HOME-003": 25,
    "HOME-004": 60,
    "HOME-005": 45,
    "CLOTH-001": 80,
    "CLOTH-002": 65,
    "CLOTH-003": 55,
    "CLOTH-004": 30,
    "CLOTH-005": 120,
    "BOOK-001": 150,
    "BOOK-002": 70,
    "BOOK-003": 90,
    "BOOK-004": 110,
    "BOOK-005": 130,
    "BEAUTY-001": 85,
    "BEAUTY-002": 95,
    "BEAUTY-003": 40,
    "BEAUTY-004": 55,
    "BEAUTY-005": 60
}

# Marketplaces
marketplaces = ["Amazon", "Walmart", "Direct"]

# Function to generate random sales
def generate_sales(db: Session, num_sales: int, start_date: datetime, end_date: datetime):
    # Get all product IDs
    product_map = {}
    for product in db.query(models.Product).all():
        product_map[product.id] = product.price
    
    product_ids = list(product_map.keys())
    
    # Generate random sales
    delta = end_date - start_date
    sales = []
    
    for i in range(num_sales):
        # Random date within the range
        random_days = random.randint(0, delta.days)
        sale_date = start_date + timedelta(days=random_days)
        
        # Random number of items in the sale (1-5)
        num_items = random.randint(1, 5)
        
        # Random marketplace
        marketplace = random.choice(marketplaces)
        
        # Create sale items
        sale_items = []
        total_amount = 0
        
        # Select random products
        selected_products = random.sample(product_ids, min(num_items, len(product_ids)))
        
        for product_id in selected_products:
            quantity = random.randint(1, 3)
            unit_price = product_map[product_id]
            subtotal = unit_price * quantity
            
            sale_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal
            })
            
            total_amount += subtotal
        
        sales.append({
            "order_id": f"ORD-{100000 + i}",
            "total_amount": total_amount,
            "marketplace": marketplace,
            "transaction_date": sale_date,
            "items": sale_items
        })
    
    return sales


def seed_database():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_categories = db.query(models.Category).count()
        if existing_categories > 0:
            print("Database already seeded. Exiting...")
            return
        
        print("Seeding database...")
        
        # Add categories
        for category_data in categories:
            category = models.Category(**category_data)
            db.add(category)
        db.commit()
        
        # Add products
        for product_data in products:
            product = models.Product(**product_data)
            db.add(product)
        db.commit()
        
        # Add inventory
        for product in db.query(models.Product).all():
            inventory = models.Inventory(
                product_id=product.id,
                quantity=inventory_data[product.sku],
                low_stock_threshold=10,
                last_restocked=datetime.now()
            )
            db.add(inventory)
        db.commit()
        
        # Generate sales for the past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        sales = generate_sales(db, 500, start_date, end_date)
        
        # Add sales to database
        for sale_data in sales:
            items = sale_data.pop("items")
            sale = models.Sale(**sale_data)
            db.add(sale)
            db.flush()
            
            for item_data in items:
                item_data["sale_id"] = sale.id
                sale_item = models.SaleItem(**item_data)
                db.add(sale_item)
                
                # Update inventory
                inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item_data["product_id"]).first()
                if inventory:
                    previous_quantity = inventory.quantity
                    inventory.quantity = max(0, inventory.quantity - item_data["quantity"])
                    
                    # Add inventory log
                    inventory_log = models.InventoryLog(
                        product_id=item_data["product_id"],
                        previous_quantity=previous_quantity,
                        new_quantity=inventory.quantity,
                        change_reason=f"Sale - Order ID: {sale.order_id}",
                        timestamp=sale.transaction_date
                    )
                    db.add(inventory_log)
            
        db.commit()
        
        print("Database seeded successfully!")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_database() 