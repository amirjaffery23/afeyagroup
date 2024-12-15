from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stock_router, user_router  # Import both routers

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    return {"message": "Welcome to the Stock Portfolio API"}

# Include the stock-related routes
app.include_router(stock_router, prefix="/api", tags=["stocks"])

# Include the user-related routes
app.include_router(user_router, prefix="/api", tags=["users"])
