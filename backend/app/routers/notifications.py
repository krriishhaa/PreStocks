"""
Notifications Router — user alerts, notifications, preferences.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.alert import Alert, Notification

router = APIRouter()


# ─── ALERTS (user-created triggers) ───

@router.get("/alerts", response_model=list)
def list_alerts(
    is_active: Optional[bool] = True,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query = db.query(Alert).filter(Alert.user_id == user_id)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    alerts = query.order_by(Alert.created_at.desc()).all()
    return [
        {
            "id": a.id, "alert_type": a.alert_type, "company_id": a.company_id,
            "condition_value": float(a.condition_value) if a.condition_value else None,
            "condition_json": a.condition_json, "title": a.title, "message": a.message,
            "is_active": a.is_active, "is_triggered": a.is_triggered,
            "triggered_at": a.triggered_at, "created_at": a.created_at
        }
        for a in alerts
    ]


@router.post("/alerts", status_code=201)
def create_alert(
    alert_type: str,
    company_id: Optional[int] = None,
    condition_value: Optional[float] = None,
    title: Optional[str] = None,
    message: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    alert = Alert(
        user_id=user_id, company_id=company_id, alert_type=alert_type,
        condition_value=condition_value, title=title, message=message
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "message": "Alert created"}


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


@router.patch("/alerts/{alert_id}/toggle")
def toggle_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == user_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_active = not alert.is_active
    db.commit()
    return {"id": alert.id, "is_active": alert.is_active}


# ─── NOTIFICATIONS (system-generated) ───

@router.get("/", response_model=list)
def list_notifications(
    is_read: Optional[bool] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    return [
        {
            "id": n.id, "title": n.title, "body": n.body, "channel": n.channel,
            "action_url": n.action_url, "is_read": n.is_read,
            "metadata": n.metadata_, "created_at": n.created_at
        }
        for n in notifications
    ]


@router.get("/unread-count")
def unread_count(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(
        Notification.user_id == user_id, Notification.is_read == False
    ).count()
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == user_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()
    return {"id": notif.id, "is_read": True}


@router.post("/mark-all-read")
def mark_all_read(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.user_id == user_id, Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()
    return {"message": "All notifications marked as read"}
