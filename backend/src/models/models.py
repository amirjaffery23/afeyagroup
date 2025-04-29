from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from core.db import Base
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)  # 🔥 Auto-update support

    # Relationships
    users = relationship("User", back_populates="tenant")
    stocks = relationship("Stock", back_populates="tenant")
    historical_stock_data = relationship("HistoricalStockData", back_populates="tenant")


class HistoricalStockData(Base):
    __tablename__ = "historicalstockdata"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    stock_symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=True)
    high_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=True)
    low_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=True)
    close_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=True)
    volume: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="historical_stock_data")


class Stock(Base):
    __tablename__ = "allstock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    stock_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stock_symbol: Mapped[str] = mapped_column(String(10), nullable=False)  # ❌ Removed unique=True globally
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_date: Mapped[Date] = mapped_column(Date, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="stocks")

    # Composite Unique Constraint for (tenant_id, stock_symbol)
    __table_args__ = (
        UniqueConstraint('tenant_id', 'stock_symbol', name='uq_tenant_stock'),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    def hash_password(self, plain_password: str):
        """Hashes a plain text password and assigns it to the password field."""
        self.password = bcrypt.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """Verifies a plain text password against the hashed password."""
        return bcrypt.verify(plain_password, self.password)
