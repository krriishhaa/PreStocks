from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.alert import Alert, Notification
from app.schemas.alerts import (
    AlertCreate, AlertUpdate, AlertResponse,
    NotificationResponse, WatchlistCreate, WatchlistItemAdd,
    WatchlistResponse, WatchlistItemResponse, NewsResponse
)
from app.models.news import NewsArticle, NewsCompany

router = APIRouter()


# ─── ALERTS ───

@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    is_active: Optional[bool] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query = db.query(Alert).filter(Alert.user_id == user_id)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    return query.order_by(Alert.created_at.desc()).all()


@router.post("/alerts", response_model=AlertResponse, status_code=201)
def create_alert(
    payload: AlertCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    alert = Alert(
        user_id=user_id,
        company_id=payload.company_id,
        alert_type=payload.alert_type,
        condition=payload.condition,
        title=payload.title,
        message=payload.message,
        cooldown_hours=payload.cooldown_hours
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()


# ─── NOTIFICATIONS ───

@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    limit: int = Query(default=50, le=200),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    from datetime import datetime
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return {"status": "read"}


@router.post("/notifications/read-all")
def mark_all_notifications_read(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    db.query(Notification).filter(
        Notification.user_id == user_id, Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"status": "all_read"}


@router.get("/notifications/unread-count")
def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    count = db.query(Notification).filter(
        Notification.user_id == user_id, Notification.is_read == False
    ).count()
    return {"unread_count": count}
