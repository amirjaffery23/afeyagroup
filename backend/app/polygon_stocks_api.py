from fastapi import FastAPI, HTTPException
import httpx
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

app = FastAPI()

@app.get("/stock/{ticker}/historical")
async def get_stock_data(ticker: str, date: str):
    """
    Fetch historical stock data for a given ticker and date.
    Date format: YYYY-MM-DD
    """
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}?apiKey={API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return response.json()
if __name__ == "__main__":
    logger.info("🚀 Polygon API microservice Started...")
