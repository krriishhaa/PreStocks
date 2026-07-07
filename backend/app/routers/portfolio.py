"""
Portfolio Router — portfolio state, trade execution, transaction history.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel as PydanticModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.portfolio import Portfolio, Holding, Trade

router = APIRouter()


class TradeRequest(PydanticModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    company_name: Optional[str] = None
    side: str = Field(..., pattern="^(buy|sell)$")
    shares: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    order_type: str = "market"


def _get_or_create_portfolio(user_id: int, db: Session) -> Portfolio:
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=user_id, name="Main Portfolio", cash=10000.00, initial_capital=10000.00)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    return portfolio


@router.get("")
def get_portfolio(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = _get_or_create_portfolio(user_id, db)
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()

    total_invested = sum(h.shares * h.avg_buy_price for h in holdings)
    total_market = sum(h.market_value for h in holdings)

    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "cash": round(portfolio.cash, 2),
        "initial_capital": portfolio.initial_capital,
        "total_value": round(portfolio.cash + total_market, 2),
        "total_invested": round(total_invested, 2),
        "unrealized_pnl": round(total_market - total_invested, 2),
        "positions": len(holdings),
        "holdings": [
            {
                "id": h.id,
                "symbol": h.symbol,
                "company_name": h.company_name,
                "shares": h.shares,
                "avg_buy_price": h.avg_buy_price,
                "current_price": h.current_price,
                "market_value": round(h.market_value, 2),
                "unrealized_pnl": round(h.unrealized_pnl, 2),
                "unrealized_pnl_pct": round(h.unrealized_pnl_pct, 2),
            }
            for h in holdings
        ],
    }


@router.get("/summary")
def get_portfolio_summary(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = _get_or_create_portfolio(user_id, db)
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()

    total_market = sum(h.market_value for h in holdings)
    total_value = portfolio.cash + total_market
    pnl = total_value - portfolio.initial_capital
    pnl_pct = (pnl / portfolio.initial_capital * 100) if portfolio.initial_capital else 0

    return {
        "total_value": round(total_value, 2),
        "cash": round(portfolio.cash, 2),
        "invested": round(total_market, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "positions": len(holdings),
        "initial_capital": portfolio.initial_capital,
    }


@router.post("/trades", status_code=201)
def place_trade(
    trade_req: TradeRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    portfolio = _get_or_create_portfolio(user_id, db)
    total_amount = trade_req.shares * trade_req.price

    if trade_req.side == "buy":
        if portfolio.cash < total_amount:
            raise HTTPException(status_code=400, detail=f"Insufficient cash. Available: ${portfolio.cash:.2f}, Required: ${total_amount:.2f}")

        portfolio.cash -= total_amount

        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id,
            Holding.symbol == trade_req.symbol.upper(),
        ).first()

        if existing:
            new_total_shares = existing.shares + trade_req.shares
            existing.avg_buy_price = (
                (existing.shares * existing.avg_buy_price) + (trade_req.shares * trade_req.price)
            ) / new_total_shares
            existing.shares = new_total_shares
            existing.current_price = trade_req.price
        else:
            holding = Holding(
                portfolio_id=portfolio.id,
                symbol=trade_req.symbol.upper(),
                company_name=trade_req.company_name,
                shares=trade_req.shares,
                avg_buy_price=trade_req.price,
                current_price=trade_req.price,
            )
            db.add(holding)

    elif trade_req.side == "sell":
        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id,
            Holding.symbol == trade_req.symbol.upper(),
        ).first()

        if not existing or existing.shares < trade_req.shares:
            available = existing.shares if existing else 0
            raise HTTPException(status_code=400, detail=f"Insufficient shares. You own {available} shares of {trade_req.symbol.upper()}")

        existing.shares -= trade_req.shares
        portfolio.cash += total_amount

        if existing.shares <= 0:
            db.delete(existing)

    trade = Trade(
        portfolio_id=portfolio.id,
        symbol=trade_req.symbol.upper(),
        company_name=trade_req.company_name,
        side=trade_req.side,
        order_type=trade_req.order_type,
        shares=trade_req.shares,
        price=trade_req.price,
        total_amount=total_amount,
        status="filled",
        executed_at=datetime.utcnow(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {
        "id": trade.id,
        "symbol": trade.symbol,
        "side": trade.side,
        "shares": trade.shares,
        "price": trade.price,
        "total_amount": trade.total_amount,
        "status": trade.status,
        "executed_at": trade.executed_at.isoformat(),
        "cash_remaining": round(portfolio.cash, 2),
    }


@router.get("/trades")
def get_trade_history(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        return []

    trades = (
        db.query(Trade)
        .filter(Trade.portfolio_id == portfolio.id)
        .order_by(Trade.executed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": t.id,
            "symbol": t.symbol,
            "company_name": t.company_name,
            "side": t.side,
            "order_type": t.order_type,
            "shares": t.shares,
            "price": t.price,
            "total_amount": t.total_amount,
            "status": t.status,
            "executed_at": t.executed_at.isoformat() if t.executed_at else None,
        }
        for t in trades
    ]


@router.get("/risk-summary")
def get_portfolio_risk(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        return {"concentration_risk": "none", "top_holding_pct": 0, "diversification_score": 100, "positions": 0}

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    if not holdings:
        return {"concentration_risk": "none", "top_holding_pct": 0, "diversification_score": 100, "positions": 0}

    total = sum(h.market_value for h in holdings)
    if total == 0:
        return {"concentration_risk": "none", "top_holding_pct": 0, "diversification_score": 100, "positions": len(holdings)}

    weights = sorted([(h.market_value / total * 100) for h in holdings], reverse=True)
    top_pct = weights[0]
    hhi = sum(w ** 2 for w in weights)
    diversification = max(0, min(100, 100 - (hhi / 100)))

    if top_pct > 40:
        concentration = "high"
    elif top_pct > 25:
        concentration = "medium"
    else:
        concentration = "low"

    return {
        "concentration_risk": concentration,
        "top_holding_pct": round(top_pct, 1),
        "diversification_score": round(diversification, 1),
        "positions": len(holdings),
    }
