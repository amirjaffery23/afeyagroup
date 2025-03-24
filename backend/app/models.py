from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr

class HistoricalStockData(Base):
    __tablename__ = "historicalstockdata"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(Numeric(10, 2), nullable=True)
    high_price = Column(Numeric(10, 2), nullable=True)
    low_price = Column(Numeric(10, 2), nullable=True)
    close_price = Column(Numeric(10, 2), nullable=True)
    volume = Column(Integer, nullable=True)

class Stock(Base):
    __tablename__ = "allstock"

    id = Column(Integer, primary_key=True, index=True)
    stock_name = Column(String(100), nullable=False)
    stock_symbol = Column(String(10), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    purchase_date = Column(Date, nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def hash_password(self, plain_password: str):
        """Hashes a plain text password and assigns it to the password field."""
        self.password = bcrypt.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """Verifies a plain text password against the hashed password."""
        return bcrypt.verify(plain_password, self.password)
