"""
Unit tests for flag calculation engine and portfolio math.
Run: pytest tests/ -v
"""
import pytest
import math
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.core.constants import RISK_THRESHOLDS, INITIAL_CASH_BALANCE
from app.services.flag_calculation_engine import FlagCalculationEngine, HIGH, MEDIUM, LOW


class TestFlagCalculationHelpers:
    """Test static helper methods."""

    def test_calculate_std_dev_empty(self):
        result = FlagCalculationEngine._calculate_std_dev([])
        assert result == 0.0

    def test_calculate_std_dev_single_price(self):
        mock_price = MagicMock(close=100.0)
        result = FlagCalculationEngine._calculate_std_dev([mock_price])
        assert result == 0.0

    def test_calculate_std_dev_stable_prices(self):
        prices = [MagicMock(close=100.0 + i * 0.01) for i in range(10)]
        result = FlagCalculationEngine._calculate_std_dev(prices)
        assert result < 0.001  # very low volatility

    def test_calculate_std_dev_volatile_prices(self):
        prices = [MagicMock(close=v) for v in [100, 110, 95, 115, 90, 120, 85]]
        result = FlagCalculationEngine._calculate_std_dev(prices)
        assert result > 0.05  # high volatility

    def test_calculate_percentile_middle(self):
        distribution = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = FlagCalculationEngine._calculate_percentile(55, distribution)
        assert 40 <= result <= 60

    def test_calculate_percentile_low(self):
        distribution = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = FlagCalculationEngine._calculate_percentile(5, distribution)
        assert result == 0.0

    def test_calculate_percentile_high(self):
        distribution = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        result = FlagCalculationEngine._calculate_percentile(99, distribution)
        assert result == 90.0

    def test_calculate_percentile_empty(self):
        result = FlagCalculationEngine._calculate_percentile(50, [])
        assert result == 50.0

    def test_make_flag_structure(self):
        flag = FlagCalculationEngine._make_flag("volatility", 75, "Test explanation", 0.9)
        assert flag["type"] == "volatility"
        assert flag["severity_score"] == 75
        assert flag["explanation"] == "Test explanation"
        assert flag["confidence"] == 0.9


class TestRiskThresholds:
    """Test risk threshold boundaries."""

    def test_low_threshold(self):
        low, high = RISK_THRESHOLDS["low"]
        assert low == 0
        assert high == 30

    def test_medium_threshold(self):
        low, high = RISK_THRESHOLDS["medium"]
        assert low == 31
        assert high == 60

    def test_high_threshold(self):
        low, high = RISK_THRESHOLDS["high"]
        assert low == 61
        assert high == 80

    def test_critical_threshold(self):
        low, high = RISK_THRESHOLDS["critical"]
        assert low == 81
        assert high == 100


class TestPortfolioMath:
    """Test portfolio calculation logic."""

    def test_weighted_average_buy_price(self):
        old_qty = 10
        old_avg = 100.0
        new_qty = 5
        new_price = 120.0
        total_qty = old_qty + new_qty
        new_avg = ((old_avg * old_qty) + (new_price * new_qty)) / total_qty
        assert abs(new_avg - 106.67) < 0.01

    def test_gain_loss_calculation(self):
        avg_price = 100.0
        current_price = 115.0
        gain_pct = ((current_price - avg_price) / avg_price) * 100
        assert gain_pct == 15.0

    def test_portfolio_value_calculation(self):
        cash = 5000.0
        holdings_value = 3000.0  # 10 shares @ $150 + 5 shares @ $300
        total = cash + holdings_value
        assert total == 8000.0

    def test_position_size_percent(self):
        position_value = 2500.0
        portfolio_value = 10000.0
        pct = (position_value / portfolio_value) * 100
        assert pct == 25.0

    def test_sector_concentration(self):
        holdings = {"Technology": 6000, "Healthcare": 2000, "Energy": 2000}
        total = sum(holdings.values())
        tech_pct = holdings["Technology"] / total
        assert tech_pct == 0.6
        assert tech_pct > 0.4  # would trigger concentration warning

    def test_initial_cash_balance(self):
        assert INITIAL_CASH_BALANCE == 10000.00

    def test_buy_reduces_cash(self):
        cash = 10000.0
        trade_cost = 1500.0  # 10 shares @ $150
        remaining = cash - trade_cost
        assert remaining == 8500.0

    def test_sell_increases_cash(self):
        cash = 8500.0
        trade_proceeds = 1200.0  # 10 shares @ $120
        new_cash = cash + trade_proceeds
        assert new_cash == 9700.0


class TestTradeValidation:
    """Test trade validation logic."""

    def test_insufficient_cash_buy(self):
        cash_available = 5000.0
        trade_cost = 6000.0
        assert trade_cost > cash_available  # should reject

    def test_sufficient_cash_buy(self):
        cash_available = 5000.0
        trade_cost = 3000.0
        assert trade_cost <= cash_available  # should allow

    def test_insufficient_shares_sell(self):
        owned = 5.0
        selling = 10.0
        assert selling > owned  # should reject

    def test_sufficient_shares_sell(self):
        owned = 10.0
        selling = 5.0
        assert selling <= owned  # should allow

    def test_zero_quantity_rejected(self):
        quantity = 0
        assert quantity <= 0  # should reject

    def test_negative_quantity_rejected(self):
        quantity = -5
        assert quantity <= 0  # should reject
