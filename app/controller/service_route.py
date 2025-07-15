from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.security.jwt_handler import verify_token
from app.services import agent_service
from sqlalchemy.orm import Session
from app.db.data_base import get_db

router = APIRouter(prefix="/api", tags=["Services"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/submit/image")
def scan_receipt_image(image: UploadFile = File(...), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token missing user ID")
    return agent_service.scan_image(image.file, user_id, db)


@router.get("/successfulTransactions")
def get_successful_transactions(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token missing user ID")
    return agent_service.get_successful_transactions(user_id=user_id,db= db)


@router.get("/unsuccessfulTransactions")
def get_unsuccessful_transactions(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token missing user ID")
    return agent_service.get_unsuccessful_transactions(user_id=user_id,db= db)