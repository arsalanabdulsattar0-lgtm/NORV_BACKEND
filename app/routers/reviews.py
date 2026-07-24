from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

@router.get("", response_model=List[schemas.ReviewOut])
def list_reviews(db: Session = Depends(get_db)):
    return crud.get_reviews(db)

@router.post("", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_new_review(
    review: schemas.ReviewCreate, 
    db: Session = Depends(get_db)
):
    return crud.create_review(db, review)

@router.put("/{review_id}", response_model=schemas.ReviewOut)
def update_existing_review(
    review_id: int, 
    review: schemas.ReviewUpdate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    updated = crud.update_review(db, review_id, review)
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_review(
    review_id: int, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    deleted = crud.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return None
