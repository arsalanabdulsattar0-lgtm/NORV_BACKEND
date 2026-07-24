from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])

@router.get("", response_model=List[schemas.BlogArticleOut])
def list_blogs(db: Session = Depends(get_db)):
    return crud.get_blogs(db)

@router.post("", response_model=schemas.BlogArticleOut, status_code=status.HTTP_201_CREATED)
def create_new_blog(
    blog: schemas.BlogArticleCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    return crud.create_blog(db, blog)

@router.put("/{blog_id}", response_model=schemas.BlogArticleOut)
def update_existing_blog(
    blog_id: int, 
    blog: schemas.BlogArticleCreate, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    updated = crud.update_blog(db, blog_id, blog)
    if not updated:
        raise HTTPException(status_code=404, detail="Blog article not found")
    return updated

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_blog(
    blog_id: int, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    deleted = crud.delete_blog(db, blog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blog article not found")
    return None
