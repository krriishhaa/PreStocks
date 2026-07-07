ASSET_UNIVERSE = {
    "stocks": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "PLTR", "TSLA"],
    "etfs": ["SPY", "QQQ", "IWM", "DIA", "VTI"],
    "indexes": ["^GSPC", "^IXIC", "^DJI", "^VIX"],
    "crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "treasuries": ["^TNX", "^FVX", "^TYX"],
    "commodities": ["CL=F", "GC=F", "SI=F", "NG=F"],
    # Option underlyings; individual contracts are discovered dynamically.
    "options_underlyings": ["AAPL", "NVDA", "SPY", "TSLA"],
}


ECONOMIC_SERIES = {
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "FEDFUNDS": "Fed Funds Effective Rate",
    "GDP": "Gross Domestic Product",
}

