from fastapi import FastAPI
from app.database import engine, Base
from app.api.router import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Organizational Structure API")
app.include_router(router, prefix="/departments", tags=["departments"])