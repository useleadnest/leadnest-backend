from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    trial_ends_at: Optional[datetime]
    subscription_status: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Lead schemas
class LeadBase(BaseModel):
    business_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

class LeadCreate(LeadBase):
    search_id: int

class Lead(LeadBase):
    id: int
    search_id: int
    ai_email_message: Optional[str] = None
    ai_sms_message: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search schemas
class SearchBase(BaseModel):
    location: str
    trade: str

class SearchCreate(SearchBase):
    pass

class Search(SearchBase):
    id: int
    user_id: int
    results_count: int
    created_at: datetime
    leads: List[Lead] = []
    
    class Config:
        from_attributes = True

# Export schemas
class ExportCreate(BaseModel):
    search_id: int
    export_type: str  # csv, webhook

class Export(BaseModel):
    id: int
    user_id: int
    search_id: int
    export_type: str
    leads_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_searches: int
    total_leads: int
    total_exports: int
    trial_days_left: Optional[int] = None
