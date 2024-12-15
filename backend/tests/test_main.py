from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # Import text for raw SQL
import pytest
from app.main import app  # Import your FastAPI app
from app.db import get_db
from app.models import Stock  # Ensure Stock model is available

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_db():
    """Fixture to set up and clean up the test database."""
    db: Session = next(get_db())

    # Verify we are working with the test database
    assert "test" in str(db.bind.url.database), "Not connected to the test database!"

    try:
        # Clean up test-specific records only
        db.execute(text("DELETE FROM allstock WHERE stock_symbol = 'TSLA'"))
        db.commit()
        yield db
    finally:
        # Clean up test-specific records after the test
        db.execute(text("DELETE FROM allstock WHERE stock_symbol = 'TSLA'"))
        db.commit()

def test_get_stocks(setup_test_db):
    # Ensure no stocks exist initially
    db = setup_test_db
    stocks = db.query(Stock).all()
    assert len(stocks) == 0  # Confirm database is empty

    # Add a sample stock for testing GET
    sample_stock = Stock(
        stock_name="Apple",
        stock_symbol="AAPL",
        quantity=10,
        purchase_price=150.0,
        purchase_date="2024-01-01"
    )
    db.add(sample_stock)
    db.commit()

    response = client.get("/api/stocks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    stock = data[0]
    assert stock["stock_name"] == "Apple"
    assert stock["stock_symbol"] == "AAPL"
    assert stock["quantity"] == 10
    assert stock["purchase_price"] == 150.0
    assert stock["purchase_date"] == "2024-01-01"


def test_create_stock(setup_test_db):
    new_stock = {
        "stock_name": "Tesla",
        "stock_symbol": "TSLA",
        "quantity": 5,
        "purchase_price": 650.0,
        "purchase_date": "2024-12-01"
    }
    response = client.post("/api/stocks/", json=new_stock)
    assert response.status_code == 200
    stock = response.json()
    assert stock["stock_name"] == "Tesla"
    assert stock["stock_symbol"] == "TSLA"
    assert stock["quantity"] == 5
    assert stock["purchase_price"] == 650.0
    assert stock["purchase_date"] == "2024-12-01"

    # Verify the stock was added via GET
    response = client.get("/api/stocks/")
    assert response.status_code == 200
    stocks = response.json()
    assert any(s["stock_symbol"] == "TSLA" for s in stocks)

    # Verify directly in the database
    db = setup_test_db
    stock_in_db = db.query(Stock).filter_by(stock_symbol="TSLA").first()
    assert stock_in_db is not None
    assert stock_in_db.stock_name == "Tesla"
    assert stock_in_db.quantity == 5
    assert stock_in_db.purchase_price == 650.0
    assert str(stock_in_db.purchase_date) == "2024-12-01"
