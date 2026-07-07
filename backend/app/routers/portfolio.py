"""
Portfolio Router — full portfolio management, trades, risk summary, performance.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.portfolio import Portfolio, Holding, Trade

router = APIRouter()


@router.get("")
def get_portfolio(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_default == True).first()
    if not portfolio:
        portfolio = Portfolio(user_id=user_id, name="My Portfolio", initial_capital=10000.00, cash=10000.00)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    total_invested = sum(h.shares * h.avg_buy_price for h in holdings)
    total_current = sum(h.shares * (h.current_price or h.avg_buy_price) for h in holdings)

    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "cash": float(portfolio.cash),
        "initial_capital": float(portfolio.initial_capital),
        "total_value": float(portfolio.cash) + total_current,
        "total_invested": total_invested,
        "unrealized_pnl": total_current - total_invested,
        "holdings_count": len(holdings),
        "holdings": [
            {
                "id": h.id, "company_id": h.company_id,
                "shares": float(h.shares), "avg_buy_price": float(h.avg_buy_price),
                "current_price": float(h.current_price) if h.current_price else None,
                "unrealized_pnl": float(h.unrealized_pnl) if h.unrealized_pnl else None,
                "unrealized_pnl_pct": float(h.unrealized_pnl_pct) if h.unrealized_pnl_pct else None,
                "weight_pct": float(h.weight_pct) if h.weight_pct else None,
            }
            for h in holdings
        ],
        "created_at": portfolio.created_at
    }


@router.get("/summary")
def get_portfolio_summary(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_default == True).first()
    if not portfolio:
        return {"total_value": 10000.00, "cash": 10000.00, "pnl": 0, "pnl_pct": 0, "positions": 0}

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    total_current = sum(h.shares * (h.current_price or h.avg_buy_price) for h in holdings)
    total_value = float(portfolio.cash) + total_current
    pnl = total_value - float(portfolio.initial_capital)
    pnl_pct = (pnl / float(portfolio.initial_capital)) * 100 if portfolio.initial_capital else 0

    return {
        "total_value": total_value,
        "cash": float(portfolio.cash),
        "invested": total_current,
        "pnl": pnl,
        "pnl_pct": round(pnl_pct, 2),
        "positions": len(holdings),
        "initial_capital": float(portfolio.initial_capital)
    }


@router.post("/trades", status_code=201)
def place_trade(
    company_id: int,
    side: str,
    shares: float,
    price: float,
    order_type: str = "market",
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_default == True).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    total_amount = shares * price

    if side == "buy":
        if float(portfolio.cash) < total_amount:
            raise HTTPException(status_code=400, detail="Insufficient cash")
        portfolio.cash = float(portfolio.cash) - total_amount

        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id, Holding.company_id == company_id
        ).first()
        if existing:
            total_shares = float(existing.shares) + shares
            existing.avg_buy_price = (
                (float(existing.shares) * float(existing.avg_buy_price)) + (shares * price)
            ) / total_shares
            existing.shares = total_shares
        else:
            holding = Holding(
                portfolio_id=portfolio.id, company_id=company_id,
                shares=shares, avg_buy_price=price, current_price=price
            )
            db.add(holding)

    elif side == "sell":
        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id, Holding.company_id == company_id
        ).first()
        if not existing or float(existing.shares) < shares:
            raise HTTPException(status_code=400, detail="Insufficient shares")
        existing.shares = float(existing.shares) - shares
        portfolio.cash = float(portfolio.cash) + total_amount
        if float(existing.shares) <= 0:
            db.delete(existing)
    else:
        raise HTTPException(status_code=400, detail="Invalid side. Use 'buy' or 'sell'.")

    trade = Trade(
        portfolio_id=portfolio.id, company_id=company_id, order_type=order_type,
        side=side, status="filled", shares=shares, price=price, total_amount=total_amount,
        executed_at=datetime.utcnow()
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {"id": trade.id, "message": f"Trade executed: {side} {shares} shares @ ${price:.2f}", "total": total_amount}


@router.get("/trades")
def get_trade_history(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_default == True).first()
    if not portfolio:
        return []
    trades = (
        db.query(Trade).filter(Trade.portfolio_id == portfolio.id)
        .order_by(Trade.executed_at.desc())
        .offset(offset).limit(limit).all()
    )
    return [
        {
            "id": t.id, "company_id": t.company_id, "side": t.side, "order_type": t.order_type,
            "shares": float(t.shares), "price": float(t.price), "total_amount": float(t.total_amount),
            "status": t.status, "executed_at": t.executed_at
        }
        for t in trades
    ]


@router.get("/risk-summary")
def get_portfolio_risk(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_default == True).first()
    if not portfolio:
        return {"concentration_risk": "none", "top_holding_pct": 0, "diversification_score": 100}

    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    if not holdings:
        return {"concentration_risk": "none", "top_holding_pct": 0, "diversification_score": 100}

    total = sum(float(h.shares) * float(h.current_price or h.avg_buy_price) for h in holdings)
    weights = sorted(
        [(float(h.shares) * float(h.current_price or h.avg_buy_price)) / total * 100 for h in holdings],
        reverse=True
    )

    top_pct = weights[0] if weights else 0
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
        "hhi_index": round(hhi, 1)
    }
