import shutil

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller.service_route import router
from app.db.data_base import Base, engine

from app.controller.auth import router as auth_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "http://172.16.0.117:8000"

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Transfer Check API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
@app.get("/tesseract-check")
def check_tesseract():
    return {"tesseract_path": shutil.which("tesseract")}

if __name__ == "__main__":
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)