from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from sqlalchemy import desc, select

from backend.warehouse.db import get_engine, init_warehouse_db, insert_rows, rag_documents


EMBED_DIM = 256


def index_documents(documents: list[dict[str, Any]]) -> dict[str, int]:
    """
    documents item shape:
    {
      "doc_type": "sec_filing|news|transcript|research_report",
      "source": "SEC",
      "symbol": "NVDA",
      "title": "...",
      "content": "..."
    }
    """
    init_warehouse_db()
    rows = []
    for doc in documents:
        content = (doc.get("content") or "").strip()
        title = (doc.get("title") or "").strip()
        if not content or not title:
            continue
        rows.append(
            {
                "doc_type": doc.get("doc_type", "research_report"),
                "source": doc.get("source"),
                "symbol": (doc.get("symbol") or "").upper() or None,
                "title": title,
                "content": content,
                "embedding": _embed(content),
            }
        )
    inserted = insert_rows(rag_documents, rows)
    return {"indexed": inserted}


def query_documents(question: str, top_k: int = 5) -> dict[str, Any]:
    init_warehouse_db()
    q_vec = _embed(question)

    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(select(rag_documents).order_by(desc(rag_documents.c.id)).limit(500)).mappings().all()

    scored = []
    for row in rows:
        doc_vec = row.get("embedding") or []
        sim = _cosine_similarity(q_vec, doc_vec)
        scored.append((sim, dict(row)))
    scored.sort(key=lambda x: x[0], reverse=True)

    matches = []
    for sim, row in scored[:top_k]:
        matches.append(
            {
                "score": round(sim, 4),
                "doc_type": row.get("doc_type"),
                "symbol": row.get("symbol"),
                "title": row.get("title"),
                "snippet": (row.get("content") or "")[:320],
            }
        )

    return {
        "question": question,
        "matches": matches,
        "answer": _compose_answer(question, matches),
    }


def _compose_answer(question: str, matches: list[dict[str, Any]]) -> str:
    if not matches:
        return "No indexed documents matched this question. Add SEC/news/transcript/research docs first."
    lines = [
        f"Based on {len(matches)} retrieved documents, here are the highest-confidence signals for: {question}",
    ]
    for m in matches[:3]:
        lines.append(f"- {m['title']} ({m.get('doc_type')}, score={m['score']})")
    lines.append("Use these references for follow-up deep-dive analysis.")
    return " ".join(lines)


def _embed(text: str) -> list[float]:
    vec = [0.0] * EMBED_DIM
    tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    if not tokens:
        return vec
    for token in tokens:
        idx = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % EMBED_DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))

