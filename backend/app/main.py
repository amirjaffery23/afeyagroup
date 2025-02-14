from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
import redis
import os
from app.routes import stock_router, user_router
from app.db import get_db

app = FastAPI(
    title="Stock Portfolio API",
    description="A REST API for fetching, storing, and managing stock data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis Configuration
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

@app.on_event("startup")
async def startup_event():
    redis_client = aioredis.Redis(
        host=redis_host, 
        port=redis_port, 
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()

@app.get("/", tags=["General"])
def root():
    return {"message": "Welcome to the Stock Portfolio API"}

def validate_api_key(token: str = Header(..., alias="X-Finnhub-Token")):
    api_key = os.getenv("FINNHUB_API_KEY")
    if token != api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")

@app.get("/api/v1/protected", dependencies=[Depends(RateLimiter(times=30, seconds=1))], tags=["General"])
def protected_endpoint():
    return {"message": "This endpoint is rate-limited and requires authentication"}

app.include_router(stock_router, prefix="/api", tags=["stocks"], dependencies=[Depends(validate_api_key)])
app.include_router(user_router, prefix="/api", tags=["users"])