from pydantic import BaseModel, ConfigDict, Field
from typing import Any
from datetime import date, datetime

class StockCreate(BaseModel):
    stock_name: str
    stock_symbol: str
    quantity: int
    purchase_price: float
    purchase_date: str  # Expecting string in ISO 8601 format

    model_config = ConfigDict(from_attributes=True)

class StockResponse(BaseModel):
    id: int
    stock_name: str
    stock_symbol: str
    quantity: int
    purchase_price: float
    purchase_date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")

    @classmethod
    def from_orm(cls, obj: Any) -> "StockResponse":
        """
        Converts ORM objects to StockResponse, ensuring correct date formatting.
        """
        data = obj.__dict__.copy()
        if isinstance(obj.purchase_date, (date, datetime)):
            data["purchase_date"] = obj.purchase_date.isoformat()
        return cls(**data)

    model_config = ConfigDict(from_attributes=True)
