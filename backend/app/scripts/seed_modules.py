"""
Seed script: Populate learning modules with full quiz questions.
Run: python -m app.scripts.seed_modules
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.database.base import AsyncSessionLocal
from app.models.learning import LearningModule


MODULES = [
    # ─── BEGINNER TIER ────────────────────────────────────────────
    {
        "title": "Stocks 101",
        "description": "What is a stock, why do prices move, and how the market works.",
        "required_tier": "beginner",
        "estimated_duration_minutes": 8,
        "content_url": None,
        "quiz_questions": [
            {"question": "What does owning a stock represent?", "options": ["A loan to the company", "Partial ownership of the company", "A fixed-income bond", "A futures contract"], "correct_index": 1},
            {"question": "What primarily drives stock prices?", "options": ["Government policy alone", "Company logo design", "Supply and demand", "Time of day"], "correct_index": 2},
            {"question": "What is a stock exchange?", "options": ["A place to trade currencies only", "A marketplace where stocks are bought and sold", "A bank", "A government office"], "correct_index": 1},
            {"question": "If a company issues 1 million shares and you own 10,000, what percentage do you own?", "options": ["0.1%", "1%", "10%", "0.01%"], "correct_index": 1},
            {"question": "Why do investors diversify?", "options": ["To increase fees", "To reduce risk from any single stock", "It's required by law", "To make accounting harder"], "correct_index": 1},
        ],
    },
    {
        "title": "Understanding P/E Ratios",
        "description": "Valuation basics — what P/E means, how to use it, and common pitfalls.",
        "required_tier": "beginner",
        "estimated_duration_minutes": 6,
        "content_url": None,
        "quiz_questions": [
            {"question": "What does P/E ratio stand for?", "options": ["Price to Equity", "Price to Earnings", "Profit to Expense", "Portfolio to Equity"], "correct_index": 1},
            {"question": "A company's stock is $50 and EPS is $5. What is the P/E ratio?", "options": ["5", "10", "25", "50"], "correct_index": 1},
            {"question": "A stock with P/E of 50 vs. industry average of 20 suggests:", "options": ["It's definitely overvalued", "Market expects higher future growth", "The company is unprofitable", "Nothing meaningful"], "correct_index": 1},
            {"question": "When is P/E ratio most useful?", "options": ["Comparing across all industries", "Comparing within the same industry", "For cryptocurrency", "For real estate"], "correct_index": 1},
            {"question": "A negative P/E ratio means:", "options": ["The stock is cheap", "The company is not profitable", "The stock will go up", "It's a good buy"], "correct_index": 1},
        ],
    },
    {
        "title": "Risk vs. Reward",
        "description": "How to think about risk, position sizing, and why higher returns come with higher risk.",
        "required_tier": "beginner",
        "estimated_duration_minutes": 7,
        "content_url": None,
        "quiz_questions": [
            {"question": "Generally, higher potential returns come with:", "options": ["Lower risk", "Higher risk", "No risk", "Government guarantees"], "correct_index": 1},
            {"question": "What is 'position sizing'?", "options": ["The physical size of your monitor", "How much of your portfolio you put into one investment", "The number of stocks in existence", "Your account balance"], "correct_index": 1},
            {"question": "If you invest 80% of your portfolio in one stock, you have:", "options": ["Good diversification", "High concentration risk", "Low risk", "A balanced portfolio"], "correct_index": 1},
            {"question": "A 'stop-loss' order is designed to:", "options": ["Guarantee profits", "Limit potential losses", "Increase returns", "Avoid taxes"], "correct_index": 1},
            {"question": "Which investment typically has the LOWEST risk?", "options": ["Penny stocks", "Cryptocurrency", "US Treasury bonds", "Startup equity"], "correct_index": 2},
        ],
    },
    {
        "title": "Reading Financial Statements",
        "description": "Balance sheet, income statement, and cash flow basics every investor should know.",
        "required_tier": "beginner",
        "estimated_duration_minutes": 10,
        "content_url": None,
        "quiz_questions": [
            {"question": "Which financial statement shows a company's assets and liabilities?", "options": ["Income statement", "Balance sheet", "Cash flow statement", "Tax return"], "correct_index": 1},
            {"question": "Revenue minus expenses equals:", "options": ["Assets", "Liabilities", "Net income (profit)", "Market cap"], "correct_index": 2},
            {"question": "A company with more liabilities than assets is:", "options": ["Very profitable", "In a strong position", "Potentially insolvent", "Guaranteed to grow"], "correct_index": 2},
            {"question": "Free cash flow tells you:", "options": ["How much cash the company generated after capital expenditures", "The stock price", "How many employees it has", "Its market cap"], "correct_index": 0},
            {"question": "Debt-to-equity ratio measures:", "options": ["Stock price vs. book value", "How much a company relies on debt vs. shareholder equity", "Dividend payments", "Revenue growth"], "correct_index": 1},
        ],
    },
    {
        "title": "Diversification",
        "description": "Why and how to spread your investments across different assets, sectors, and geographies.",
        "required_tier": "beginner",
        "estimated_duration_minutes": 6,
        "content_url": None,
        "quiz_questions": [
            {"question": "What is diversification?", "options": ["Buying only tech stocks", "Spreading investments across different assets to reduce risk", "Investing all money in one stock", "Day trading"], "correct_index": 1},
            {"question": "Which portfolio is MORE diversified?", "options": ["5 tech stocks", "1 stock from each of 5 different sectors", "All money in an S&P 500 ETF", "Both B and C are well-diversified"], "correct_index": 3},
            {"question": "Correlation in investing means:", "options": ["Stocks always go up together", "How closely two investments move relative to each other", "The stock market is rigged", "Nothing important"], "correct_index": 1},
            {"question": "Why might someone own bonds AND stocks?", "options": ["Bonds often go up when stocks go down, reducing overall volatility", "It's required by law", "Bonds always beat stocks", "No good reason"], "correct_index": 0},
            {"question": "If your portfolio is 70% in one sector, you should:", "options": ["Add more to that sector", "Consider rebalancing into other sectors", "Sell everything", "Ignore it"], "correct_index": 1},
        ],
    },

    # ─── INTERMEDIATE TIER ────────────────────────────────────────
    {
        "title": "Technical Analysis Intro",
        "description": "Charts, trends, support/resistance, and common indicators.",
        "required_tier": "intermediate",
        "estimated_duration_minutes": 12,
        "content_url": None,
        "quiz_questions": [
            {"question": "What does 'support level' mean?", "options": ["A price level where buying pressure prevents further decline", "The highest price ever", "A government price floor", "Nothing useful"], "correct_index": 0},
            {"question": "RSI above 70 typically suggests:", "options": ["Oversold conditions", "Overbought conditions", "Fair value", "No signal"], "correct_index": 1},
            {"question": "A 'moving average crossover' signal occurs when:", "options": ["Volume spikes", "A shorter-term MA crosses a longer-term MA", "The stock hits all-time high", "Earnings are reported"], "correct_index": 1},
            {"question": "Which chart type shows open, high, low, and close?", "options": ["Line chart", "Candlestick chart", "Pie chart", "Bar chart (standard)"], "correct_index": 1},
        ],
    },
    {
        "title": "Earnings & Volatility",
        "description": "What happens around earnings reports and how to prepare.",
        "required_tier": "intermediate",
        "estimated_duration_minutes": 9,
        "content_url": None,
        "quiz_questions": [
            {"question": "What typically happens to a stock's implied volatility before earnings?", "options": ["It decreases", "It increases", "It stays the same", "It becomes zero"], "correct_index": 1},
            {"question": "'Earnings beat' means:", "options": ["The stock went up", "Actual EPS exceeded analyst estimates", "The CEO was fired", "Revenue declined"], "correct_index": 1},
            {"question": "A stock can drop after beating earnings because:", "options": ["Impossible — beats always mean stock goes up", "The beat was already priced in or guidance was weak", "The market is broken", "Earnings don't matter"], "correct_index": 1},
        ],
    },
    {
        "title": "Insider Trading Signals",
        "description": "How to read insider buy/sell data from SEC filings.",
        "required_tier": "intermediate",
        "estimated_duration_minutes": 8,
        "content_url": None,
        "quiz_questions": [
            {"question": "Form 4 filed with the SEC reports:", "options": ["Quarterly earnings", "Insider stock transactions", "Company bankruptcy", "New product launches"], "correct_index": 1},
            {"question": "Cluster buying by multiple insiders is often:", "options": ["Illegal", "A positive signal about company outlook", "Meaningless", "Required by law"], "correct_index": 1},
            {"question": "Why might insiders sell for non-bearish reasons?", "options": ["Tax planning, diversification, or personal liquidity needs", "They never have good reasons", "It's always a red flag", "The company forces them"], "correct_index": 0},
        ],
    },
    {
        "title": "Sector Rotation",
        "description": "How money flows between sectors during economic cycles.",
        "required_tier": "intermediate",
        "estimated_duration_minutes": 10,
        "content_url": None,
        "quiz_questions": [
            {"question": "During economic expansion, which sectors typically outperform?", "options": ["Utilities and Consumer Staples", "Technology and Consumer Discretionary", "Only bonds", "None — all sectors move equally"], "correct_index": 1},
            {"question": "Defensive sectors include:", "options": ["Technology and crypto", "Utilities, Healthcare, Consumer Staples", "Only government bonds", "Real estate exclusively"], "correct_index": 1},
            {"question": "Sector rotation strategy involves:", "options": ["Never changing your portfolio", "Shifting allocation based on economic cycle phase", "Only buying one sector", "Day trading within a sector"], "correct_index": 1},
        ],
    },
    {
        "title": "Options Explained",
        "description": "Theory only — calls, puts, and basic options concepts.",
        "required_tier": "intermediate",
        "estimated_duration_minutes": 11,
        "content_url": None,
        "quiz_questions": [
            {"question": "A call option gives the holder the right to:", "options": ["Sell at a set price", "Buy at a set price", "Short the stock", "Lend money"], "correct_index": 1},
            {"question": "The 'strike price' is:", "options": ["The current market price", "The price at which the option can be exercised", "The premium paid", "The expiration date"], "correct_index": 1},
            {"question": "If you buy a put option, you profit when:", "options": ["The stock goes up", "The stock goes down below the strike price", "Nothing happens", "The stock stays flat"], "correct_index": 1},
        ],
    },

    # ─── ADVANCED TIER ────────────────────────────────────────────
    {
        "title": "Options Trading Deep Dive",
        "description": "Strategies, Greeks, and execution for advanced traders.",
        "required_tier": "advanced",
        "estimated_duration_minutes": 15,
        "content_url": None,
        "quiz_questions": [
            {"question": "Delta measures:", "options": ["Time decay", "How much option price changes per $1 move in stock", "Volatility exposure", "Interest rate sensitivity"], "correct_index": 1},
            {"question": "Theta represents:", "options": ["Directional exposure", "Time decay — how much value an option loses per day", "Volatility changes", "Dividend impact"], "correct_index": 1},
            {"question": "A covered call strategy involves:", "options": ["Buying calls without owning stock", "Owning stock and selling calls against it", "Buying puts", "Short selling"], "correct_index": 1},
        ],
    },
    {
        "title": "Short Selling & Shorting",
        "description": "How short selling works, risks, and short squeeze mechanics.",
        "required_tier": "advanced",
        "estimated_duration_minutes": 12,
        "content_url": None,
        "quiz_questions": [
            {"question": "Short selling involves:", "options": ["Buying low and selling high", "Borrowing shares, selling them, hoping to buy back lower", "Only buying ETFs", "A type of bond"], "correct_index": 1},
            {"question": "The maximum loss on a short position is:", "options": ["Limited to your investment", "Theoretically unlimited", "Always 50%", "Zero"], "correct_index": 1},
            {"question": "A 'short squeeze' occurs when:", "options": ["Shorts are profitable", "Heavy short covering drives the price rapidly higher", "The stock goes to zero", "Trading is halted"], "correct_index": 1},
        ],
    },
    {
        "title": "Leverage & Margin",
        "description": "Theory + simulation of leveraged trading and margin requirements.",
        "required_tier": "advanced",
        "estimated_duration_minutes": 14,
        "content_url": None,
        "quiz_questions": [
            {"question": "Buying on margin means:", "options": ["Using only your own money", "Borrowing money from your broker to buy more stock", "A type of savings account", "Getting free stocks"], "correct_index": 1},
            {"question": "A margin call happens when:", "options": ["You make a profit", "Your account equity falls below the maintenance requirement", "You close a position", "You open an account"], "correct_index": 1},
            {"question": "2x leverage means a 10% stock drop results in:", "options": ["10% portfolio loss", "20% portfolio loss", "5% portfolio loss", "No loss"], "correct_index": 1},
        ],
    },
]


async def seed_modules():
    """Insert learning modules into the database."""
    async with AsyncSessionLocal() as db:
        inserted = 0
        skipped = 0

        for mod in MODULES:
            existing = await db.execute(
                select(LearningModule).where(LearningModule.title == mod["title"])
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            module = LearningModule(
                title=mod["title"],
                description=mod["description"],
                required_tier=mod["required_tier"],
                content_url=mod["content_url"],
                estimated_duration_minutes=mod["estimated_duration_minutes"],
                quiz_questions=mod["quiz_questions"],
                created_at=datetime.now(timezone.utc),
            )
            db.add(module)
            inserted += 1

        await db.commit()
        print(f"Seeded {inserted} learning modules ({skipped} already existed). Total: {len(MODULES)}")


if __name__ == "__main__":
    asyncio.run(seed_modules())
