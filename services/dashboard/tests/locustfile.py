import json
import random
from datetime import date, timedelta
from locust import HttpUser, task, between


class EcommerceAdminUser(HttpUser):
    wait_time = between(1, 3)  # Wait between 1 and 3 seconds between tasks
    
    # Simulate common API endpoints that would be frequently accessed
    
    @task(5)  # Higher weight for more common operations
    def get_dashboard_data(self):
        # Get today's and last week's date for analytics
        today = date.today()
        last_week = today - timedelta(days=7)
        
        # Get today's sales summary
        self.client.get(
            f"/api/v1/analytics/sales/?start_date={today.isoformat()}&end_date={today.isoformat()}"
        )
        
        # Get weekly revenue comparison
        self.client.get(f"/api/v1/analytics/revenue/week")
        
        # Get low stock products
        self.client.get("/api/v1/inventory/low-stock/")
    
    @task(3)
    def browse_products(self):
        # Get all categories
        with self.client.get("/api/v1/categories/") as response:
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    # Randomly select a category to view its products
                    category = random.choice(categories)
                    self.client.get(f"/api/v1/products/?category_id={category['id']}")
        
        # Get all products (paginated)
        self.client.get("/api/v1/products/?skip=0&limit=20")
    
    @task(2)
    def check_inventory(self):
        # Get all inventory
        with self.client.get("/api/v1/inventory/") as response:
            if response.status_code == 200:
                inventory_items = response.json()
                if inventory_items:
                    # Randomly select an inventory item to view details
                    inventory = random.choice(inventory_items)
                    self.client.get(f"/api/v1/inventory/{inventory['product_id']}")
    
    @task(1)
    def create_sale(self):
        # First get some products to create a sale
        with self.client.get("/api/v1/products/?limit=5") as response:
            if response.status_code == 200:
                products = response.json()
                if products:
                    # Create a sale with 1-3 random products
                    num_items = random.randint(1, min(3, len(products)))
                    selected_products = random.sample(products, num_items)
                    
                    # Calculate total and create sale items
                    total_amount = 0
                    items = []
                    
                    for product in selected_products:
                        quantity = random.randint(1, 3)
                        unit_price = product["price"]
                        subtotal = unit_price * quantity
                        
                        items.append({
                            "product_id": product["id"],
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "subtotal": subtotal
                        })
                        
                        total_amount += subtotal
                    
                    # Create the sale
                    sale_data = {
                        "order_id": f"ORD-LOAD-{random.randint(10000, 99999)}",
                        "total_amount": total_amount,
                        "marketplace": random.choice(["Amazon", "Walmart", "Direct"]),
                        "items": items
                    }
                    
                    self.client.post("/api/v1/sales/", json=sale_data)
    
    @task(1)
    def update_inventory(self):
        # Get all inventory
        with self.client.get("/api/v1/inventory/") as response:
            if response.status_code == 200:
                inventory_items = response.json()
                if inventory_items:
                    # Randomly select an inventory item to update
                    inventory = random.choice(inventory_items)
                    
                    # Update with a random quantity (±10 of current quantity)
                    current_quantity = inventory["quantity"]
                    new_quantity = max(0, current_quantity + random.randint(-10, 10))
                    
                    update_data = {
                        "quantity": new_quantity
                    }
                    
                    self.client.put(f"/api/v1/inventory/{inventory['product_id']}", json=update_data)
    
    @task(1)
    def view_product_analytics(self):
        # Get product sales analytics for the past 30 days
        today = date.today()
        month_ago = today - timedelta(days=30)
        
        query_data = {
            "start_date": month_ago.isoformat(),
            "end_date": today.isoformat()
        }
        
        # Optionally add product or category filters
        if random.choice([True, False]):
            # Get a random product ID between 1 and 25
            query_data["product_id"] = random.randint(1, 25)
        
        if random.choice([True, False]):
            # Get a random category ID between 1 and 5
            query_data["category_id"] = random.randint(1, 5)
        
        self.client.post("/api/v1/analytics/product-sales/", json=query_data) 