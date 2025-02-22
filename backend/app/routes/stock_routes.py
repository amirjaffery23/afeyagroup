from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Stock
from app.schemas.stock import StockCreate, StockUpdate, StockResponse

stock_router = APIRouter()

# Stock Endpoints
@stock_router.post("/stocks/", response_model=StockResponse)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    """
    Create a new stock entry.
    """
    # Check if the stock already exists by its symbol
    existing_stock = db.query(Stock).filter(Stock.stock_symbol == stock.stock_symbol).first()
    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock already exists")
    
    # Create new stock entry
    new_stock = Stock(**stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

@stock_router.get("/stocks/", response_model=List[StockResponse])
def read_stocks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a list of stocks.
    """
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks

@stock_router.get("/stocks/{stock_id}", response_model=StockResponse)
def read_stock(stock_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a stock by its ID.
    """
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@stock_router.put("/stocks/{stock_symbol}", response_model=StockResponse)
def update_stock(stock_symbol: str, stock_data: StockUpdate, db: Session = Depends(get_db)):
    """
    Update a stock entry using the stock symbol.
    """
    if not stock_symbol:
        raise HTTPException(status_code=400, detail="Stock symbol is required")

    existing_stock = db.query(Stock).filter(Stock.stock_symbol == stock_symbol).first()
    if not existing_stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Convert `purchase_date` from string to date if necessary
    if stock_data.purchase_date and isinstance(stock_data.purchase_date, str):
        try:
            stock_data.purchase_date = datetime.strptime(stock_data.purchase_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # ✅ Update only provided fields
    for key, value in stock_data.dict(exclude_unset=True).items():
        setattr(existing_stock, key, value)

    db.commit()
    db.refresh(existing_stock)
    return existing_stock


@stock_router.delete("/stocks/{stock_symbol}", response_model=StockResponse)
def delete_stock(stock_symbol: str, db: Session = Depends(get_db)):
    """
    Delete a stock entry using the stock symbol.
    """
    stock = db.query(Stock).filter(Stock.stock_symbol == stock_symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    db.delete(stock)
    db.commit()
    return stock
