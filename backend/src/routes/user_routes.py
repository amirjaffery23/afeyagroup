# backend/src/app/routes/user_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db  # Import the `get_db` function
from models.models import User, Tenant  # Import User and Tenant models
from schemas.user import UserCreate, UserResponse  # Import schemas
from typing import List
from passlib.hash import bcrypt

user_router = APIRouter()

# -------------------------------
# User Endpoints
# -------------------------------

@user_router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Always create a new tenant when a new user registers
    tenant_name = user.name if user.name else user.email.split("@")[0]
    new_tenant = Tenant(name=tenant_name)
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)

    hashed_password = bcrypt.hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        tenant_id=new_tenant.id  # 🔥 Link user to the new tenant
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@user_router.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

