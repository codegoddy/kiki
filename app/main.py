from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.api import users

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI with PostgreSQL", version="1.0.0")

app.include_router(users.router, prefix="/api/v1", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with PostgreSQL"}