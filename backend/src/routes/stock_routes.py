from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from core.db import get_db
from models.models import Stock, User
from schemas.stock import StockCreate, StockUpdate, StockResponse
from core.auth import get_current_user  # ⬅️ Dependency to get logged-in user
from datetime import datetime

stock_router = APIRouter()

# -------------------------------
# Stock Endpoints
# -------------------------------

@stock_router.post("/stocks/", response_model=StockResponse)
def create_stock(stock: StockCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new stock entry for the current user's tenant.
    """
    existing_stock = db.query(Stock).filter(
        Stock.stock_symbol == stock.stock_symbol,
        Stock.tenant_id == current_user.tenant_id  # 🔥 Only check inside this tenant
    ).first()
    
    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock already exists for your tenant")
    
    new_stock = Stock(
        tenant_id=current_user.tenant_id,  # 🔥 Always tie stock to user's tenant
        stock_name=stock.stock_name,
        stock_symbol=stock.stock_symbol,
        quantity=stock.quantity,
        purchase_price=stock.purchase_price,
        purchase_date=stock.purchase_date,
    )
    
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

@stock_router.get("/stocks/", response_model=List[StockResponse])
def read_stocks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of stocks for the current user's tenant.
    """
    stocks = db.query(Stock).filter(
        Stock.tenant_id == current_user.tenant_id  # 🔥 Filter by tenant
    ).offset(skip).limit(limit).all()
    return stocks

@stock_router.get("/stocks/{stock_id}", response_model=StockResponse)
def read_stock(stock_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a stock by its ID for the current user's tenant.
    """
    stock = db.query(Stock).filter(
        Stock.id == stock_id,
        Stock.tenant_id == current_user.tenant_id
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@stock_router.get("/stocks/symbol/{stock_symbol}", response_model=StockResponse)
def read_stock_by_symbol(stock_symbol: str, date: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a stock by its symbol and date for the current user's tenant.
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    stock = db.query(Stock).filter(
        Stock.stock_symbol == stock_symbol,
        Stock.purchase_date == date_obj,
        Stock.tenant_id == current_user.tenant_id
    ).first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@stock_router.put("/stocks/{stock_symbol}", response_model=StockResponse)
def update_stock(stock_symbol: str, stock_data: StockUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a stock entry using the stock symbol for the current user's tenant.
    """
    existing_stock = db.query(Stock).filter(
        Stock.stock_symbol == stock_symbol,
        Stock.tenant_id == current_user.tenant_id
    ).first()
    
    if not existing_stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    if stock_data.purchase_date and isinstance(stock_data.purchase_date, str):
        try:
            stock_data.purchase_date = datetime.strptime(stock_data.purchase_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    for key, value in stock_data.dict(exclude_unset=True).items():
        setattr(existing_stock, key, value)

    db.commit()
    db.refresh(existing_stock)
    return existing_stock

@stock_router.delete("/stocks/{stock_symbol}", response_model=StockResponse)
def delete_stock(stock_symbol: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a stock entry using the stock symbol for the current user's tenant.
    """
    stock = db.query(Stock).filter(
        Stock.stock_symbol == stock_symbol,
        Stock.tenant_id == current_user.tenant_id
    ).first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    db.delete(stock)
    db.commit()
    return stock
