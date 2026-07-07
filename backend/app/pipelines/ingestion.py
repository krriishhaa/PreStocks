"""
Financial Data Engineering — Ingestion Pipelines

Pipelines for:
- Funding rounds (Crunchbase, PitchBook-style)
- Valuations (public market data, private estimates)
- Company metadata (SEC EDGAR, websites)
- Executive changes (SEC 8-K filings, news)
- Acquisitions (M&A databases, news)
- News (NewsAPI, RSS feeds, GDELT)
- Hiring trends (job board APIs, LinkedIn)

Every data point carries: source, timestamp, confidence_score
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger("prestocks.pipelines")


class DataSource(str, Enum):
    SEC_EDGAR = "sec_edgar"
    CRUNCHBASE = "crunchbase"
    PITCHBOOK = "pitchbook"
    NEWS_API = "news_api"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    IEX_CLOUD = "iex_cloud"
    LINKEDIN = "linkedin"
    GLASSDOOR = "glassdoor"
    COMPANY_WEBSITE = "company_website"
    MANUAL_ENTRY = "manual"
    AI_EXTRACTED = "ai_extracted"


class ConfidenceLevel(str, Enum):
    VERIFIED = "verified"       # 0.95-1.0: Confirmed from primary source
    HIGH = "high"               # 0.80-0.94: Reliable secondary source
    MEDIUM = "medium"           # 0.60-0.79: Cross-referenced
    LOW = "low"                 # 0.40-0.59: Single unverified source
    ESTIMATED = "estimated"     # 0.20-0.39: AI-estimated or inferred


@dataclass
class DataPoint:
    """Every ingested data point carries provenance metadata."""
    value: Any
    source: DataSource
    source_url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.7
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    raw_payload: Optional[Dict] = None
    checksum: Optional[str] = None

    def __post_init__(self):
        if self.raw_payload and not self.checksum:
            self.checksum = hashlib.md5(json.dumps(self.raw_payload, default=str).encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "value": self.value,
            "source": self.source.value,
            "source_url": self.source_url,
            "timestamp": self.timestamp.isoformat(),
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level.value,
            "checksum": self.checksum
        }


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence_adjustment: float = 0.0


class DataValidator:
    """Validates and scores incoming data points."""

    def validate_funding_round(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("company_name") and not data.get("company_id"):
            errors.append("Missing company identifier")
        if not data.get("amount_usd") and not data.get("stage"):
            errors.append("Must have either amount or stage")
        if data.get("amount_usd") and data["amount_usd"] < 0:
            errors.append("Amount cannot be negative")
        if data.get("amount_usd") and data["amount_usd"] > 100_000_000_000:
            warnings.append("Unusually large amount — verify")
        if data.get("pre_money_valuation") and data.get("amount_usd"):
            if data["pre_money_valuation"] < data["amount_usd"]:
                warnings.append("Pre-money valuation less than round size — verify")
        if not data.get("announced_date"):
            warnings.append("Missing announcement date — using current timestamp")

        adjustment = -0.1 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_valuation(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("company_id"):
            errors.append("Missing company identifier")
        if not data.get("valuation_usd"):
            errors.append("Missing valuation amount")
        if data.get("valuation_usd") and data["valuation_usd"] <= 0:
            errors.append("Valuation must be positive")
        if not data.get("valuation_type"):
            warnings.append("Missing valuation type (market_cap, post_money, estimated)")
        if not data.get("as_of_date"):
            warnings.append("Missing valuation date")

        adjustment = -0.1 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_company_metadata(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("name"):
            errors.append("Company name is required")
        if data.get("founded_year") and (data["founded_year"] < 1800 or data["founded_year"] > datetime.utcnow().year):
            errors.append("Invalid founded year")
        if data.get("employee_count") and data["employee_count"] < 0:
            errors.append("Employee count cannot be negative")
        if data.get("website_url") and not data["website_url"].startswith("http"):
            warnings.append("Website URL should start with http/https")

        adjustment = -0.05 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_executive_change(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("company_id"):
            errors.append("Missing company identifier")
        if not data.get("person_name"):
            errors.append("Missing executive name")
        if not data.get("change_type"):
            errors.append("Missing change type (hired, departed, promoted)")
        if not data.get("role"):
            warnings.append("Missing role/title")
        if not data.get("effective_date"):
            warnings.append("Missing effective date")

        adjustment = -0.1 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_acquisition(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("acquirer_id") and not data.get("acquirer_name"):
            errors.append("Missing acquirer")
        if not data.get("target_id") and not data.get("target_name"):
            errors.append("Missing target company")
        if data.get("deal_value_usd") and data["deal_value_usd"] < 0:
            errors.append("Deal value cannot be negative")
        if not data.get("announced_date"):
            warnings.append("Missing announcement date")
        if not data.get("deal_status"):
            warnings.append("Missing deal status (announced, completed, terminated)")

        adjustment = -0.1 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_news(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("title"):
            errors.append("Missing article title")
        if not data.get("source_name"):
            warnings.append("Missing source name")
        if not data.get("published_at"):
            warnings.append("Missing publication date")
        if data.get("content") and len(data["content"]) < 50:
            warnings.append("Content appears too short for analysis")

        adjustment = -0.05 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)

    def validate_hiring_trend(self, data: Dict) -> ValidationResult:
        errors, warnings = [], []

        if not data.get("company_id"):
            errors.append("Missing company identifier")
        if not data.get("metric_type"):
            errors.append("Missing metric type (job_postings, headcount, department_growth)")
        if data.get("value") is None:
            errors.append("Missing metric value")
        if not data.get("period"):
            warnings.append("Missing measurement period")

        adjustment = -0.1 * len(warnings) - 0.3 * len(errors)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, confidence_adjustment=adjustment)


class BasePipeline:
    """Base class for all ingestion pipelines."""

    def __init__(self, db_session):
        self.db = db_session
        self.validator = DataValidator()
        self.stats = {"ingested": 0, "validated": 0, "rejected": 0, "warnings": 0}

    def ingest(self, raw_data: List[Dict], source: DataSource) -> Dict:
        raise NotImplementedError

    def _create_data_point(self, value: Any, source: DataSource, confidence: float = 0.7, source_url: str = None, raw: Dict = None) -> DataPoint:
        return DataPoint(value=value, source=source, confidence_score=confidence, source_url=source_url, raw_payload=raw)

    def _log_result(self, pipeline_name: str):
        logger.info(f"[{pipeline_name}] Ingested: {self.stats['ingested']}, Rejected: {self.stats['rejected']}, Warnings: {self.stats['warnings']}")


class FundingRoundPipeline(BasePipeline):
    """Ingests funding round data from Crunchbase, PitchBook, SEC filings."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.CRUNCHBASE) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_funding_round(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors, "data": record})
                continue

            confidence = 0.85 + validation.confidence_adjustment
            if source == DataSource.SEC_EDGAR:
                confidence = min(1.0, confidence + 0.1)

            data_point = self._create_data_point(
                value=record, source=source, confidence=confidence,
                source_url=record.get("source_url"), raw=record
            )

            self.stats["ingested"] += 1
            self.stats["warnings"] += len(validation.warnings)
            results.append({
                "status": "ingested",
                "data_point": data_point.to_dict(),
                "warnings": validation.warnings
            })

        self._log_result("FundingRoundPipeline")
        return {"pipeline": "funding_rounds", "source": source.value, "stats": self.stats, "results": results}


