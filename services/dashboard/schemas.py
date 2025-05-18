from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sku: str
    category_id: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class InventoryBase(BaseModel):
    product_id: int
    quantity: int
    low_stock_threshold: int = 10


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None


class Inventory(InventoryBase):
    id: int
    last_restocked: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: int
    sale_id: int

    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    order_id: str
    total_amount: float
    marketplace: str


class SaleCreate(SaleBase):
    items: List[SaleItemCreate]


class Sale(SaleBase):
    id: int
    transaction_date: datetime
    items: List[SaleItem]

    class Config:
        orm_mode = True


class InventoryLogBase(BaseModel):
    product_id: int
    previous_quantity: int
    new_quantity: int
    change_reason: Optional[str] = None


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLog(InventoryLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# Additional schemas for specific queries

class DateRangeQuery(BaseModel):
    start_date: date
    end_date: date


class ProductSalesQuery(DateRangeQuery):
    product_id: Optional[int] = None
    category_id: Optional[int] = None


class SalesSummary(BaseModel):
    total_sales: float
    total_orders: int
    items_sold: int


class RevenueSummary(BaseModel):
    revenue: float
    period: str
    comparison_revenue: Optional[float] = None
    percentage_change: Optional[float] = None


class LowStockProduct(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    threshold: int

    class Config:
        orm_mode = True
