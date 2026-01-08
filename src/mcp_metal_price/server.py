from mcp.server.fastmcp import FastMCP
import httpx
import re
from datetime import datetime

# --------------------------------------------------
# MCP SERVER INSTANCE (REQUIRED NAME)
# --------------------------------------------------
mcp = FastMCP("mcp-silver")

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SILVER_URL = "https://groww.in/commodities/futures/mcx_silver"

# --------------------------------------------------
# TOOL: GET SILVER MCX PRICE
# --------------------------------------------------
@mcp.tool()
def get_silver_price() -> dict:
    """
    Fetch latest Silver MCX price from Groww.in
    """

    with httpx.Client(timeout=10) as client:
        response = client.get(SILVER_URL)
        response.raise_for_status()

    html = response.text

    # Extract price (₹xx,xxx.xx)
    price_match = re.search(r'₹([\d,]+\.\d{2})', html)

    return {
        "metal": "Silver",
        "exchange": "MCX",
        "currency": "INR",
        "price": price_match.group(1) if price_match else None,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "Groww.in"
    }
