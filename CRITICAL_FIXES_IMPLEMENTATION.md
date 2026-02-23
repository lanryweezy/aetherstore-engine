# Critical Fixes - Implementation Guide
**Quick fixes for the 5 most critical issues**

---

## Fix #1: Duplicate Database Session Function (30 min)

### Current Problem
`backend/database.py` has `get_db()` defined twice, breaking FastAPI dependency injection.

### Solution

**File:** `backend/database.py`

Replace the entire file with:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool if settings.ENVIRONMENT == "testing" else None,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency for database session.
    Usage: Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """
    Context manager for database session.
    Usage: with get_db_session() as db:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
```

### Verification
```python
# In main_app.py, verify this works:
from fastapi import Depends
from database import get_db

@app.get("/api/test")
async def test_db(db: Session = Depends(get_db)):
    # This should work without errors
    return {"status": "ok"}
```

---

## Fix #2: Hardcoded SECRET_KEY (1 hour)

### Current Problem
`backend/config.py` has default SECRET_KEY exposed in code.

### Solution

**File:** `backend/config.py`

Replace with:

```python
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Aetherstore Engine"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # Required
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Security settings - CRITICAL
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)  # Required, min 32 chars
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS settings
    CORS_ORIGINS: list = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
        ],
        env="CORS_ORIGINS"
    )
    
    # Payment settings
    STRIPE_API_KEY: str = Field(default="", env="STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")
    PAYSTACK_API_KEY: str = Field(default="", env="PAYSTACK_API_KEY")
    
    # Email settings
    EMAIL_PROVIDER: str = Field(default="smtp", env="EMAIL_PROVIDER")
    EMAIL_SENDGRID_API_KEY: str = Field(default="", env="EMAIL_SENDGRID_API_KEY")
    EMAIL_MAILGUN_API_KEY: str = Field(default="", env="EMAIL_MAILGUN_API_KEY")
    EMAIL_MAILGUN_DOMAIN: str = Field(default="", env="EMAIL_MAILGUN_DOMAIN")
    SMTP_HOST: str = Field(default="localhost", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    
    # Monitoring settings
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY is not default and meets requirements"""
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError(
                "SECRET_KEY must be set via environment variable and must be at least 32 characters. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v):
        """Validate DATABASE_URL is set"""
        if not v:
            raise ValueError("DATABASE_URL must be set via environment variable")
        return v
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Load settings
settings = Settings()

# Validate critical settings on startup
def validate_settings():
    """Validate all critical settings are configured"""
    errors = []
    
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY not properly configured")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL not configured")
    
    if settings.ENVIRONMENT == "production":
        if not settings.STRIPE_API_KEY:
            errors.append("STRIPE_API_KEY required in production")
        if settings.DEBUG:
            errors.append("DEBUG must be False in production")
        if settings.CORS_ORIGINS == ["*"]:
            errors.append("CORS_ORIGINS must be specific in production")
    
    if errors:
        logger.error(f"Configuration errors: {', '.join(errors)}")
        raise RuntimeError(f"Configuration validation failed: {', '.join(errors)}")
    
    logger.info(f"Configuration validated for {settings.ENVIRONMENT} environment")
```

### Create `.env.example`

**File:** `backend/.env.example`

```env
# Application
DEBUG=false
ENVIRONMENT=development
APP_NAME=Aetherstore Engine

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aetherstore_dev
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Security - GENERATE NEW SECRET KEY!
# Run: python -c 'import secrets; print(secrets.token_urlsafe(32))'
SECRET_KEY=your-generated-secret-key-here-min-32-chars

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Payment
STRIPE_API_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
PAYSTACK_API_KEY=pk_test_xxx

# Email
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
REDIS_URL=redis://localhost:6379
```

### Update `backend/main_app.py`

Add startup validation:

```python
from config import settings, validate_settings

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    validate_settings()
    logger.info(f"Starting Aetherstore Engine in {settings.ENVIRONMENT} mode")
```

---

## Fix #3: Weak Permission System (4 hours)

### Current Problem
Admin check based on email string: `if "admin" in current_user.email.lower()`

### Solution

**Step 1:** Update `backend/models.py`

Add role model:

```python
from enum import Enum
from sqlalchemy import Column, String, Enum as SQLEnum

