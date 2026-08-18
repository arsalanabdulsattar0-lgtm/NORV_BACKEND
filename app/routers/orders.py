from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models
from ..mailer import (
    send_order_confirmation_email,
    send_order_shipped_email,
    send_out_for_delivery_email,
    send_order_delivered_email,
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", response_model=List[schemas.OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    return crud.get_orders(db)


@router.get("/{order_id}", response_model=schemas.OrderOut)
def read_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_new_order(
    order: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create order and send confirmation email to customer."""
    created_order = crud.create_order(db, order)

    order_data = {
        "id":            created_order.id,
        "name":          created_order.name,
        "email":         created_order.email,
        "phone":         created_order.phone,
        "address":       created_order.address,
        "city":          created_order.city,
        "paymentMethod": created_order.payment_method,
        "total":         created_order.total,
        "items":         created_order.items or [],
    }
    background_tasks.add_task(send_order_confirmation_email, order_data)
    return created_order


@router.put("/{order_id}", response_model=schemas.OrderOut)
def update_existing_order(
    order_id: str,
    order: schemas.OrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    """Update order. Sends email when status changes to Shipped / Out for Delivery / Delivered."""
    old_order = crud.get_order(db, order_id)
    if not old_order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = old_order.status
    updated    = crud.update_order(db, order_id, order)
    new_status = updated.status

    # Trigger email only when status actually changed
    if new_status and new_status != old_status:
        order_data = {
            "id":                 updated.id,
            "name":               updated.name,
            "email":              updated.email,
            "phone":              updated.phone,
            "address":            updated.address,
            "city":               updated.city,
            "payment_method":     updated.payment_method,
            "total":              updated.total,
            "items":              updated.items or [],
            "tracking_number":    updated.tracking_number,
            "estimated_delivery": updated.estimated_delivery,
        }

        if new_status == "Shipped":
            background_tasks.add_task(send_order_shipped_email, order_data)
        elif new_status == "Out for Delivery":
            background_tasks.add_task(send_out_for_delivery_email, order_data)
        elif new_status == "Delivered":
            background_tasks.add_task(send_order_delivered_email, order_data)

    return updated


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    crud.delete_order(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
