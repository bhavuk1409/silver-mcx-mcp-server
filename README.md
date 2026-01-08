# Silver Price MCP Server

Get silver prices and chart images from Groww.in (MCX India) via MCP.

## Features

- Real-time silver price data
- Chart image included
- Current price, open, previous close
- 52-week high/low
- Volume & Open Interest
- Trend analysis (UP/DOWN)
- No API key needed
- Clean & simple

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Test
```bash
python test.py
```

### MCP Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "silver-price": {
      "command": "python",
      "args": ["-m", "mcp_metal_price"],
      "cwd": "/Users/bhavukagrawal/mcp-metal-price"
    }
  }
}
```

Restart Claude and ask: **"Get the current silver price"**

## API

### Tool: `get_silver_price`

No parameters required.

**Returns:**
- JSON data with price metrics
- PNG chart image (base64 encoded)

**Example Data:**
```json
{
  "metal": "Silver",
  "symbol": "XAG",
  "currency": "INR",
  "current_price": "2,42,798.00",
  "price_formatted": "₹2,42,798.00",
  "open": "2,42,775.00",
  "previous_close": "2,40,277.00",
  "52w_low": "1,09,741.00",
  "52w_high": "2,59,692.00",
  "oi_lots": "12,394",
  "lot_size": "30",
  "change": "+2521.00",
  "percent_change": "+1.05%",
  "trend": "UP"
}
```

Plus chart image showing the price graph.

## Requirements

- Python 3.10+
- Chrome browser
- Dependencies: mcp, selenium, webdriver-manager

## How It Works

1. Opens Groww.in silver page with Selenium
2. Waits for content to load (8 seconds)
3. Extracts price data using regex
4. Captures full-page screenshot
5. Returns JSON data + chart image to Claude

## Notes

- Scraping takes ~8-10 seconds
- Chrome runs headless (no window)
- Image is PNG format, base64 encoded
- Data from MCX India market

## License

MIT
