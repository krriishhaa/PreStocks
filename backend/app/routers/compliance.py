"""
Legal & Compliance — Data retention, AI disclosures, required notices.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.user import User

router = APIRouter()


@router.get("/disclosures")
def get_required_disclosures():
    """Return all required disclosures for the platform."""
    return {
        "platform_classification": {
            "type": "educational_analytical",
            "is_registered_advisor": False,
            "is_broker_dealer": False,
            "regulatory_basis": "Publisher's exclusion under Section 202(a)(11)(D) of the Investment Advisers Act",
            "description": "PreStocks provides educational market research tools and paper trading simulation. No real securities transactions occur."
        },
        "ai_disclosure": {
            "uses_ai": True,
            "ai_systems": [
                {
                    "name": "Research Assistant",
                    "model_type": "Large Language Model",
                    "purpose": "Generate company research summaries and risk analysis",
                    "limitations": ["May produce inaccurate information", "Training data has a cutoff date", "Cannot predict future events"],
                    "labeling": "All outputs marked with AI Generated badge"
                },
                {
                    "name": "Risk Scoring Engine",
                    "model_type": "Rule-based + ML ensemble",
                    "purpose": "Calculate composite risk scores (0-100)",
                    "limitations": ["Based on historical patterns", "Cannot predict black swan events", "Scores are estimates, not guarantees"],
                    "labeling": "Scores display methodology and confidence level"
                },
                {
                    "name": "News Sentiment Analyzer",
                    "model_type": "FinBERT (fine-tuned NLP)",
                    "purpose": "Classify news article sentiment",
                    "limitations": ["May misread sarcasm or context", "Limited to English language", "Domain-specific jargon may confuse model"],
                    "labeling": "Sentiment labels marked as AI-determined"
                },
                {
                    "name": "Portfolio Advisor",
                    "model_type": "Rule-based + LLM",
                    "purpose": "Diversification analysis and general suggestions",
                    "limitations": ["General education only", "Not personalized financial advice", "Does not consider tax or legal implications"],
                    "labeling": "All suggestions prefixed with educational disclaimer"
                },
                {
                    "name": "Recommendation Engine",
                    "model_type": "Collaborative filtering",
                    "purpose": "Suggest similar companies based on user interests",
                    "limitations": ["Based on behavioral patterns", "Not a suitability assessment", "May have popularity bias"],
                    "labeling": "Recommendations labeled as interest-based, not advice"
                }
            ],
            "user_controls": [
                "Opt out of AI data improvement in Settings",
                "View which AI system generated each output",
                "Report inaccurate AI outputs via feedback button",
                "Delete AI conversation history"
            ]
        },
        "investment_risks": {
            "general": "Investing involves risk. You may lose some or all of your investment.",
            "pre_ipo_specific": [
                "Private securities are illiquid and may not be sellable for years",
                "Valuations are estimates, not verified market prices",
                "Less disclosure than public companies",
                "High failure rate among startups",
                "Accredited investor requirements may apply to real investments"
            ],
            "paper_trading": [
                "Simulated results do not represent actual trading outcomes",
                "Real execution involves fees, spreads, and liquidity constraints",
                "Past simulated performance does not predict real results"
            ]
        },
        "not_financial_advice_statement": "Nothing on PreStocks constitutes investment advice, a recommendation to buy or sell any security, or an offer of any financial product. All content is for informational and educational purposes only. Consult a qualified financial advisor before making investment decisions."
    }


@router.get("/data-retention")
def get_data_retention_policy():
    """Return the data retention schedule."""
    return {
        "policy_version": "1.0",
        "effective_date": "2026-07-01",
        "retention_schedule": [
            {
                "data_category": "Account information",
                "retention_period": "Duration of account + 30 days",
                "deletion_method": "Hard delete on account deletion",
                "legal_basis": "Contract performance"
            },
            {
                "data_category": "Paper trading history",
                "retention_period": "Duration of account + 90 days",
                "deletion_method": "Anonymized after account deletion",
                "legal_basis": "Legitimate interest (service delivery)"
            },
            {
                "data_category": "AI conversation logs",
                "retention_period": "90 days active, then anonymized",
                "deletion_method": "PII stripped; anonymized content retained for model improvement",
                "legal_basis": "Consent (opt-out available)"
            },
            {
                "data_category": "Search queries",
                "retention_period": "30 days (individual), aggregated indefinitely",
                "deletion_method": "Individual queries purged; aggregated for trending",
                "legal_basis": "Legitimate interest"
            },
            {
                "data_category": "Server/access logs",
                "retention_period": "30 days",
                "deletion_method": "Automatic purge",
                "legal_basis": "Security & legitimate interest"
            },
            {
                "data_category": "Analytics data",
                "retention_period": "24 months (aggregated only)",
                "deletion_method": "Anonymized at collection",
                "legal_basis": "Consent"
            },
            {
                "data_category": "Security audit logs",
                "retention_period": "12 months",
                "deletion_method": "Automatic purge",
                "legal_basis": "Legal obligation & legitimate interest"
            },
            {
                "data_category": "Backup copies",
                "retention_period": "30 days after primary deletion",
                "deletion_method": "Overwritten in backup rotation",
                "legal_basis": "Legitimate interest (disaster recovery)"
            },
            {
                "data_category": "Marketing preferences",
                "retention_period": "Until consent withdrawn",
                "deletion_method": "Immediate on opt-out",
                "legal_basis": "Consent"
            }
        ],
        "user_rights": {
            "access": "Request a copy of all personal data (Settings → Privacy → Export Data)",
            "correction": "Update information via Settings or support request",
            "deletion": "Settings → Account → Delete Account (30-day grace period)",
            "portability": "Export in JSON format via Settings → Privacy → Export",
            "opt_out_ai": "Settings → Privacy → AI Data Usage → Disable"
        },
        "deletion_process": [
            "User initiates deletion via Settings or email to privacy@prestocks.io",
            "Account immediately deactivated (30-day recovery window)",
            "After 30 days: personal data hard-deleted from primary databases",
            "After 60 days: removed from all backup systems",
            "Anonymized aggregate data (user counts, trends) retained indefinitely"
        ]
    }


@router.post("/data-export")
def request_data_export(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Request a full export of user's personal data (GDPR Art. 20)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # In production: queue background job to compile export
    return {
        "status": "processing",
        "message": "Your data export is being prepared. You will receive an email with a download link within 48 hours.",
        "request_id": f"export_{user_id}_{int(datetime.utcnow().timestamp())}",
        "estimated_completion": (datetime.utcnow() + timedelta(hours=48)).isoformat()
    }


@router.post("/delete-account")
def initiate_account_deletion(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Initiate account deletion (30-day grace period)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = user.preferences or {}
    prefs["deletion_requested"] = True
    prefs["deletion_requested_at"] = datetime.utcnow().isoformat()
    prefs["deletion_scheduled_for"] = (datetime.utcnow() + timedelta(days=30)).isoformat()
    user.preferences = prefs
    user.is_active = False
    db.commit()

    return {
        "status": "scheduled",
        "message": "Account deletion initiated. Your account is now deactivated.",
        "grace_period_ends": prefs["deletion_scheduled_for"],
        "recovery_instructions": "Log in within 30 days to cancel deletion."
    }


@router.post("/cancel-deletion")
def cancel_account_deletion(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cancel a pending account deletion during grace period."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = user.preferences or {}
    if not prefs.get("deletion_requested"):
        raise HTTPException(status_code=400, detail="No pending deletion request")

    prefs.pop("deletion_requested", None)
    prefs.pop("deletion_requested_at", None)
    prefs.pop("deletion_scheduled_for", None)
    user.preferences = prefs
    user.is_active = True
    db.commit()

    return {"status": "cancelled", "message": "Account deletion cancelled. Your account is active again."}
