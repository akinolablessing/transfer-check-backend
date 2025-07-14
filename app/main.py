from fastapi import FastAPI

from app.controller.service_route import router
from app.db.data_base import Base, engine

from app.controller.auth import router as auth_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Transfer Check API"}
