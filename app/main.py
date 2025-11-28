from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base
from app.api import users, auth, posts, comments
from app.middleware import log_requests

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI with PostgreSQL", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(log_requests)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(posts.router, prefix="/api/v1", tags=["posts"])
app.include_router(comments.router, prefix="/api/v1", tags=["comments"])

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with PostgreSQL"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}