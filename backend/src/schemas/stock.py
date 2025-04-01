from typing import Any, Optional
from datetime import date
import logging
from pydantic import BaseModel, ConfigDict, constr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Model for creating a new stock entry
class StockCreate(BaseModel):
    stock_name: constr(min_length=1, max_length=255)
    stock_symbol: constr(min_length=1, max_length=10)
    quantity: int
    purchase_price: float
    purchase_date: date  # Uses date type

    # Pydantic v2 config (no validate_assignment for performance)
    model_config = ConfigDict()

# ✅ New Model: Stock Update (Allows Partial Updates)
class StockUpdate(BaseModel):
    stock_name: Optional[constr(min_length=1, max_length=255)] = None
    quantity: Optional[int] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[date] = None  # Allows date updates but remains optional

    model_config = ConfigDict()
    
# Model for responding with stock details
class StockResponse(BaseModel):
    id: int
    stock_name: str
    stock_symbol: str
    quantity: int
    purchase_price: float
    purchase_date: date  # Returns a date object in the response

    # Enable ORM mapping
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj: Any) -> "StockResponse":
        """
        Converts ORM objects to StockResponse using Pydantic's model_validate.
        """
        try:
            response = cls.model_validate(obj)
            logger.debug(f"Final StockResponse object: {response}")
            return response
        except Exception as e:
            logger.error(f"Error converting ORM object: {e}")
            raise ValueError(f"Invalid ORM object: {e}")
