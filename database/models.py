"""
Database models and initialization for AI Document Explainer.

This module provides SQLAlchemy models for storing document analysis results
and utilities for database initialization with support for both SQLite and PostgreSQL.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create base class for models
Base = declarative_base()


class DocumentAnalysis(Base):
    """
    Model for storing document analysis results.
    
    Attributes:
        id: Primary key
        filename: Original filename of the uploaded document
        upload_timestamp: When the document was uploaded
        summary: AI-generated summary of the document
        important_points: List of important points extracted
        deadlines: List of deadlines mentioned in the document
        obligations: List of user obligations
        risks: List of potential risks
        recommended_next_steps: List of recommended actions
        action_items: List of specific action items
        confidence: AI confidence level in the analysis
    """
    __tablename__ = 'document_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    summary = Column(Text, nullable=True)
    important_points = Column(JSON, nullable=True)
    deadlines = Column(JSON, nullable=True)
    obligations = Column(JSON, nullable=True)
    risks = Column(JSON, nullable=True)
    recommended_next_steps = Column(JSON, nullable=True)
    action_items = Column(JSON, nullable=True)
    confidence = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<DocumentAnalysis(id={self.id}, filename='{self.filename}', timestamp={self.upload_timestamp})>"


def get_database_url():
    """
    Get database URL from environment variable or use default SQLite.
    
    Returns:
        str: Database connection URL
    """
    return os.getenv('DATABASE_URL', 'sqlite:///./documents.db')


def init_database():
    """
    Initialize database connection and create tables if they don't exist.
    
    Returns:
        tuple: (engine, Session) - SQLAlchemy engine and session maker
    """
    database_url = get_database_url()
    
    # Create engine
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging (development only)
        pool_pre_ping=True  # Verify connections before using them
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session maker
    Session = sessionmaker(bind=engine)
    
    return engine, Session


def save_analysis(session, filename, analysis_data):
    """
    Save document analysis to database.
    
    Args:
        session: SQLAlchemy session
        filename: Name of the uploaded file
        analysis_data: Dictionary containing analysis results
        
    Returns:
        DocumentAnalysis: The saved analysis object
    """
    analysis = DocumentAnalysis(
        filename=filename,
        summary=analysis_data.get('summary'),
        important_points=analysis_data.get('important_points'),
        deadlines=analysis_data.get('deadlines'),
        obligations=analysis_data.get('obligations'),
        risks=analysis_data.get('risks'),
        recommended_next_steps=analysis_data.get('recommended_next_steps'),
        action_items=analysis_data.get('action_items'),
        confidence=analysis_data.get('confidence')
    )
    
    session.add(analysis)
    session.commit()
    
    return analysis


def get_all_analyses(session):
    """
    Retrieve all document analyses from database.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        list: List of DocumentAnalysis objects
    """
    return session.query(DocumentAnalysis).order_by(DocumentAnalysis.upload_timestamp.desc()).all()


def delete_all_analyses(session):
    """
    Delete all document analyses from database.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        int: Number of records deleted
    """
    count = session.query(DocumentAnalysis).count()
    session.query(DocumentAnalysis).delete()
    session.commit()
    
    return count
