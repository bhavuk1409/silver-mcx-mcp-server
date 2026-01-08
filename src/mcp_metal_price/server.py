from collections.abc import Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent
from typing import Any
import json
import logging
import re
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-silver")

app = Server("mcp-silver")

SILVER_URL = "https://groww.in/commodities/futures/mcx_silver"

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_silver_price",
            description="Get Silver MCX price data from Groww",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

def scrape_silver_data() -> dict:
    with httpx.Client(timeout=10) as client:
        r = client.get(SILVER_URL)
        r.raise_for_status()

    text = r.text

    result = {
        "metal": "Silver",
        "exchange": "MCX",
        "currency": "INR",
        "timestamp": datetime.now().isoformat(),
        "source": "Groww.in"
    }

    price_match = re.search(r'₹([\d,]+\.\d{2})', text)
    if price_match:
        result["current_price"] = price_match.group(1)

    return result

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    if name != "get_silver_price":
        raise RuntimeError("Unknown tool")

    data = scrape_silver_data()

    return [
        TextContent(
            type="text",
            text=json.dumps(data, indent=2)
        )
    ]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
