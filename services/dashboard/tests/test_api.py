import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
import models
import schemas
from typing import Dict, List, Any

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Fixture for database setup and teardown
@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)


# Fixture for seeding test data
@pytest.fixture(scope="function")
def seed_data(test_db):
    db = TestingSessionLocal()

    # Create categories
    categories = [
        {"name": "Electronics", "description": "Electronic devices"},
        {"name": "Clothing", "description": "Apparel items"}
    ]
    
    for category_data in categories:
        db.add(models.Category(**category_data))
    db.commit()
    
    # Create products
    products = [
        {"name": "Smartphone", "description": "Latest model", "price": 999.99, "sku": "ELEC-001", "category_id": 1},
        {"name": "T-shirt", "description": "Cotton t-shirt", "price": 19.99, "sku": "CLOTH-001", "category_id": 2}
    ]
    
    for product_data in products:
        db.add(models.Product(**product_data))
    db.commit()
    
    # Create inventory
    inventories = [
        {"product_id": 1, "quantity": 50, "low_stock_threshold": 10, "last_restocked": datetime.now()},
        {"product_id": 2, "quantity": 100, "low_stock_threshold": 20, "last_restocked": datetime.now()}
    ]
    
    for inventory_data in inventories:
        db.add(models.Inventory(**inventory_data))
    db.commit()
    
    # Create sales
    sale = models.Sale(
        order_id="ORD-12345",
        total_amount=1039.97,
        marketplace="Amazon",
        transaction_date=datetime.now()
    )
    db.add(sale)
    db.flush()
    
    # Create sale items
    sale_items = [
        {"sale_id": 1, "product_id": 1, "quantity": 1, "unit_price": 999.99, "subtotal": 999.99},
        {"sale_id": 1, "product_id": 2, "quantity": 2, "unit_price": 19.99, "subtotal": 39.98}
    ]
    
    for item_data in sale_items:
        db.add(models.SaleItem(**item_data))

    # Create inventory logs
    inventory_logs = [
        {"product_id": 1, "previous_quantity": 51, "new_quantity": 50, "change_reason": "Sale"},
        {"product_id": 2, "previous_quantity": 102, "new_quantity": 100, "change_reason": "Sale"}
    ]
    
    for log_data in inventory_logs:
        db.add(models.InventoryLog(**log_data))
    
    db.commit()
    db.close()


