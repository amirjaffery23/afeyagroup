from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import PolygonStocksSettings

settings = PolygonStocksSettings()

# Use DATABASE_URL directly from settings
DATABASE_URL = settings.DATABASE_URL

print('db_url =', DATABASE_URL)  # Optional: You may remove this in production

# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to provide a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
