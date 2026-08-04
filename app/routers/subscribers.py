from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from .. import models, schemas, auth
from ..mailer import send_subscriber_confirmation_email, send_admin_new_subscriber_alert_email

router = APIRouter(prefix="/api/subscribers", tags=["Subscribers"])


# ─── PUBLIC: Subscribe (no auth required) ────────────────────────────────────
@router.post("", response_model=schemas.SubscriberOut, status_code=201)
def subscribe(
    payload: schemas.SubscriberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register an email for bundle launch notifications."""
    existing = db.query(models.Subscriber).filter(
        models.Subscriber.email == payload.email
    ).first()

    if existing:
        # Already subscribed — re-activate if unsubscribed
        existing.status = "Subscribed"
        db.commit()
        db.refresh(existing)
        return existing

    subscriber = models.Subscriber(
        email=payload.email,
        source=payload.source or "Launch Queue",
        status="Subscribed"
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    # Fire confirmation + admin alert emails in background (non-blocking)
    total = db.query(models.Subscriber).count()
    background_tasks.add_task(
        send_subscriber_confirmation_email,
        subscriber.email,
        subscriber.source or "NORV Newsletter"
    )
    background_tasks.add_task(
        send_admin_new_subscriber_alert_email,
        subscriber.email,
        subscriber.source or "NORV Newsletter",
        total
    )

    return subscriber


# ─── ADMIN: List all subscribers ─────────────────────────────────────────────
@router.get("", response_model=List[schemas.SubscriberOut])
def get_subscribers(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    """Retrieve all launch queue subscribers (admin only)."""
    return db.query(models.Subscriber).order_by(models.Subscriber.id.desc()).all()


# ─── ADMIN: Update subscriber status ─────────────────────────────────────────
@router.put("/{subscriber_id}", response_model=schemas.SubscriberOut)
def update_subscriber(
    subscriber_id: int,
    payload: schemas.SubscriberUpdate,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    """Update a subscriber's status (Active / Unsubscribed)."""
    subscriber = db.query(models.Subscriber).filter(
        models.Subscriber.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    if payload.status is not None:
        subscriber.status = payload.status

    db.commit()
    db.refresh(subscriber)
    return subscriber


# ─── ADMIN: Delete subscriber ─────────────────────────────────────────────────
@router.delete("/{subscriber_id}")
def delete_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    """Permanently remove a subscriber from the registry."""
    subscriber = db.query(models.Subscriber).filter(
        models.Subscriber.id == subscriber_id
    ).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    db.delete(subscriber)
    db.commit()
    return {"detail": "Subscriber deleted"}


# ─── ADMIN: Bulk email dispatch ───────────────────────────────────────────────
from pydantic import BaseModel as _BM

class BulkEmailPayload(_BM):
    subject: str
    message: str
    bundle_filter: str | None = None  # None = all, else filter by bundle name


@router.post("/send-bulk-email")
def send_bulk_email(
    payload: BulkEmailPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    """Dispatch a custom email to all active (or filtered) launch subscribers."""
    from ..mailer import _send, _base_template, GOLD, MUTED, TEXT

    query = db.query(models.Subscriber).filter(models.Subscriber.status == "Subscribed")
    if payload.bundle_filter:
        query = query.filter(models.Subscriber.source == payload.bundle_filter)

    subscribers = query.all()
    if not subscribers:
        raise HTTPException(status_code=404, detail="No active subscribers found for the given filter")

    safe_message = payload.message.replace("\n", "<br>")

    content = f"""
    <h2 style="margin:0 0 8px;font-size:22px;color:{TEXT};font-weight:400;">
      A message from <span style="color:{GOLD};">NORV Atelier</span>
    </h2>
    <div style="background:#0D0D0D;border-radius:8px;padding:24px;margin:24px 0;color:{TEXT};font-size:14px;line-height:1.8;">
      {safe_message}
    </div>
    <div style="margin-top:24px;text-align:center;">
      <a href="https://shopnorv.com" style="display:inline-block;background:{GOLD};color:#000;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;font-size:14px;letter-spacing:1px;">
        SHOP NORV
      </a>
    </div>
    <p style="margin:28px 0 0;font-size:12px;color:{MUTED};">
      You received this because you signed up for NORV launch notifications.
    </p>"""

    html = _base_template(content)

    dispatched = 0
    for sub in subscribers:
        background_tasks.add_task(_send, sub.email, payload.subject, html)
        dispatched += 1

    return {
        "detail": f"Dispatched to {dispatched} subscriber(s)",
        "count": dispatched
    }