# Test cases for Category API
class TestCategoryAPI:
    def test_get_all_categories(self, seed_data):
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Electronics"
        assert data[1]["name"] == "Clothing"
    
    def test_get_category_by_id(self, seed_data):
        response = client.get("/api/v1/categories/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Electronics"
        assert data["description"] == "Electronic devices"
    
    def test_get_category_not_found(self, seed_data):
        response = client.get("/api/v1/categories/999")
        assert response.status_code == 404
    
    def test_create_category(self, seed_data):
        category_data = {"name": "Furniture", "description": "Home furniture"}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Furniture"
        assert data["id"] == 3
    
    def test_create_duplicate_category(self, seed_data):
        category_data = {"name": "Electronics", "description": "Duplicate category"}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 400


# Test cases for Product API
class TestProductAPI:
    def test_get_all_products(self, seed_data):
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Smartphone"
        assert data[1]["name"] == "T-shirt"
    
    def test_get_products_by_category(self, seed_data):
        response = client.get("/api/v1/products/?category_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Smartphone"
    
    def test_get_product_by_id(self, seed_data):
        response = client.get("/api/v1/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Smartphone"
        assert data["price"] == 999.99
    
    def test_get_product_not_found(self, seed_data):
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404
    
    def test_create_product(self, seed_data):
        product_data = {
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 1499.99,
            "sku": "ELEC-002",
            "category_id": 1
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Laptop"
        assert data["price"] == 1499.99
    
    def test_create_product_with_invalid_category(self, seed_data):
        product_data = {
            "name": "Invalid Product",
            "description": "Product with invalid category",
            "price": 99.99,
            "sku": "INVALID-001",
            "category_id": 999
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 404
    
    def test_create_product_with_duplicate_sku(self, seed_data):
        product_data = {
            "name": "Duplicate SKU",
            "description": "Product with duplicate SKU",
            "price": 99.99,
            "sku": "ELEC-001",
            "category_id": 1
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 400


# Test cases for Inventory API
class TestInventoryAPI:
    def test_get_all_inventory(self, seed_data):
        response = client.get("/api/v1/inventory/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["product_id"] == 1
        assert data[0]["quantity"] == 50
    
    def test_get_inventory_by_product_id(self, seed_data):
        response = client.get("/api/v1/inventory/1")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == 1
        assert data["quantity"] == 50
        assert data["low_stock_threshold"] == 10
    
    def test_get_inventory_not_found(self, seed_data):
        response = client.get("/api/v1/inventory/999")
        assert response.status_code == 404
    
    def test_create_inventory(self, seed_data):
        # First create a new product
        product_data = {
            "name": "New Product",
            "description": "Product for inventory test",
            "price": 199.99,
            "sku": "TEST-001",
            "category_id": 1
        }
        product_response = client.post("/api/v1/products/", json=product_data)
        product_id = product_response.json()["id"]
        
        inventory_data = {
            "product_id": product_id,
            "quantity": 75,
            "low_stock_threshold": 15
        }
        response = client.post("/api/v1/inventory/", json=inventory_data)
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product_id
        assert data["quantity"] == 75
    
    def test_create_inventory_for_nonexistent_product(self, seed_data):
        inventory_data = {
            "product_id": 999,
            "quantity": 75,
            "low_stock_threshold": 15
        }
        response = client.post("/api/v1/inventory/", json=inventory_data)
        assert response.status_code == 404
    
    def test_create_duplicate_inventory(self, seed_data):
        inventory_data = {
            "product_id": 1,
            "quantity": 75,
            "low_stock_threshold": 15
        }
        response = client.post("/api/v1/inventory/", json=inventory_data)
        assert response.status_code == 400
    
    def test_update_inventory(self, seed_data):
        update_data = {
            "quantity": 60,
            "low_stock_threshold": 12
        }
        response = client.put("/api/v1/inventory/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 60
        assert data["low_stock_threshold"] == 12
    
    def test_update_inventory_not_found(self, seed_data):
        update_data = {
            "quantity": 60,
            "low_stock_threshold": 12
        }
        response = client.put("/api/v1/inventory/999", json=update_data)
        assert response.status_code == 404

    def test_get_low_stock_products(self, seed_data):
        # First update inventory to be below threshold
        update_data = {
            "quantity": 5  # Below the threshold of 10
        }
        client.put("/api/v1/inventory/1", json=update_data)
        
        response = client.get("/api/v1/inventory/low-stock/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Check if our product is in the low stock list
        low_stock_product = [p for p in data if p["product_id"] == 1]
        assert len(low_stock_product) == 1
        assert low_stock_product[0]["current_quantity"] == 5
    
    def test_get_inventory_history(self, seed_data):
        response = client.get("/api/v1/inventory/history/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_id"] == 1
        assert data[0]["previous_quantity"] == 51
        assert data[0]["new_quantity"] == 50


# Test cases for Sale API
class TestSaleAPI:
    def test_get_all_sales(self, seed_data):
        response = client.get("/api/v1/sales/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_id"] == "ORD-12345"
        assert data[0]["total_amount"] == 1039.97
    
    def test_get_sale_by_id(self, seed_data):
        response = client.get("/api/v1/sales/1")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD-12345"
        assert data["marketplace"] == "Amazon"
        assert len(data["items"]) == 2
    
    def test_get_sale_not_found(self, seed_data):
        response = client.get("/api/v1/sales/999")
        assert response.status_code == 404
    
    def test_create_sale(self, seed_data):
        sale_data = {
            "order_id": "ORD-67890",
            "total_amount": 1019.98,
            "marketplace": "Walmart",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 999.99,
                    "subtotal": 999.99
                },
                {
                    "product_id": 2,
                    "quantity": 1,
                    "unit_price": 19.99,
                    "subtotal": 19.99
                }
            ]
        }
        response = client.post("/api/v1/sales/", json=sale_data)
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD-67890"
        assert data["total_amount"] == 1019.98
        assert len(data["items"]) == 2
        
        # Check if inventory was updated
        inventory_response = client.get("/api/v1/inventory/1")
        inventory_data = inventory_response.json()
        assert inventory_data["quantity"] == 49  # 50 - 1
    
    def test_create_sale_with_nonexistent_product(self, seed_data):
        sale_data = {
            "order_id": "ORD-INVALID",
            "total_amount": 99.99,
            "marketplace": "Direct",
            "items": [
                {
                    "product_id": 999,  # Non-existent product
                    "quantity": 1,
                    "unit_price": 99.99,
                    "subtotal": 99.99
                }
            ]
        }
        response = client.post("/api/v1/sales/", json=sale_data)
        assert response.status_code == 404
    
    def test_create_sale_with_insufficient_inventory(self, seed_data):
        sale_data = {
            "order_id": "ORD-TOOLARGE",
            "total_amount": 19990.0,
            "marketplace": "Amazon",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 100,  # More than available (50)
                    "unit_price": 999.99,
                    "subtotal": 99999.0
                }
            ]
        }
        response = client.post("/api/v1/sales/", json=sale_data)
        assert response.status_code == 400
    
    def test_create_sale_with_mismatched_total(self, seed_data):
        sale_data = {
            "order_id": "ORD-MISMATCH",
            "total_amount": 500.0,  # Incorrect total (should be 999.99)
            "marketplace": "Direct",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "unit_price": 999.99,
                    "subtotal": 999.99
                }
            ]
        }
        response = client.post("/api/v1/sales/", json=sale_data)
        assert response.status_code == 400


# Test cases for Analytics API
class TestAnalyticsAPI:
    def test_get_sales_analytics(self, seed_data):
        today = date.today()
        params = {
            "start_date": (today - timedelta(days=7)).isoformat(),
            "end_date": today.isoformat()
        }
        response = client.get("/api/v1/analytics/sales/", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "total_sales" in data
        assert "total_orders" in data
        assert "items_sold" in data
    
    def test_get_sales_analytics_invalid_date_range(self, seed_data):
        today = date.today()
        params = {
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=7)).isoformat()  # End date before start date
        }
        response = client.get("/api/v1/analytics/sales/", params=params)
        assert response.status_code == 400
    
    def test_get_revenue_analytics(self, seed_data):
        response = client.get("/api/v1/analytics/revenue/day")
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
        assert "period" in data
        assert data["period"] == "day"
    
    def test_get_revenue_analytics_with_date(self, seed_data):
        today = date.today()
        params = {
            "date": today.isoformat()
        }
        response = client.get("/api/v1/analytics/revenue/day", params=params)
        assert response.status_code == 200
    
    def test_get_revenue_analytics_invalid_period(self, seed_data):
        response = client.get("/api/v1/analytics/revenue/invalid_period")
        assert response.status_code == 400
    
    def test_get_product_sales_analytics(self, seed_data):
        query_data = {
            "start_date": (date.today() - timedelta(days=7)).isoformat(),
            "end_date": date.today().isoformat()
        }
        response = client.post("/api/v1/analytics/product-sales/", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_product_sales_analytics_with_filters(self, seed_data):
        query_data = {
            "start_date": (date.today() - timedelta(days=7)).isoformat(),
            "end_date": date.today().isoformat(),
            "product_id": 1,
            "category_id": 1
        }
        response = client.post("/api/v1/analytics/product-sales/", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_product_sales_analytics_invalid_date_range(self, seed_data):
        query_data = {
            "start_date": date.today().isoformat(),
            "end_date": (date.today() - timedelta(days=7)).isoformat()  # End date before start date
        }
        response = client.post("/api/v1/analytics/product-sales/", json=query_data)
        assert response.status_code == 400


# Integration tests
class TestIntegration:
    def test_complete_workflow(self, seed_data):
        # 1. Create a new category
        category_data = {"name": "Accessories", "description": "Various accessories"}
        category_response = client.post("/api/v1/categories/", json=category_data)
        category_id = category_response.json()["id"]
        
        # 2. Create a new product in that category
        product_data = {
            "name": "Headphones",
            "description": "Wireless headphones",
            "price": 149.99,
            "sku": "ACC-001",
            "category_id": category_id
        }
        product_response = client.post("/api/v1/products/", json=product_data)
        product_id = product_response.json()["id"]
        
        # 3. Create inventory for the product
        inventory_data = {
            "product_id": product_id,
            "quantity": 30,
            "low_stock_threshold": 5
        }
        client.post("/api/v1/inventory/", json=inventory_data)
        
        # 4. Create a sale that includes the new product
        sale_data = {
            "order_id": "ORD-INTEGRATION",
            "total_amount": 149.99,
            "marketplace": "Direct",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "unit_price": 149.99,
                    "subtotal": 149.99
                }
            ]
        }
        sale_response = client.post("/api/v1/sales/", json=sale_data)
        sale_id = sale_response.json()["id"]
        
        # 5. Check if the sale was created
        get_sale_response = client.get(f"/api/v1/sales/{sale_id}")
        assert get_sale_response.status_code == 200
        
        # 6. Check if inventory was updated
        inventory_response = client.get(f"/api/v1/inventory/{product_id}")
        inventory_data = inventory_response.json()
        assert inventory_data["quantity"] == 29  # 30 - 1
        
        # 7. Check inventory history
        history_response = client.get(f"/api/v1/inventory/history/{product_id}")
        history_data = history_response.json()
        assert len(history_data) >= 1
        
        # 8. Check analytics
        today = date.today()
        analytics_params = {
            "start_date": (today - timedelta(days=7)).isoformat(),
            "end_date": today.isoformat()
        }
        analytics_response = client.get("/api/v1/analytics/sales/", params=analytics_params)
        analytics_data = analytics_response.json()
        assert analytics_data["total_orders"] >= 1
    
    def test_error_handling_workflow(self, seed_data):
        # Attempt to create a product with non-existent category
        product_data = {
            "name": "Invalid Product",
            "description": "Product with invalid category",
            "price": 99.99,
            "sku": "INVALID-001",
            "category_id": 999
        }
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 404
        
        # Attempt to create inventory for non-existent product
        inventory_data = {
            "product_id": 999,
            "quantity": 50,
            "low_stock_threshold": 10
        }
        response = client.post("/api/v1/inventory/", json=inventory_data)
        assert response.status_code == 404
        
        # Attempt to create a sale with insufficient inventory
        # First update inventory to a low value
        update_data = {"quantity": 1}
        client.put("/api/v1/inventory/1", json=update_data)
        
        # Then try to create a sale with more quantity than available
        sale_data = {
            "order_id": "ORD-INSUFFICIENT",
            "total_amount": 1999.98,
            "marketplace": "Amazon",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,  # More than available (1)
                    "unit_price": 999.99,
                    "subtotal": 1999.98
                }
            ]
        }
        response = client.post("/api/v1/sales/", json=sale_data)
        assert response.status_code == 400 