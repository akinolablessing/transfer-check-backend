from fastapi import APIRouter, Depends, File, UploadFile
from app.services import agent_service
from sqlalchemy.orm import Session
from app.db.data_base import get_db

router = APIRouter(prefix="/api", tags=["Services"])


@router.post("/submit/image")
def scan_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    return agent_service.scan_image(image.file)