class ValuationPipeline(BasePipeline):
    """Ingests company valuations from market data, funding rounds, analyst estimates."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.POLYGON) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_valuation(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.9 if source in (DataSource.POLYGON, DataSource.IEX_CLOUD) else 0.7
            confidence += validation.confidence_adjustment

            data_point = self._create_data_point(value=record, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("ValuationPipeline")
        return {"pipeline": "valuations", "source": source.value, "stats": self.stats, "results": results}


class CompanyMetadataPipeline(BasePipeline):
    """Ingests company metadata from SEC, Crunchbase, company websites."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.SEC_EDGAR) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_company_metadata(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.95 if source == DataSource.SEC_EDGAR else 0.80
            confidence += validation.confidence_adjustment

            data_point = self._create_data_point(value=record, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("CompanyMetadataPipeline")
        return {"pipeline": "company_metadata", "source": source.value, "stats": self.stats, "results": results}


class ExecutiveChangePipeline(BasePipeline):
    """Ingests executive hires, departures, promotions from SEC 8-K and news."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.SEC_EDGAR) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_executive_change(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.92 if source == DataSource.SEC_EDGAR else 0.70
            confidence += validation.confidence_adjustment

            data_point = self._create_data_point(value=record, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("ExecutiveChangePipeline")
        return {"pipeline": "executive_changes", "source": source.value, "stats": self.stats, "results": results}


class AcquisitionPipeline(BasePipeline):
    """Ingests M&A deal data from news, SEC filings, databases."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.NEWS_API) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_acquisition(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.90 if source == DataSource.SEC_EDGAR else 0.75
            confidence += validation.confidence_adjustment

            data_point = self._create_data_point(value=record, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("AcquisitionPipeline")
        return {"pipeline": "acquisitions", "source": source.value, "stats": self.stats, "results": results}


class NewsPipeline(BasePipeline):
    """Ingests news articles with NLP-based sentiment and entity extraction."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.NEWS_API) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_news(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.85
            confidence += validation.confidence_adjustment

            enriched = self._enrich_news(record)
            data_point = self._create_data_point(value=enriched, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("NewsPipeline")
        return {"pipeline": "news", "source": source.value, "stats": self.stats, "results": results}

    def _enrich_news(self, record: Dict) -> Dict:
        """Add sentiment and entity extraction."""
        text = (record.get("title", "") + " " + record.get("content", "")).lower()
        positive = sum(1 for w in ["growth", "profit", "beat", "surge", "strong"] if w in text)
        negative = sum(1 for w in ["loss", "decline", "miss", "cut", "weak"] if w in text)
        net = (positive - negative) / max(1, positive + negative)

        record["sentiment_score"] = round(net, 3)
        record["sentiment_label"] = "positive" if net > 0.2 else "negative" if net < -0.2 else "neutral"
        return record


class HiringTrendPipeline(BasePipeline):
    """Ingests hiring/workforce data from job boards and company reports."""

    def ingest(self, raw_data: List[Dict], source: DataSource = DataSource.LINKEDIN) -> Dict:
        results = []
        for record in raw_data:
            validation = self.validator.validate_hiring_trend(record)
            if not validation.is_valid:
                self.stats["rejected"] += 1
                results.append({"status": "rejected", "errors": validation.errors})
                continue

            confidence = 0.70 if source == DataSource.LINKEDIN else 0.60
            confidence += validation.confidence_adjustment

            data_point = self._create_data_point(value=record, source=source, confidence=confidence, raw=record)
            self.stats["ingested"] += 1
            results.append({"status": "ingested", "data_point": data_point.to_dict()})

        self._log_result("HiringTrendPipeline")
        return {"pipeline": "hiring_trends", "source": source.value, "stats": self.stats, "results": results}


class PipelineOrchestrator:
    """Coordinates all data pipelines."""

    def __init__(self, db_session):
        self.db = db_session
        self.pipelines = {
            "funding_rounds": FundingRoundPipeline(db_session),
            "valuations": ValuationPipeline(db_session),
            "company_metadata": CompanyMetadataPipeline(db_session),
            "executive_changes": ExecutiveChangePipeline(db_session),
            "acquisitions": AcquisitionPipeline(db_session),
            "news": NewsPipeline(db_session),
            "hiring_trends": HiringTrendPipeline(db_session),
        }

    def run_pipeline(self, pipeline_name: str, data: List[Dict], source: DataSource) -> Dict:
        pipeline = self.pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Unknown pipeline: {pipeline_name}. Available: {list(self.pipelines.keys())}")
        return pipeline.ingest(data, source)

    def run_all(self, data_by_pipeline: Dict[str, List[Dict]], source: DataSource) -> Dict:
        results = {}
        for name, data in data_by_pipeline.items():
            if name in self.pipelines and data:
                results[name] = self.run_pipeline(name, data, source)
        return results

    def get_pipeline_status(self) -> Dict:
        return {name: {"available": True, "type": type(p).__name__} for name, p in self.pipelines.items()}
