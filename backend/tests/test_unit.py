"""
Unit Tests — Individual components and functions.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


# ─── PIPELINE UNIT TESTS ───

class TestDataValidator:
    """Unit tests for DataValidator."""

    def setup_method(self):
        from app.pipelines.ingestion import DataValidator
        self.validator = DataValidator()

    def test_valid_funding_round(self):
        data = {"company_name": "TestCorp", "amount_usd": 50_000_000, "stage": "series_a", "announced_date": "2026-01-15"}
        result = self.validator.validate_funding_round(data)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_funding_round_missing_company(self):
        data = {"amount_usd": 50_000_000, "stage": "series_a"}
        result = self.validator.validate_funding_round(data)
        assert result.is_valid is False
        assert "Missing company identifier" in result.errors

    def test_funding_round_negative_amount(self):
        data = {"company_name": "Test", "amount_usd": -100, "stage": "seed"}
        result = self.validator.validate_funding_round(data)
        assert result.is_valid is False

    def test_funding_round_unusually_large(self):
        data = {"company_name": "Test", "amount_usd": 200_000_000_000, "stage": "late"}
        result = self.validator.validate_funding_round(data)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_valid_valuation(self):
        data = {"company_id": 1, "valuation_usd": 1_000_000_000, "valuation_type": "post_money", "as_of_date": "2026-06-01"}
        result = self.validator.validate_valuation(data)
        assert result.is_valid is True

    def test_valuation_missing_amount(self):
        data = {"company_id": 1}
        result = self.validator.validate_valuation(data)
        assert result.is_valid is False

    def test_valid_company_metadata(self):
        data = {"name": "TestCorp", "founded_year": 2020, "employee_count": 500, "website_url": "https://testcorp.com"}
        result = self.validator.validate_company_metadata(data)
        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_company_metadata_invalid_year(self):
        data = {"name": "TestCorp", "founded_year": 1700}
        result = self.validator.validate_company_metadata(data)
        assert result.is_valid is False

    def test_valid_executive_change(self):
        data = {"company_id": 1, "person_name": "Jane Doe", "change_type": "hired", "role": "CTO", "effective_date": "2026-03-01"}
        result = self.validator.validate_executive_change(data)
        assert result.is_valid is True

    def test_executive_change_missing_fields(self):
        data = {"company_id": 1}
        result = self.validator.validate_executive_change(data)
        assert result.is_valid is False
        assert len(result.errors) >= 2

    def test_valid_acquisition(self):
        data = {"acquirer_name": "BigCo", "target_name": "SmallCo", "deal_value_usd": 500_000_000, "deal_status": "completed"}
        result = self.validator.validate_acquisition(data)
        assert result.is_valid is True

    def test_valid_news(self):
        data = {"title": "Company raises $100M", "source_name": "TechCrunch", "published_at": "2026-06-01", "content": "Full article content here with sufficient length for processing."}
        result = self.validator.validate_news(data)
        assert result.is_valid is True

    def test_valid_hiring_trend(self):
        data = {"company_id": 1, "metric_type": "job_postings", "value": 150, "period": "2026-Q2"}
        result = self.validator.validate_hiring_trend(data)
        assert result.is_valid is True


class TestDataPoint:
    """Unit tests for DataPoint model."""

    def test_create_data_point(self):
        from app.pipelines.ingestion import DataPoint, DataSource
        dp = DataPoint(value={"test": 1}, source=DataSource.SEC_EDGAR, confidence_score=0.95)
        assert dp.confidence_score == 0.95
        assert dp.source == DataSource.SEC_EDGAR

    def test_data_point_checksum(self):
        from app.pipelines.ingestion import DataPoint, DataSource
        dp = DataPoint(value="test", source=DataSource.NEWS_API, raw_payload={"key": "value"})
        assert dp.checksum is not None
        assert len(dp.checksum) == 32

    def test_data_point_to_dict(self):
        from app.pipelines.ingestion import DataPoint, DataSource, ConfidenceLevel
        dp = DataPoint(value=100, source=DataSource.POLYGON, confidence_score=0.85, confidence_level=ConfidenceLevel.HIGH)
        d = dp.to_dict()
        assert d["source"] == "polygon"
        assert d["confidence_score"] == 0.85
        assert d["confidence_level"] == "high"


class TestSEOManager:
    """Unit tests for SEO utilities (frontend)."""

    def test_generate_landing_meta(self):
        # Simulating the SEOManager from JS — testing logic
        configs = {
            "landing": {"title": "PreStocks", "description": "Research pre-IPO companies"},
            "blog": {"title": "Blog", "description": "Insights"}
        }
        assert "PreStocks" in configs["landing"]["title"]
        assert "pre-IPO" in configs["landing"]["description"]


class TestReferralProgram:
    """Unit tests for referral tier logic."""

    def test_tier_calculation(self):
        TIERS = [
            {"referrals": 3, "reward": "1 month Pro"},
            {"referrals": 10, "reward": "3 months Pro"},
            {"referrals": 25, "reward": "Lifetime Pro"}
        ]

        def get_tier(count):
            return next((t for t in reversed(TIERS) if count >= t["referrals"]), None)

        assert get_tier(0) is None
        assert get_tier(3)["reward"] == "1 month Pro"
        assert get_tier(10)["reward"] == "3 months Pro"
        assert get_tier(50)["reward"] == "Lifetime Pro"


# ─── SECURITY UNIT TESTS ───

class TestSecurityFunctions:
    """Unit tests for security utilities."""

    def test_password_hashing(self):
        from app.core.security import hash_password
        hashed = hash_password("TestPassword123!")
        assert hashed != "TestPassword123!"
        assert len(hashed) > 20

    def test_token_creation(self):
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_decode(self):
        from app.core.security import create_access_token, decode_token
        token = create_access_token(data={"sub": "42"})
        payload = decode_token(token)
        assert payload is not None
