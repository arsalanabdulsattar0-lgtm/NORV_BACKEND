from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, crud, schemas, auth

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_admin_user_by_email(db, form_data.username)
    # Check fallback username matching
    if not user:
        # Check if they entered username instead of email, or check initial fallback
        user = db.query(models.AdminUser).filter(models.AdminUser.name == form_data.username).first()
        
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or security passphrase.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate token
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role})
    
    # Update last active timestamp
    from datetime import datetime
    user.last_active = datetime.now().strftime("%B %d, %Y %I:%M %p")
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name
    }
