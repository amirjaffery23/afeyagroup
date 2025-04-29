# backend/src/services/hedge_service/hedge_strategy.py

from typing import Dict, List
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models import Stock

def calculate_portfolio_exposure(db: Session) -> Dict[str, float]:
    """
    Calculate the total exposure per stock using stored data in the database.
    """
    stocks = db.query(Stock).all()
    exposure = {}

    for stock in stocks:
        try:
            total_value = stock.quantity * float(stock.purchase_price)
            exposure[stock.stock_symbol] = round(total_value, 2)
        except Exception as e:
            print(f"⚠️ Error calculating exposure for {stock.stock_symbol}: {e}")
            continue

    return exposure

def suggest_hedging_etfs(exposure: Dict[str, float]) -> List[Dict[str, object]]:
    """
    Recommend basic hedging instruments based on total exposure.
    """
    total_value = sum(exposure.values())
    if total_value == 0:
        return []

    recommendations = [
        {
            "symbol": "SH",
            "name": "ProShares Short S&P500",
            "description": "Inverse ETF for hedging S&P 500 exposure",
            "suggested_allocation": round(total_value * 0.2, 2)
        },
        {
            "symbol": "PSQ",
            "name": "ProShares Short QQQ",
            "description": "Inverse ETF for hedging tech-heavy NASDAQ exposure",
            "suggested_allocation": round(total_value * 0.1, 2)
        }
    ]
    return recommendations
