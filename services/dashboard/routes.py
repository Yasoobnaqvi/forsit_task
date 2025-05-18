from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

import crud, models, schemas
from database import get_db

router = APIRouter()


# Category routes
@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud.create_category(db=db, category=category)


@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/categories/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


# Product routes
@router.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_sku(db, sku=product.sku)
    if db_product:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")
    
    # Verify category exists
    category = crud.get_category(db, category_id=product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return crud.create_product(db=db, product=product)


@router.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    products = crud.get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products


@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


# Inventory routes
@router.post("/inventory/", response_model=schemas.Inventory)
def create_inventory(inventory: schemas.InventoryCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = crud.get_product(db, product_id=inventory.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory for product already exists
    db_inventory = crud.get_inventory(db, product_id=inventory.product_id)
    if db_inventory:
        raise HTTPException(status_code=400, detail="Inventory for this product already exists")
    
    return crud.create_inventory(db=db, inventory=inventory)


@router.get("/inventory/", response_model=List[schemas.Inventory])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    inventory = crud.get_all_inventory(db, skip=skip, limit=limit)
    return inventory


@router.get("/inventory/{product_id}", response_model=schemas.Inventory)
def read_product_inventory(product_id: int, db: Session = Depends(get_db)):
    db_inventory = crud.get_inventory(db, product_id=product_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return db_inventory


@router.put("/inventory/{product_id}", response_model=schemas.Inventory)
def update_product_inventory(
    product_id: int, 
    inventory: schemas.InventoryUpdate, 
    db: Session = Depends(get_db)
):
    # Check if product exists
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory exists
    db_inventory = crud.get_inventory(db, product_id=product_id)
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    
    return crud.update_inventory(db=db, product_id=product_id, inventory_data=inventory)


@router.get("/inventory/low-stock/", response_model=List[schemas.LowStockProduct])
def read_low_stock_products(db: Session = Depends(get_db)):
    result = crud.get_low_stock_products(db)
    
    low_stock_products = []
    for inventory, product_name in result:
        low_stock_products.append({
            "product_id": inventory.product_id,
            "product_name": product_name,
            "current_quantity": inventory.quantity,
            "threshold": inventory.low_stock_threshold
        })
    
    return low_stock_products


@router.get("/inventory/history/{product_id}", response_model=List[schemas.InventoryLog])
def read_inventory_history(product_id: int, limit: int = 10, db: Session = Depends(get_db)):
    # Check if product exists
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inventory_logs = crud.get_inventory_history(db, product_id=product_id, limit=limit)
    return inventory_logs


# Sales routes
@router.post("/sales/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    # Validate all products in the sale
    for item in sale.items:
        product = crud.get_product(db, product_id=item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")
        
        # Check inventory
        inventory = crud.get_inventory(db, product_id=item.product_id)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory for product {item.product_id} not found")
        
        if inventory.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough inventory for product {product.name} (ID: {product.id})")
    
    # Validate total amount
    calculated_total = sum(item.subtotal for item in sale.items)
    if abs(calculated_total - sale.total_amount) > 0.01:  # Allow small rounding differences
        raise HTTPException(status_code=400, detail="Total amount doesn't match sum of item subtotals")
    
    return crud.create_sale(db=db, sale=sale)


@router.get("/sales/", response_model=List[schemas.Sale])
def read_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sales = crud.get_sales(db, skip=skip, limit=limit)
    return sales


@router.get("/sales/{sale_id}", response_model=schemas.Sale)
def read_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = crud.get_sale(db, sale_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale


# Analytics routes
@router.get("/analytics/sales/", response_model=schemas.SalesSummary)
def get_sales_analytics(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    sales_summary = crud.get_sales_summary(db, start_date=start_datetime, end_date=end_datetime)
    return sales_summary


@router.get("/analytics/revenue/{period}", response_model=schemas.RevenueSummary)
def get_revenue_analytics(
    period: str,
    date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    valid_periods = ["day", "week", "month", "year"]
    if period not in valid_periods:
        raise HTTPException(status_code=400, detail=f"Period must be one of: {', '.join(valid_periods)}")
    
    # Use current date if not provided
    if date is None:
        date = datetime.now().date()
    
    current_datetime = datetime.combine(date, datetime.min.time())
    revenue_data = crud.get_revenue_comparison(db, period=period, current_date=current_datetime)
    return revenue_data


@router.post("/analytics/product-sales/", response_model=List)
def get_product_sales_analytics(
    query: schemas.ProductSalesQuery,
    db: Session = Depends(get_db)
):
    if query.start_date > query.end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    sales_data = crud.get_product_sales(db, query=query)
    
    # Transform the result into a more usable format
    result = []
    for sale_item, transaction_date, product_name, category_name in sales_data:
        result.append({
            "product_id": sale_item.product_id,
            "product_name": product_name,
            "category_name": category_name,
            "quantity": sale_item.quantity,
            "unit_price": sale_item.unit_price,
            "subtotal": sale_item.subtotal,
            "transaction_date": transaction_date
        })
    
    return result