class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    BRAND = "brand"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"
    
    id: str = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: str = Column(String, unique=True, index=True)
    password_hash: str = Column(String)
    role: UserRole = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, index=True)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    avatars = relationship("UserAvatar", back_populates="user")
```

**Step 2:** Update `backend/auth.py`

Replace permission checking:

```python
from functools import wraps
from fastapi import HTTPException, status
from models import UserRole

def require_role(*allowed_roles: UserRole):
    """
    Decorator to require specific roles
    Usage: @require_role(UserRole.ADMIN, UserRole.BRAND)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires one of these roles: {', '.join([r.value for r in allowed_roles])}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def is_admin(current_user: User) -> bool:
    """Check if user is admin"""
    return current_user.role == UserRole.ADMIN

def is_brand(current_user: User) -> bool:
    """Check if user is brand"""
    return current_user.role == UserRole.BRAND

def is_customer(current_user: User) -> bool:
    """Check if user is customer"""
    return current_user.role == UserRole.CUSTOMER
```

**Step 3:** Update API endpoints

**File:** `backend/api/users.py`

```python
from auth import require_role
from models import UserRole

@router.post("/api/admin/users")
@require_role(UserRole.ADMIN)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create user - Admin only"""
    # Create user logic
    pass

@router.get("/api/admin/users")
@require_role(UserRole.ADMIN)
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users - Admin only"""
    pass

@router.post("/api/brand/stores")
@require_role(UserRole.BRAND, UserRole.ADMIN)
async def create_store(
    store_data: StoreCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create store - Brand or Admin"""
    pass
```

**Step 4:** Create migration

```bash
cd backend
alembic revision --autogenerate -m "Add user roles"
alembic upgrade head
```

---

## Fix #4: Add CSRF Protection (2 hours)

### Solution

**File:** `backend/main_app.py`

```python
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = settings.SECRET_KEY

@CsrfProtect.load_config
def load_config():
    return CsrfSettings()

# Add CSRF middleware
app.add_middleware(CsrfProtect)

# Add CSRF token endpoint
@app.get("/api/csrf-token")
async def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    """Get CSRF token for forms"""
    return {"csrf_token": csrf_protect.generate_csrf()}
```

**File:** `backend/api/orders.py`

```python
from fastapi_csrf_protect import CsrfProtect

@router.post("/api/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    """Create order with CSRF protection"""
    await csrf_protect.validate_csrf(request)
    # Create order logic
    pass
```

**File:** `frontend/js/api-client.js`

```javascript
class APIClient {
    async getCsrfToken() {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        return data.csrf_token;
    }
    
    async post(url, data) {
        const csrfToken = await this.getCsrfToken();
        
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify(data)
        });
    }
}
```

---

## Fix #5: Add Password Validation (1 hour)

### Solution

**File:** `backend/schemas.py` (create if doesn't exist)

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=12, max_length=128)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        errors = []
        
        if len(v) < 12:
            errors.append('at least 12 characters')
        
        if not re.search(r'[A-Z]', v):
            errors.append('uppercase letter')
        
        if not re.search(r'[a-z]', v):
            errors.append('lowercase letter')
        
        if not re.search(r'[0-9]', v):
            errors.append('digit')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', v):
            errors.append('special character')
        
        if errors:
            raise ValueError(f'Password must contain: {", ".join(errors)}')
        
        return v

class UserLogin(BaseModel):
    email: str
    password: str
```

**File:** `backend/api/auth.py`

```python
from schemas import UserCreate, UserLogin
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user with password validation"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    
    return {"message": "User registered successfully"}

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with rate limiting"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```

---

## Installation & Testing

### Install dependencies
```bash
cd backend
pip install fastapi-csrf-protect slowapi
```

### Test the fixes
```bash
# Test database connection
python -c "from database import get_db; print('✓ Database OK')"

# Test config validation
python -c "from config import settings, validate_settings; validate_settings(); print('✓ Config OK')"

# Test RBAC
python -c "from models import UserRole; print('✓ RBAC OK')"

# Run server
python -m main_app
```

---

## Deployment Checklist

- [ ] Generate new SECRET_KEY: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`
- [ ] Set all environment variables in `.env`
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Test all endpoints with new security
- [ ] Update frontend CSRF handling
- [ ] Test login rate limiting
- [ ] Verify password validation works
- [ ] Test admin/brand/customer role separation

---

**Estimated Time:** ~8 hours total
**Impact:** Eliminates 5 critical security vulnerabilities
