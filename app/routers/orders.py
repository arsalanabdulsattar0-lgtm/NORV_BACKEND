from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models
from ..mailer import send_order_confirmation_email

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
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
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
    # Create the order in the database first
    created_order = crud.create_order(db, order)
    
    # Build the order data dict for the email template
    order_data = {
        "id": created_order.id,
        "name": created_order.name,
        "email": created_order.email,
        "phone": created_order.phone,
        "address": created_order.address,
        "city": created_order.city,
        "paymentMethod": created_order.payment_method,
        "total": created_order.total,
        "items": [
            {
                "name": item.get("name", "Product"),
                "size": item.get("size", "Standard"),
                "quantity": item.get("quantity", 1),
                "price": item.get("price", 0)
            }
            for item in (created_order.items or [])
        ]
    }
    
    # Send confirmation email in background (non-blocking)
    background_tasks.add_task(send_order_confirmation_email, order_data)
    
    return created_order

@router.put("/{order_id}", response_model=schemas.OrderOut)
def update_existing_order(
    order_id: str, 
    order: schemas.OrderUpdate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    updated = crud.update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_order(
    order_id: str, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    deleted = crud.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return None
