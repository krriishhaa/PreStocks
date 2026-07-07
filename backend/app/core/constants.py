# Risk tier definitions
RISK_TIERS = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
}

# Risk flag severity scores
RISK_FLAG_SEVERITY = {
    "low": 25,
    "medium": 50,
    "high": 75,
}

# Risk flag types
RISK_FLAG_TYPES = [
    "volatility",
    "valuation",
    "balance_sheet",
    "insider_activity",
    "short_interest",
    "earnings_risk",
    "liquidity",
    "social_hype",
]

# Starting portfolio value (simulated)
STARTING_PORTFOLIO_VALUE = 10000.00

# Portfolio constraints
MAX_POSITION_SIZE_PCT = 0.25  # 25% of portfolio
MAX_SECTOR_EXPOSURE_PCT = 0.40  # 40% of portfolio
MIN_TRADING_QUANTITY = 0.01  # Allow fractional shares

# Learning module requirements
QUIZ_PASSING_SCORE = 80  # 80% required to pass
BEGINNER_MODULES_TO_UNLOCK_INTERMEDIATE = 5
INTERMEDIATE_MODULES_TO_UNLOCK_ADVANCED = 5
