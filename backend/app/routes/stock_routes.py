from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Stock
from app.schemas.stock import StockCreate, StockResponse

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
        raise HTTPException(status_code=400, detail="Stock with this symbol already exists")
    
    # Create and save the new stock
    db_stock = Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    # Use `from_orm` to ensure proper serialization
    return StockResponse.from_orm(db_stock)

@stock_router.get("/stocks/", response_model=List[StockResponse])
def get_stocks(db: Session = Depends(get_db)):
    """
    Retrieve all stock entries.
    """
    stocks = db.query(Stock).all()
    # Use `from_orm` for each stock for proper serialization
    return [StockResponse.from_orm(stock) for stock in stocks]

@stock_router.delete("/stocks/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    """
    Delete a stock by ID.
    """
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    db.delete(stock)
    db.commit()
    return {"message": "Stock deleted successfully"}

