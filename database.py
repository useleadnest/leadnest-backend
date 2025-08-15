from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import logging
from config import config

logger = logging.getLogger(__name__)

# Database setup with error handling
try:
    engine = create_engine(
        config.database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=(config.environment == "development")  # Log SQL in development
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {str(e)}")
    raise

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trial_ends_at = Column(DateTime(timezone=True))
    subscription_status = Column(String, default="trial")  # trial, active, cancelled
    stripe_customer_id = Column(String)

class Search(Base):
    __tablename__ = "searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    location = Column(String)
    trade = Column(String)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, index=True)
    business_name = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    address = Column(String)
    category = Column(String)
    rating = Column(Float)
    review_count = Column(Integer)
    ai_email_message = Column(Text)
    ai_sms_message = Column(Text)
    quality_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Export(Base):
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    search_id = Column(Integer, index=True)
    export_type = Column(String)  # csv, webhook
    leads_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
