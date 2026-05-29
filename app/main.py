from fastapi import FastAPI
from app.database import engine, Base
from app.v1.router import router as v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Organizational Structure API")
app.include_router(v1_router, prefix="/departments", tags=["departments"])