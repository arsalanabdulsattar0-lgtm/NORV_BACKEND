from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.post("", response_model=schemas.CategoryOut, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    return crud.create_category(db, category)

@router.put("/{cat_id}", response_model=schemas.CategoryOut)
def update_existing_category(
    cat_id: int, 
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    updated = crud.update_category(db, cat_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_category(
    cat_id: int, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    deleted = crud.delete_category(db, cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return None
