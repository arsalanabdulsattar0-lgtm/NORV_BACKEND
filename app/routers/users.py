from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/users", tags=["Admin Users"])

@router.get("", response_model=List[schemas.AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.check_super_admin)  # Super Admin restriction
):
    return crud.get_admin_users(db)

@router.post("", response_model=schemas.AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user: schemas.AdminUserCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.check_super_admin)  # Super Admin restriction
):
    existing = crud.get_admin_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    return crud.create_admin_user(db, user)

@router.put("/{user_id}", response_model=schemas.AdminUserOut)
def update_existing_user(
    user_id: int, 
    user_update: schemas.AdminUserUpdate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.check_super_admin)  # Super Admin restriction
):
    updated = crud.update_admin_user(db, user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.check_super_admin)  # Super Admin restriction
):
    success = crud.delete_admin_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
