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
    Fetch historical stock data with a clean response format.
    """
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}?apiKey={API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("resultsCount", 0) > 0:
            stock_data = data["results"][0]
            return {
                "ticker": ticker,
                "date": date,
                "open": stock_data["o"],
                "close": stock_data["c"],
                "high": stock_data["h"],
                "low": stock_data["l"],
                "volume": stock_data["v"],
                "trades": stock_data["n"],
            }
        else:
            return {"message": "No data available for this date."}

    return {"error": "Failed to fetch stock data", "status_code": response.status_code}


if __name__ == "__main__":
    logger.info("🚀 Polygon API microservice Started...")
