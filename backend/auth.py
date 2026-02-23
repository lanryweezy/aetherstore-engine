# auth.py
# Authentication and authorization for Aetherstore Engine

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import uuid
from models import User
from database import get_db
import logging
from config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key and algorithm for JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    try:
        with get_db_session() as db:
            user = db.query(User).filter(User.email == email).first()
            if user and verify_password(password, user.password_hash):
                return user
        return None
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        return None

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise credentials_exception
            return user
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_user_account(email: str, password: str, name: str) -> Optional[User]:
    """Create a new user account"""
    try:
        with get_db_session() as db:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Hash password
            hashed_password = get_password_hash(password)
            
            # Create new user
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "name": name,
                "password_hash": hashed_password,
                "is_active": True
            }
            
            db_user = User(**user_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Created new user account: {email}")
            return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user account: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating user account")

def login_user(form_data: OAuth2PasswordRequestForm):
    """Login a user and return access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def change_user_password(user_id: str, old_password: str, new_password: str) -> bool:
    """Change a user's password"""
    try:
        with get_db_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify old password
            if not verify_password(old_password, user.password_hash):
                raise HTTPException(status_code=400, detail="Incorrect current password")
            
            # Hash new password
            new_hashed_password = get_password_hash(new_password)
            user.password_hash = new_hashed_password
            db.commit()
            
            logger.info(f"Changed password for user: {user.email}")
            return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing user password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error changing password")

def reset_user_password(email: str, new_password: str) -> bool:
    """Reset a user's password (typically used with email verification)"""
    try:
        with get_db_session() as db:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Hash new password
            new_hashed_password = get_password_hash(new_password)
            user.password_hash = new_hashed_password
            db.commit()
            
            logger.info(f"Reset password for user: {email}")
            return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting user password: {str(e)}")
        raise HTTPException(status_code=500, detail="Error resetting password")

# Permission checking functions
def require_permission(required_permission: str):
    """Decorator to require specific permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        # In a real implementation, this would check user permissions
        # For now, we'll allow all authenticated users
        return current_user
    return permission_checker

# Admin permission checker
def require_admin_permission(current_user: User = Depends(get_current_active_user)):
    """Require admin permissions"""
    # In a real implementation, this would check if user has admin role
    # For now, we'll check if user email contains "admin"
    if "admin" in current_user.email.lower():
        return current_user
    raise HTTPException(status_code=403, detail="Admin permission required")