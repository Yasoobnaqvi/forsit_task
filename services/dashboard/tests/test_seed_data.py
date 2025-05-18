import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
from models import Category, Product, Inventory, Sale, SaleItem, InventoryLog
import seed_data

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_seed.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the database engine and session
seed_data.engine = engine
seed_data.SessionLocal = TestingSessionLocal


# Fixture for database setup and teardown
@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables
    Base.metadata.drop_all(bind=engine)


def test_seed_database(test_db):
    # Run the seed function
    seed_data.seed_database()
    
    # Open a session to query the data
    db = TestingSessionLocal()
    
    # Test if categories were created
    categories = db.query(Category).all()
    assert len(categories) == 5
    assert "Electronics" in [c.name for c in categories]
    assert "Home & Kitchen" in [c.name for c in categories]
    assert "Clothing" in [c.name for c in categories]
    assert "Books" in [c.name for c in categories]
    assert "Beauty" in [c.name for c in categories]
    
    # Test if products were created (25 products expected)
    products = db.query(Product).all()
    assert len(products) == 25
    
    # Test for specific products in each category
    electronic_products = db.query(Product).filter(Product.category_id == 1).all()
    assert len(electronic_products) == 5
    assert "Smartphone X" in [p.name for p in electronic_products]
    
    home_products = db.query(Product).filter(Product.category_id == 2).all()
    assert len(home_products) == 5
    assert "Coffee Maker" in [p.name for p in home_products]
    
    # Test if inventory was created for each product
    inventory = db.query(Inventory).all()
    assert len(inventory) == 25
    
    # Check specific inventory quantities
    smartphone_inventory = (db.query(Inventory)
                           .join(Product, Inventory.product_id == Product.id)
                           .filter(Product.sku == "ELEC-001")
                           .first())
    assert smartphone_inventory.quantity == 50
    
    # Test if sales were created (500 random sales expected)
    sales = db.query(Sale).all()
    assert len(sales) == 500
    
    # Test if sales have items
    sale_items = db.query(SaleItem).all()
    assert len(sale_items) > 0
    
    # Test if there are inventory logs
    inventory_logs = db.query(InventoryLog).all()
    assert len(inventory_logs) > 0
    
    # Run the seed function again - should exit early and not create duplicate data
    seed_data.seed_database()
    
    # Check that no new categories were added
    new_categories_count = db.query(Category).count()
    assert new_categories_count == 5  # Still just the original 5
    
    db.close() 