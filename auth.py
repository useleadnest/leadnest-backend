from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from database import get_db
from schemas import UserCreate, UserLogin, User as UserSchema, Token
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    create_user, 
    get_user_by_email, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    try:
        db_user = create_user(db, email=user.email, password=user.password)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)) -> Any:
    """
    Login user and return access token
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: UserSchema = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information based on token
    """
    return current_user

@router.get("/test")
async def test_auth_router():
    """
    Test endpoint to verify router is loaded
    """
    return {
        "message": "Auth router is working",
        "endpoints": ["/register", "/login", "/me", "/test"]
    }
