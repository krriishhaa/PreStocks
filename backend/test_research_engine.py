from backend.research.sec_filing_analyzer import analyze_sec_filing
from backend.research.earnings_call_analyzer import analyze_earnings_call
from backend.research.valuation_agent import ValuationInput, compute_valuation_metrics
from backend.research.rag_engine import index_documents, query_documents
from backend.warehouse.db import init_warehouse_db


def test_sec_and_earnings_analyzers():
    sec = analyze_sec_filing(
        "10-K",
        "Management expects growth and expansion. Regulatory risk and competition remain key risks.",
    )
    assert "risks" in sec and "opportunities" in sec

    earn = analyze_earnings_call(
        "We are confident in our pipeline. We raised guidance for next quarter despite macro headwinds."
    )
    assert "sentiment" in earn and "guidance_changes" in earn


def test_valuation_agent_output():
    out = compute_valuation_metrics(
        ValuationInput(
            symbol="NVDA",
            price=145.0,
            shares_outstanding=2500.0,
            free_cash_flow=25000.0,
            growth_rate=0.15,
            discount_rate=0.1,
            terminal_growth=0.03,
            eps=2.2,
            earnings_growth_rate=0.25,
            ebitda=32000.0,
            enterprise_value=900000.0,
            revenue_growth=0.22,
            profit_margin=0.24,
        )
    )
    assert out["valuation_label"] in {"cheap", "fair", "expensive", "indeterminate"}


def test_rag_index_and_query():
    init_warehouse_db()
    index_documents(
        [
            {
                "doc_type": "sec_filing",
                "source": "SEC",
                "symbol": "NVDA",
                "title": "NVDA 10-K risk factors",
                "content": "Key risk factors include supply chain exposure and regulatory changes.",
            },
            {
                "doc_type": "research_report",
                "source": "Internal",
                "symbol": "MSFT",
                "title": "Cloud AI growth report",
                "content": "Cloud AI growth remains strong with rising enterprise adoption.",
            },
        ]
    )
    result = query_documents("What are regulatory risks for NVDA?", top_k=2)
    assert len(result["matches"]) >= 1

