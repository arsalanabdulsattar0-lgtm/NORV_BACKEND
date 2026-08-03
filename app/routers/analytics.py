from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import datetime
from ..database import get_db
from ..models import AnalyticsEvent
from ..schemas import AnalyticsEventCreate

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.post("/events", status_code=201)
def record_event(payload: AnalyticsEventCreate, db: Session = Depends(get_db)):
    """
    Public Endpoint: Storefront visitors send real-time event telemetry
    """
    try:
        evt_id = payload.eventId or f"evt-{int(datetime.datetime.utcnow().timestamp()*1000)}"
        event_obj = AnalyticsEvent(
            event_id=evt_id,
            event_type=payload.eventType,
            session_id=payload.sessionId,
            visitor_id=payload.visitorId,
            user_id=payload.userId,
            page=payload.page,
            product_id=str(payload.productId) if payload.productId else None,
            product_name=payload.productName,
            device=payload.device or "Mobile",
            browser=payload.browser or "Chrome",
            os=payload.os or "Android",
            country=payload.country or "Pakistan",
            city=payload.city or "Lahore",
            referrer=payload.referrer or "Direct",
            campaign=payload.campaign,
            properties=payload.properties or {}
        )
        db.add(event_obj)
        db.commit()
        db.refresh(event_obj)
        return {"status": "success", "event_id": event_obj.event_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@router.get("/events")
def get_events(limit: int = 500, db: Session = Depends(get_db)):
    """
    Admin Endpoint: Returns real-time telemetry events captured from all devices
    """
    events = db.query(AnalyticsEvent).order_by(AnalyticsEvent.timestamp.desc()).limit(limit).all()
    return [
        {
            "eventId": e.event_id,
            "eventType": e.event_type,
            "sessionId": e.session_id,
            "visitorId": e.visitor_id,
            "userId": e.user_id,
            "timestamp": int(e.timestamp.timestamp() * 1000) if e.timestamp else int(datetime.datetime.utcnow().timestamp() * 1000),
            "page": e.page,
            "productId": e.product_id,
            "productName": e.product_name,
            "device": e.device,
            "browser": e.browser,
            "os": e.os,
            "country": e.country,
            "city": e.city,
            "referrer": e.referrer,
            "campaign": e.campaign,
            "properties": e.properties or {}
        }
        for e in events
    ]

@router.delete("/events", status_code=204)
def purge_events(db: Session = Depends(get_db)):
    """
    Admin Endpoint: Clears all telemetry events for a fresh 0 state
    """
    db.query(AnalyticsEvent).delete()
    db.commit()
    return None
