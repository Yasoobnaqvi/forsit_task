from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_, desc
from datetime import datetime, timedelta
import models, schemas
from typing import List, Optional, Dict, Any


# Category CRUD operations
def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Product CRUD operations
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str):
    return db.query(models.Product).filter(models.Product.sku == sku).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None):
    query = db.query(models.Product)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_data: Dict[str, Any]):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


# Inventory CRUD operations
def get_inventory(db: Session, product_id: int):
    return db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()


def get_all_inventory(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Inventory).offset(skip).limit(limit).all()


def create_inventory(db: Session, inventory: schemas.InventoryCreate):
    db_inventory = models.Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory(db: Session, product_id: int, inventory_data: schemas.InventoryUpdate):
    db_inventory = db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()
    
    if db_inventory:
        update_data = inventory_data.dict(exclude_unset=True)
        
        # Log inventory change if quantity is being updated
        if 'quantity' in update_data and update_data['quantity'] != db_inventory.quantity:
            inventory_log = models.InventoryLog(
                product_id=product_id,
                previous_quantity=db_inventory.quantity,
                new_quantity=update_data['quantity'],
                change_reason="Manual update"
            )
            db.add(inventory_log)
            
            # Update last_restocked if increasing inventory
            if update_data['quantity'] > db_inventory.quantity:
                db_inventory.last_restocked = datetime.now()
        
        # Update inventory fields
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
            
        db.commit()
        db.refresh(db_inventory)
    
    return db_inventory


def get_low_stock_products(db: Session):
    return db.query(
        models.Inventory, 
        models.Product.name.label("product_name")
    ).join(
        models.Product, 
        models.Inventory.product_id == models.Product.id
    ).filter(
        models.Inventory.quantity <= models.Inventory.low_stock_threshold
    ).all()


# Sale CRUD operations
def create_sale(db: Session, sale: schemas.SaleCreate):
    # Create sale record
    db_sale = models.Sale(
        order_id=sale.order_id,
        total_amount=sale.total_amount,
        marketplace=sale.marketplace
    )
    db.add(db_sale)
    db.flush()  # Get the sale ID without committing
    
    # Create sale items
    for item in sale.items:
        db_sale_item = models.SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal
        )
        db.add(db_sale_item)
        
        # Update inventory
        db_inventory = get_inventory(db, item.product_id)
        if db_inventory:
            new_quantity = max(0, db_inventory.quantity - item.quantity)
            inventory_log = models.InventoryLog(
                product_id=item.product_id,
                previous_quantity=db_inventory.quantity,
                new_quantity=new_quantity,
                change_reason=f"Sale - Order ID: {sale.order_id}"
            )
            db.add(inventory_log)
            
            db_inventory.quantity = new_quantity
            db.add(db_inventory)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


def get_sale(db: Session, sale_id: int):
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()


def get_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sale).order_by(desc(models.Sale.transaction_date)).offset(skip).limit(limit).all()


# Analytics operations
def get_sales_by_date_range(db: Session, start_date: datetime, end_date: datetime):
    return db.query(models.Sale).filter(
        models.Sale.transaction_date >= start_date,
        models.Sale.transaction_date <= end_date
    ).all()


def get_product_sales(db: Session, query: schemas.ProductSalesQuery):
    start_date = datetime.combine(query.start_date, datetime.min.time())
    end_date = datetime.combine(query.end_date, datetime.max.time())
    
    sale_items_query = db.query(
        models.SaleItem,
        models.Sale.transaction_date,
        models.Product.name.label("product_name"),
        models.Category.name.label("category_name")
    ).join(
        models.Sale, models.SaleItem.sale_id == models.Sale.id
    ).join(
        models.Product, models.SaleItem.product_id == models.Product.id
    ).join(
        models.Category, models.Product.category_id == models.Category.id
    ).filter(
        models.Sale.transaction_date >= start_date,
        models.Sale.transaction_date <= end_date
    )
    
    if query.product_id:
        sale_items_query = sale_items_query.filter(models.SaleItem.product_id == query.product_id)
    
    if query.category_id:
        sale_items_query = sale_items_query.filter(models.Product.category_id == query.category_id)
    
    return sale_items_query.all()


def get_sales_summary(db: Session, start_date: datetime, end_date: datetime):
    sales_data = db.query(
        func.sum(models.Sale.total_amount).label("total_sales"),
        func.count(models.Sale.id).label("total_orders")
    ).filter(
        models.Sale.transaction_date >= start_date,
        models.Sale.transaction_date <= end_date
    ).first()
    
    items_count = db.query(
        func.sum(models.SaleItem.quantity).label("items_sold")
    ).join(
        models.Sale, models.SaleItem.sale_id == models.Sale.id
    ).filter(
        models.Sale.transaction_date >= start_date,
        models.Sale.transaction_date <= end_date
    ).scalar()
    
    if sales_data:
        return {
            "total_sales": sales_data.total_sales or 0,
            "total_orders": sales_data.total_orders or 0,
            "items_sold": items_count or 0
        }
    return {"total_sales": 0, "total_orders": 0, "items_sold": 0}


def get_revenue_by_period(db: Session, period: str, date: datetime):
    """
    Get revenue for a specific period (day, week, month, year)
    """
    if period == "day":
        start_date = datetime.combine(date.date(), datetime.min.time())
        end_date = datetime.combine(date.date(), datetime.max.time())
    elif period == "week":
        # Start from Monday of the week
        start_of_week = date.date() - timedelta(days=date.weekday())
        start_date = datetime.combine(start_of_week, datetime.min.time())
        end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
    elif period == "month":
        start_date = datetime(date.year, date.month, 1)
        if date.month == 12:
            end_date = datetime(date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(date.year, date.month + 1, 1) - timedelta(seconds=1)
    elif period == "year":
        start_date = datetime(date.year, 1, 1)
        end_date = datetime(date.year, 12, 31, 23, 59, 59)
    else:
        raise ValueError("Invalid period. Must be one of: day, week, month, year")
    
    revenue = db.query(
        func.sum(models.Sale.total_amount)
    ).filter(
        models.Sale.transaction_date >= start_date,
        models.Sale.transaction_date <= end_date
    ).scalar()
    
    return revenue or 0


def get_revenue_comparison(db: Session, period: str, current_date: datetime):
    """
    Compare revenue between current period and previous period
    """
    current_revenue = get_revenue_by_period(db, period, current_date)
    
    # Calculate previous period
    if period == "day":
        previous_date = current_date - timedelta(days=1)
    elif period == "week":
        previous_date = current_date - timedelta(weeks=1)
    elif period == "month":
        if current_date.month == 1:
            previous_date = datetime(current_date.year - 1, 12, current_date.day)
        else:
            previous_date = datetime(current_date.year, current_date.month - 1, current_date.day)
    elif period == "year":
        previous_date = datetime(current_date.year - 1, current_date.month, current_date.day)
    else:
        raise ValueError("Invalid period. Must be one of: day, week, month, year")
    
    previous_revenue = get_revenue_by_period(db, period, previous_date)
    
    # Calculate percentage change
    percentage_change = None
    if previous_revenue > 0:
        percentage_change = ((current_revenue - previous_revenue) / previous_revenue) * 100
    
    return {
        "revenue": current_revenue,
        "period": period,
        "comparison_revenue": previous_revenue,
        "percentage_change": percentage_change
    }


def get_inventory_history(db: Session, product_id: int, limit: int = 10):
    return db.query(models.InventoryLog).filter(
        models.InventoryLog.product_id == product_id
    ).order_by(desc(models.InventoryLog.timestamp)).limit(limit).all()
