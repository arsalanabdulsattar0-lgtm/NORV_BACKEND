from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/media", tags=["Media Assets"])

@router.get("", response_model=List[schemas.MediaAssetOut])
def get_all_media(db: Session = Depends(get_db)):
    return crud.get_media_assets(db)

@router.post("", response_model=schemas.MediaAssetOut)
def upload_media(asset: schemas.MediaAssetCreate, db: Session = Depends(get_db)):
    return crud.create_media_asset(db, asset)

@router.delete("/{asset_id}")
def remove_media(asset_id: str, db: Session = Depends(get_db)):
    success = crud.delete_media_asset(db, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return {"message": "Media asset deleted successfully"}
