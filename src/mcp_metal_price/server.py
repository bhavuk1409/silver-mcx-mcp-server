from collections.abc import Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from typing import Any
import json
import logging
import re
import time
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-silver")
app = Server("mcp-silver")

SILVER_URL = "https://groww.in/commodities/futures/mcx_silver"

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_silver_price",
            description="Get silver price data and chart image from Groww.in (MCX India)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

def scrape_silver_data() -> dict:
    """Scrape silver data and capture chart screenshot"""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        logger.info("Loading silver data...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(SILVER_URL)
        
        # Wait for content
        time.sleep(8)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        result = {
            "metal": "Silver",
            "symbol": "XAG",
            "currency": "INR",
            "timestamp": datetime.now().isoformat(),
            "source": "Groww.in (MCX)",
            "url": SILVER_URL,
        }
        
        # Extract main price (appears after "Silver 5 Mar Fut" and before performance metrics)
        current_price_match = re.search(r'Silver \d+ \w+ Fut.*?₹([\d,]+\.\d{2})', page_text, re.DOTALL)
        if current_price_match:
            result["current_price"] = current_price_match.group(1)
            result["price_formatted"] = f"₹{current_price_match.group(1)}"
        
        # Extract Open
        open_match = re.search(r'Open\s+([\d,]+\.\d{2})', page_text)
        if open_match:
            result["open"] = open_match.group(1)
        
        # Extract Previous Close
        prev_close_match = re.search(r'Prev\.\s+Close\s+([\d,]+\.\d{2})', page_text)
        if prev_close_match:
            result["previous_close"] = prev_close_match.group(1)
        
        # Extract 52W Low/High
        low_52w_match = re.search(r'52W Low\s+([\d,]+\.\d{2})', page_text)
        if low_52w_match:
            result["52w_low"] = low_52w_match.group(1)
        
        high_52w_match = re.search(r'52W High\s+([\d,]+\.\d{2})', page_text)
        if high_52w_match:
            result["52w_high"] = high_52w_match.group(1)
        
        # Extract Volume and OI
        volume_match = re.search(r'Volume \(qty\)\s+([\d,]+)', page_text)
        if volume_match:
            result["volume"] = volume_match.group(1)
        
        oi_match = re.search(r'OI \(lots\)\s+([\d,]+)', page_text)
        if oi_match:
            result["oi_lots"] = oi_match.group(1)
        
        # Extract Lot Size
        lot_size_match = re.search(r'Lot Size\s+(\d+)', page_text)
        if lot_size_match:
            result["lot_size"] = lot_size_match.group(1)
        
        # Calculate trend
        if "current_price" in result and "previous_close" in result:
            try:
                current = float(result["current_price"].replace(',', ''))
                prev = float(result["previous_close"].replace(',', ''))
                change = current - prev
                pct_change = (change / prev) * 100
                
                result["change"] = f"{change:+.2f}"
                result["percent_change"] = f"{pct_change:+.2f}%"
                result["trend"] = "UP" if pct_change > 0 else "DOWN"
            except:
                pass
        
        # Capture screenshot
        screenshot = driver.get_screenshot_as_png()
        result["chart_image_base64"] = base64.b64encode(screenshot).decode('utf-8')
        
        driver.quit()
        return result
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if driver:
            driver.quit()
        raise RuntimeError(f"Failed to get silver data: {str(e)}")

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent]:
    if not isinstance(arguments, dict):
        raise RuntimeError("Arguments must be a dictionary")

    if name != "get_silver_price":
        raise RuntimeError(f"Unknown tool: {name}")

    try:
        result = scrape_silver_data()
        
        # Extract chart image
        chart_base64 = result.pop("chart_image_base64", None)
        
        # Return text data and image
        response = [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]
        
        if chart_base64:
            response.append(
                ImageContent(
                    type="image",
                    data=chart_base64,
                    mimeType="image/png"
                )
            )
        
        return response
        
    except Exception as e:
        raise RuntimeError(f"Error: {str(e)}")

async def main():
    from mcp.server.stdio import stdio_server

    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logging.info("Shutting down...")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
