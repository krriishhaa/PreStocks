"""
Backtesting pipeline: validates flag accuracy against historical price data.
Compares predicted risk scores to actual 30-day outcomes.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flags import FlagHistory
from app.models.stock import PriceHistory


class BacktestResult:
    def __init__(self, ticker: str, accuracy: float, sample_size: int, avg_predicted_risk: float, avg_actual_return: float):
        self.ticker = ticker
        self.accuracy = accuracy
        self.sample_size = sample_size
        self.avg_predicted_risk = avg_predicted_risk
        self.avg_actual_return = avg_actual_return


async def run_backtest(db: AsyncSession, ticker: str, lookback_days: int = 365) -> Optional[BacktestResult]:
    """
    Compare historical flag predictions to actual price outcomes.
    A high-risk flag should correlate with negative 30-day returns.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    result = await db.execute(
        select(FlagHistory)
        .where(FlagHistory.ticker == ticker, FlagHistory.snapshot_date >= cutoff)
        .order_by(FlagHistory.snapshot_date)
    )
    snapshots = result.scalars().all()

    if len(snapshots) < 10:
        return None

    correct_predictions = 0
    total = 0
    sum_predicted = 0.0
    sum_actual = 0.0

    for snap in snapshots:
        if snap.actual_outcome_30d is None:
            continue
        total += 1
        sum_predicted += snap.composite_score
        sum_actual += snap.actual_outcome_30d

        high_risk = snap.composite_score > 60
        negative_outcome = snap.actual_outcome_30d < -5
        low_risk = snap.composite_score < 30
        positive_outcome = snap.actual_outcome_30d > 0

        if (high_risk and negative_outcome) or (low_risk and positive_outcome):
            correct_predictions += 1

    if total == 0:
        return None

    return BacktestResult(
        ticker=ticker,
        accuracy=correct_predictions / total,
        sample_size=total,
        avg_predicted_risk=sum_predicted / total,
        avg_actual_return=sum_actual / total,
    )
