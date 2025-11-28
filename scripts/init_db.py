#!/usr/bin/env python3
"""
Script to initialize the database.
"""
from app.database import engine
from app.models import Base

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()