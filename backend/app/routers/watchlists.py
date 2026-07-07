from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.security import get_current_user_id
from app.schemas.alerts import WatchlistCreate, WatchlistItemAdd, WatchlistResponse, WatchlistItemResponse

router = APIRouter()


@router.get("/", response_model=List[WatchlistResponse])
def list_watchlists(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Watchlist, WatchlistItem
    watchlists = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
    result = []
    for wl in watchlists:
        count = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == wl.id).count()
        result.append(WatchlistResponse(
            id=wl.id, user_id=wl.user_id, name=wl.name,
            description=wl.description, is_default=wl.is_default,
            items_count=count, created_at=wl.created_at
        ))
    return result


@router.post("/", response_model=WatchlistResponse, status_code=201)
def create_watchlist(
    payload: WatchlistCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Watchlist
    wl = Watchlist(user_id=user_id, name=payload.name, description=payload.description)
    db.add(wl)
    db.commit()
    db.refresh(wl)
    return WatchlistResponse(
        id=wl.id, user_id=wl.user_id, name=wl.name,
        description=wl.description, is_default=wl.is_default,
        items_count=0, created_at=wl.created_at
    )


@router.get("/{watchlist_id}/items", response_model=List[WatchlistItemResponse])
def list_watchlist_items(
    watchlist_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Watchlist, WatchlistItem
    from app.models.company import Company

    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    items = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).all()
    result = []
    for item in items:
        company = db.query(Company).filter(Company.id == item.company_id).first()
        result.append(WatchlistItemResponse(
            id=item.id, watchlist_id=item.watchlist_id, company_id=item.company_id,
            company_name=company.name if company else None,
            company_ticker=company.ticker if company else None,
            notes=item.notes, target_price=item.target_price,
            alert_above=item.alert_above, alert_below=item.alert_below,
            added_at=item.added_at
        ))
    return result


@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=201)
def add_watchlist_item(
    watchlist_id: int,
    payload: WatchlistItemAdd,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Watchlist, WatchlistItem
    from app.models.company import Company

    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    existing = db.query(WatchlistItem).filter(
        WatchlistItem.watchlist_id == watchlist_id, WatchlistItem.company_id == payload.company_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Company already in watchlist")

    item = WatchlistItem(
        watchlist_id=watchlist_id, company_id=payload.company_id,
        notes=payload.notes, target_price=payload.target_price,
        alert_above=payload.alert_above, alert_below=payload.alert_below
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    company = db.query(Company).filter(Company.id == item.company_id).first()
    return WatchlistItemResponse(
        id=item.id, watchlist_id=item.watchlist_id, company_id=item.company_id,
        company_name=company.name if company else None,
        company_ticker=company.ticker if company else None,
        notes=item.notes, target_price=item.target_price,
        alert_above=item.alert_above, alert_below=item.alert_below,
        added_at=item.added_at
    )


@router.delete("/{watchlist_id}/items/{item_id}", status_code=204)
def remove_watchlist_item(
    watchlist_id: int,
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.models.portfolio import Watchlist, WatchlistItem

    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == user_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")

    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id, WatchlistItem.watchlist_id == watchlist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
