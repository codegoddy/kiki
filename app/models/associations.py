"""
Database association tables for many-to-many relationships.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table
from datetime import datetime


# Association table for many-to-many relationship between posts and categories
post_category_association = Table(
    'post_category_association',
    # Base.metadata,  # This will be updated after all models are created
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)