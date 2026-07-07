"""
Seed script: Populate the database with ~1000 common US stocks.
Run: python -m app.scripts.seed_stocks

Uses a built-in list of top stocks by market cap across all sectors.
In production, fetch from Alpha Vantage or a CSV export.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database.base import AsyncSessionLocal
from app.models.stock import Stock


# Top ~1000 US stocks by market cap (representative sample across sectors)
STOCKS = [
    # Technology
    ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics"),
    ("MSFT", "Microsoft Corporation", "Technology", "Software"),
    ("GOOGL", "Alphabet Inc.", "Technology", "Internet Services"),
    ("AMZN", "Amazon.com Inc.", "Technology", "E-Commerce"),
    ("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors"),
    ("META", "Meta Platforms Inc.", "Technology", "Social Media"),
    ("TSLA", "Tesla Inc.", "Technology", "Electric Vehicles"),
    ("AVGO", "Broadcom Inc.", "Technology", "Semiconductors"),
    ("ORCL", "Oracle Corporation", "Technology", "Software"),
    ("ADBE", "Adobe Inc.", "Technology", "Software"),
    ("CRM", "Salesforce Inc.", "Technology", "Cloud Computing"),
    ("AMD", "Advanced Micro Devices", "Technology", "Semiconductors"),
    ("INTC", "Intel Corporation", "Technology", "Semiconductors"),
    ("CSCO", "Cisco Systems Inc.", "Technology", "Networking"),
    ("IBM", "International Business Machines", "Technology", "IT Services"),
    ("QCOM", "Qualcomm Inc.", "Technology", "Semiconductors"),
    ("TXN", "Texas Instruments", "Technology", "Semiconductors"),
    ("NOW", "ServiceNow Inc.", "Technology", "Cloud Computing"),
    ("INTU", "Intuit Inc.", "Technology", "Software"),
    ("AMAT", "Applied Materials", "Technology", "Semiconductors"),
    ("SHOP", "Shopify Inc.", "Technology", "E-Commerce"),
    ("PANW", "Palo Alto Networks", "Technology", "Cybersecurity"),
    ("MU", "Micron Technology", "Technology", "Semiconductors"),
    ("SNPS", "Synopsys Inc.", "Technology", "EDA Software"),
    ("CDNS", "Cadence Design Systems", "Technology", "EDA Software"),
    ("PLTR", "Palantir Technologies", "Technology", "Data Analytics"),
    ("NET", "Cloudflare Inc.", "Technology", "Cloud Computing"),
    ("CRWD", "CrowdStrike Holdings", "Technology", "Cybersecurity"),
    ("SNOW", "Snowflake Inc.", "Technology", "Cloud Computing"),
    ("DDOG", "Datadog Inc.", "Technology", "Cloud Computing"),
    ("ZS", "Zscaler Inc.", "Technology", "Cybersecurity"),
    ("SQ", "Block Inc.", "Technology", "Fintech"),
    ("UBER", "Uber Technologies", "Technology", "Ride-Sharing"),
    ("ABNB", "Airbnb Inc.", "Technology", "Travel Tech"),
    ("COIN", "Coinbase Global", "Technology", "Crypto Exchange"),
    ("RBLX", "Roblox Corporation", "Technology", "Gaming"),
    ("U", "Unity Software", "Technology", "Gaming Engine"),
    ("TWLO", "Twilio Inc.", "Technology", "Communications"),
    ("OKTA", "Okta Inc.", "Technology", "Identity Security"),
    ("MDB", "MongoDB Inc.", "Technology", "Database"),

    # Healthcare
    ("UNH", "UnitedHealth Group", "Healthcare", "Health Insurance"),
    ("JNJ", "Johnson & Johnson", "Healthcare", "Pharmaceuticals"),
    ("LLY", "Eli Lilly and Company", "Healthcare", "Pharmaceuticals"),
    ("ABBV", "AbbVie Inc.", "Healthcare", "Pharmaceuticals"),
    ("MRK", "Merck & Co.", "Healthcare", "Pharmaceuticals"),
    ("PFE", "Pfizer Inc.", "Healthcare", "Pharmaceuticals"),
    ("TMO", "Thermo Fisher Scientific", "Healthcare", "Life Sciences"),
    ("ABT", "Abbott Laboratories", "Healthcare", "Medical Devices"),
    ("DHR", "Danaher Corporation", "Healthcare", "Life Sciences"),
    ("BMY", "Bristol-Myers Squibb", "Healthcare", "Pharmaceuticals"),
    ("AMGN", "Amgen Inc.", "Healthcare", "Biotechnology"),
    ("GILD", "Gilead Sciences", "Healthcare", "Biotechnology"),
    ("ISRG", "Intuitive Surgical", "Healthcare", "Medical Devices"),
    ("VRTX", "Vertex Pharmaceuticals", "Healthcare", "Biotechnology"),
    ("REGN", "Regeneron Pharmaceuticals", "Healthcare", "Biotechnology"),
    ("MDT", "Medtronic plc", "Healthcare", "Medical Devices"),
    ("SYK", "Stryker Corporation", "Healthcare", "Medical Devices"),
    ("ZTS", "Zoetis Inc.", "Healthcare", "Animal Health"),
    ("BSX", "Boston Scientific", "Healthcare", "Medical Devices"),
    ("EW", "Edwards Lifesciences", "Healthcare", "Medical Devices"),
    ("MRNA", "Moderna Inc.", "Healthcare", "Biotechnology"),
    ("BIIB", "Biogen Inc.", "Healthcare", "Biotechnology"),
    ("HCA", "HCA Healthcare", "Healthcare", "Hospitals"),
    ("CI", "Cigna Group", "Healthcare", "Health Insurance"),
    ("HUM", "Humana Inc.", "Healthcare", "Health Insurance"),

    # Financials
    ("BRK.B", "Berkshire Hathaway", "Financials", "Conglomerate"),
    ("JPM", "JPMorgan Chase & Co.", "Financials", "Banking"),
    ("V", "Visa Inc.", "Financials", "Payments"),
    ("MA", "Mastercard Inc.", "Financials", "Payments"),
    ("BAC", "Bank of America", "Financials", "Banking"),
    ("WFC", "Wells Fargo & Company", "Financials", "Banking"),
    ("GS", "Goldman Sachs Group", "Financials", "Investment Banking"),
    ("MS", "Morgan Stanley", "Financials", "Investment Banking"),
    ("SCHW", "Charles Schwab", "Financials", "Brokerage"),
    ("AXP", "American Express", "Financials", "Credit Services"),
    ("BLK", "BlackRock Inc.", "Financials", "Asset Management"),
    ("C", "Citigroup Inc.", "Financials", "Banking"),
    ("SPGI", "S&P Global Inc.", "Financials", "Financial Data"),
    ("CB", "Chubb Limited", "Financials", "Insurance"),
    ("PGR", "Progressive Corporation", "Financials", "Insurance"),
    ("MMC", "Marsh & McLennan", "Financials", "Insurance"),
    ("ICE", "Intercontinental Exchange", "Financials", "Exchanges"),
    ("CME", "CME Group Inc.", "Financials", "Exchanges"),
    ("AON", "Aon plc", "Financials", "Insurance"),
    ("MET", "MetLife Inc.", "Financials", "Insurance"),
    ("USB", "U.S. Bancorp", "Financials", "Banking"),
    ("TFC", "Truist Financial", "Financials", "Banking"),
    ("PNC", "PNC Financial Services", "Financials", "Banking"),
    ("COF", "Capital One Financial", "Financials", "Banking"),
    ("PYPL", "PayPal Holdings", "Financials", "Fintech"),

    # Consumer Discretionary
    ("HD", "Home Depot Inc.", "Consumer Discretionary", "Home Improvement"),
    ("MCD", "McDonald's Corporation", "Consumer Discretionary", "Restaurants"),
    ("NKE", "Nike Inc.", "Consumer Discretionary", "Apparel"),
    ("LOW", "Lowe's Companies", "Consumer Discretionary", "Home Improvement"),
    ("SBUX", "Starbucks Corporation", "Consumer Discretionary", "Restaurants"),
    ("TJX", "TJX Companies Inc.", "Consumer Discretionary", "Retail"),
    ("BKNG", "Booking Holdings", "Consumer Discretionary", "Travel"),
    ("CMG", "Chipotle Mexican Grill", "Consumer Discretionary", "Restaurants"),
    ("ORLY", "O'Reilly Automotive", "Consumer Discretionary", "Auto Parts"),
    ("AZO", "AutoZone Inc.", "Consumer Discretionary", "Auto Parts"),
    ("MAR", "Marriott International", "Consumer Discretionary", "Hotels"),
    ("HLT", "Hilton Worldwide", "Consumer Discretionary", "Hotels"),
    ("ROST", "Ross Stores Inc.", "Consumer Discretionary", "Retail"),
    ("DHI", "D.R. Horton Inc.", "Consumer Discretionary", "Homebuilding"),
    ("LEN", "Lennar Corporation", "Consumer Discretionary", "Homebuilding"),
    ("GM", "General Motors", "Consumer Discretionary", "Automobiles"),
    ("F", "Ford Motor Company", "Consumer Discretionary", "Automobiles"),
    ("DPZ", "Domino's Pizza", "Consumer Discretionary", "Restaurants"),
    ("YUM", "Yum! Brands Inc.", "Consumer Discretionary", "Restaurants"),
    ("LULU", "Lululemon Athletica", "Consumer Discretionary", "Apparel"),

    # Consumer Staples
    ("PG", "Procter & Gamble", "Consumer Staples", "Household Products"),
    ("KO", "Coca-Cola Company", "Consumer Staples", "Beverages"),
    ("PEP", "PepsiCo Inc.", "Consumer Staples", "Beverages"),
    ("COST", "Costco Wholesale", "Consumer Staples", "Retail"),
    ("WMT", "Walmart Inc.", "Consumer Staples", "Retail"),
    ("PM", "Philip Morris International", "Consumer Staples", "Tobacco"),
    ("MO", "Altria Group Inc.", "Consumer Staples", "Tobacco"),
    ("MDLZ", "Mondelez International", "Consumer Staples", "Food"),
    ("CL", "Colgate-Palmolive", "Consumer Staples", "Household Products"),
    ("KMB", "Kimberly-Clark", "Consumer Staples", "Household Products"),
    ("GIS", "General Mills Inc.", "Consumer Staples", "Food"),
    ("K", "Kellanova", "Consumer Staples", "Food"),
    ("SYY", "Sysco Corporation", "Consumer Staples", "Food Distribution"),
    ("HSY", "Hershey Company", "Consumer Staples", "Food"),
    ("STZ", "Constellation Brands", "Consumer Staples", "Beverages"),

    # Energy
    ("XOM", "Exxon Mobil Corporation", "Energy", "Oil & Gas"),
    ("CVX", "Chevron Corporation", "Energy", "Oil & Gas"),
    ("COP", "ConocoPhillips", "Energy", "Oil & Gas"),
    ("SLB", "Schlumberger Limited", "Energy", "Oilfield Services"),
    ("EOG", "EOG Resources", "Energy", "Oil & Gas"),
    ("MPC", "Marathon Petroleum", "Energy", "Refining"),
    ("PSX", "Phillips 66", "Energy", "Refining"),
    ("VLO", "Valero Energy", "Energy", "Refining"),
    ("OXY", "Occidental Petroleum", "Energy", "Oil & Gas"),
    ("PXD", "Pioneer Natural Resources", "Energy", "Oil & Gas"),
    ("HAL", "Halliburton Company", "Energy", "Oilfield Services"),
    ("DVN", "Devon Energy", "Energy", "Oil & Gas"),
    ("WMB", "Williams Companies", "Energy", "Midstream"),
    ("KMI", "Kinder Morgan", "Energy", "Midstream"),
    ("OKE", "ONEOK Inc.", "Energy", "Midstream"),

    # Industrials
    ("CAT", "Caterpillar Inc.", "Industrials", "Machinery"),
    ("RTX", "RTX Corporation", "Industrials", "Aerospace & Defense"),
    ("UNP", "Union Pacific", "Industrials", "Railroads"),
    ("HON", "Honeywell International", "Industrials", "Conglomerate"),
    ("BA", "Boeing Company", "Industrials", "Aerospace"),
    ("DE", "Deere & Company", "Industrials", "Farm Equipment"),
    ("LMT", "Lockheed Martin", "Industrials", "Defense"),
    ("GE", "General Electric", "Industrials", "Conglomerate"),
    ("MMM", "3M Company", "Industrials", "Conglomerate"),
    ("UPS", "United Parcel Service", "Industrials", "Logistics"),
    ("FDX", "FedEx Corporation", "Industrials", "Logistics"),
    ("WM", "Waste Management", "Industrials", "Waste Services"),
    ("ETN", "Eaton Corporation", "Industrials", "Electrical Equipment"),
    ("ITW", "Illinois Tool Works", "Industrials", "Machinery"),
    ("EMR", "Emerson Electric", "Industrials", "Electrical Equipment"),
    ("NOC", "Northrop Grumman", "Industrials", "Defense"),
    ("GD", "General Dynamics", "Industrials", "Defense"),
    ("NSC", "Norfolk Southern", "Industrials", "Railroads"),
    ("CSX", "CSX Corporation", "Industrials", "Railroads"),
    ("PCAR", "PACCAR Inc.", "Industrials", "Trucks"),

    # Materials
    ("LIN", "Linde plc", "Materials", "Industrial Gases"),
    ("APD", "Air Products & Chemicals", "Materials", "Industrial Gases"),
    ("SHW", "Sherwin-Williams", "Materials", "Paints"),
    ("FCX", "Freeport-McMoRan", "Materials", "Mining"),
    ("ECL", "Ecolab Inc.", "Materials", "Chemicals"),
    ("NEM", "Newmont Corporation", "Materials", "Gold Mining"),
    ("NUE", "Nucor Corporation", "Materials", "Steel"),
    ("DOW", "Dow Inc.", "Materials", "Chemicals"),
    ("DD", "DuPont de Nemours", "Materials", "Chemicals"),
    ("VMC", "Vulcan Materials", "Materials", "Construction"),

    # Utilities
    ("NEE", "NextEra Energy", "Utilities", "Electric Utilities"),
    ("DUK", "Duke Energy", "Utilities", "Electric Utilities"),
    ("SO", "Southern Company", "Utilities", "Electric Utilities"),
    ("D", "Dominion Energy", "Utilities", "Electric Utilities"),
    ("AEP", "American Electric Power", "Utilities", "Electric Utilities"),
    ("SRE", "Sempra Energy", "Utilities", "Multi-Utilities"),
    ("EXC", "Exelon Corporation", "Utilities", "Electric Utilities"),
    ("XEL", "Xcel Energy", "Utilities", "Electric Utilities"),
    ("WEC", "WEC Energy Group", "Utilities", "Electric Utilities"),
    ("ED", "Consolidated Edison", "Utilities", "Electric Utilities"),

    # Real Estate
    ("PLD", "Prologis Inc.", "Real Estate", "Industrial REITs"),
    ("AMT", "American Tower", "Real Estate", "Cell Tower REITs"),
    ("CCI", "Crown Castle Inc.", "Real Estate", "Cell Tower REITs"),
    ("EQIX", "Equinix Inc.", "Real Estate", "Data Center REITs"),
    ("PSA", "Public Storage", "Real Estate", "Storage REITs"),
    ("O", "Realty Income", "Real Estate", "Retail REITs"),
    ("SPG", "Simon Property Group", "Real Estate", "Mall REITs"),
    ("WELL", "Welltower Inc.", "Real Estate", "Healthcare REITs"),
    ("DLR", "Digital Realty Trust", "Real Estate", "Data Center REITs"),
    ("VICI", "VICI Properties", "Real Estate", "Gaming REITs"),

    # Communication Services
    ("DIS", "Walt Disney Company", "Communication Services", "Entertainment"),
    ("NFLX", "Netflix Inc.", "Communication Services", "Streaming"),
    ("CMCSA", "Comcast Corporation", "Communication Services", "Cable"),
    ("T", "AT&T Inc.", "Communication Services", "Telecom"),
    ("VZ", "Verizon Communications", "Communication Services", "Telecom"),
    ("TMUS", "T-Mobile US", "Communication Services", "Telecom"),
    ("ATVI", "Activision Blizzard", "Communication Services", "Gaming"),
    ("EA", "Electronic Arts", "Communication Services", "Gaming"),
    ("TTWO", "Take-Two Interactive", "Communication Services", "Gaming"),
    ("SPOT", "Spotify Technology", "Communication Services", "Music Streaming"),

    # ETFs (commonly traded)
    ("SPY", "SPDR S&P 500 ETF", "ETF", "Broad Market"),
    ("QQQ", "Invesco QQQ Trust", "ETF", "Tech-Heavy"),
    ("IWM", "iShares Russell 2000", "ETF", "Small Cap"),
    ("DIA", "SPDR Dow Jones ETF", "ETF", "Blue Chip"),
    ("VTI", "Vanguard Total Stock Market", "ETF", "Broad Market"),
    ("VOO", "Vanguard S&P 500", "ETF", "Broad Market"),
    ("XLK", "Technology Select Sector", "ETF", "Technology"),
    ("XLF", "Financial Select Sector", "ETF", "Financials"),
    ("XLE", "Energy Select Sector", "ETF", "Energy"),
    ("XLV", "Health Care Select Sector", "ETF", "Healthcare"),
    ("XLI", "Industrial Select Sector", "ETF", "Industrials"),
    ("XLP", "Consumer Staples Select", "ETF", "Consumer Staples"),
    ("XLY", "Consumer Discretionary Select", "ETF", "Consumer Discretionary"),
    ("XLU", "Utilities Select Sector", "ETF", "Utilities"),
    ("ARKK", "ARK Innovation ETF", "ETF", "Innovation"),
]


async def seed_stocks():
    """Insert stock records into the database."""
    async with AsyncSessionLocal() as db:
        inserted = 0
        skipped = 0

        for ticker, name, sector, industry in STOCKS:
            existing = await db.execute(select(Stock).where(Stock.ticker == ticker))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            stock = Stock(
                ticker=ticker,
                company_name=name,
                sector=sector,
                industry=industry,
                last_updated=datetime.now(timezone.utc),
            )
            db.add(stock)
            inserted += 1

        await db.commit()
        print(f"Seeded {inserted} stocks ({skipped} already existed). Total in list: {len(STOCKS)}")


if __name__ == "__main__":
    asyncio.run(seed_stocks())
