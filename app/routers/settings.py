from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas, auth, models

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=schemas.StoreSettingsOut)
def read_settings(
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.get_current_user)
):
    return crud.get_settings(db)

@router.put("", response_model=schemas.StoreSettingsOut)
def update_settings(
    settings_update: schemas.StoreSettingsBase, 
    db: Session = Depends(get_db),
    current_user: models.AdminUser = Depends(auth.check_super_admin)  # Super Admin restriction
):
    return crud.update_settings(db, settings_update)
