# PreStocks Phases 2-5 Overview

## Phase 2: Financial Data Warehouse

Implemented in `backend/warehouse/db.py` with these tables:

- `users`
- `companies`
- `prices`
- `financials`
- `news`
- `earnings_calls`
- `watchlists`
- `portfolios`
- `transactions`
- `ai_reports`

Support table:

- `rag_documents` (vectorized document index for RAG)

API endpoints:

- `POST /warehouse/init`
- `POST /warehouse/seed-demo`
- `GET /warehouse/status`

## Phase 3: AI Research Engine

Implemented modules:

- SEC Filing Analyzer: `backend/research/sec_filing_analyzer.py`
- Earnings Call Analyzer: `backend/research/earnings_call_analyzer.py`
- Valuation Agent: `backend/research/valuation_agent.py`

API endpoints:

- `POST /ai/sec-filing/analyze`
- `POST /ai/earnings-call/analyze`
- `POST /ai/valuation`

## Phase 4: RAG

Implemented in `backend/research/rag_engine.py`.

Workflow:

1. Index documents (`/rag/index`)
2. Embed and store vectors in `rag_documents`
3. Query (`/rag/query`)
4. Retrieve top-k by cosine similarity
5. Return synthesized answer + citations

## Phase 5: Investment Copilot

Implemented in `backend/copilot/engine.py`.

API endpoint:

- `POST /copilot/query`

Supported user flows:

- "What stocks benefit from AI?"
- "Build a retirement portfolio"

