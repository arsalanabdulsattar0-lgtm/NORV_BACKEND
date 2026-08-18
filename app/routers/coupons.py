from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/coupons", tags=["Coupons"])

@router.get("", response_model=List[schemas.CouponOut])
def list_coupons(db: Session = Depends(get_db)):
    return crud.get_coupons(db)

@router.get("/validate/{code}")
def validate_coupon_code(code: str, db: Session = Depends(get_db)):
    code_clean = code.strip().upper()
    coupon = db.query(models.Coupon).filter(models.Coupon.code == code_clean, models.Coupon.status == "Active").first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid or expired promo code")
    return {
        "valid": True,
        "code": coupon.code,
        "type": coupon.type,
        "value": coupon.value,
        "discount_percent": coupon.value if coupon.type == "percentage" else 25
    }

@router.post("", response_model=schemas.CouponOut, status_code=status.HTTP_201_CREATED)
def create_new_coupon(
    coupon: schemas.CouponCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    return crud.create_coupon(db, coupon)

@router.put("/{coupon_id}", response_model=schemas.CouponOut)
def update_existing_coupon(
    coupon_id: int, 
    coupon: schemas.CouponCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    updated = crud.update_coupon(db, coupon_id, coupon)
    if not updated:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return updated

@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_coupon(
    coupon_id: int, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    deleted = crud.delete_coupon(db, coupon_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return None
