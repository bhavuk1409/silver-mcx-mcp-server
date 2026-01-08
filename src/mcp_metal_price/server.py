from mcp.server.fastmcp import FastMCP
from datetime import datetime
import re
import httpx

mcp = FastMCP("mcp-silver")

SILVER_URL = "https://groww.in/commodities/futures/mcx_silver"

@mcp.tool()
def get_silver_price() -> dict:
    """
    Fetch latest Silver MCX price from Groww.in
    """
    try:
        with httpx.Client(timeout=8) as client:
            response = client.get(SILVER_URL)
            response.raise_for_status()

        html = response.text
        price_match = re.search(r'₹([\d,]+\.\d{2})', html)

        return {
            "metal": "Silver",
            "exchange": "MCX",
            "currency": "INR",
            "price": price_match.group(1) if price_match else None,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Groww.in"
        }

    except Exception as e:
        # IMPORTANT: never crash the server
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
