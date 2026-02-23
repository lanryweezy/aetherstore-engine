# test_api_structure.py
# Test script to verify the new API structure

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_api_imports():
    """Test that all API modules can be imported"""
    try:
        # Test importing individual API modules
        from api import users
        print("[PASS] Users API module imported successfully")
        
        from api import stores
        print("[PASS] Stores API module imported successfully")
        
        from api import products
        print("[PASS] Products API module imported successfully")
        
        from api import avatars
        print("[PASS] Avatars API module imported successfully")
        
        from api import tryon
        print("[PASS] Try-on API module imported successfully")
        
        # Test that the main API router can be imported
        from api import api_router
        print("[PASS] Main API router imported successfully")
        
        print("\n[PASS] All API modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

def test_database_imports():
    """Test that database modules can be imported"""
    try:
        from database import Base, engine, SessionLocal, get_db, init_db
        print("[PASS] Database modules imported successfully")
        
        from models import User, Brand, Store, Product
        print("[PASS] Database models imported successfully")
        
        from crud import get_user, create_user, update_user, delete_user
        print("[PASS] CRUD operations imported successfully")
        
        print("\n[PASS] All database modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Database import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected database error: {e}")
        return False

def test_auth_imports():
    """Test that auth modules can be imported"""
    try:
        from auth import verify_password, get_password_hash, create_access_token
        from auth import authenticate_user, get_current_user, get_current_active_user
        print("[PASS] Auth modules imported successfully")
        
        print("\n[PASS] All auth modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"[FAIL] Auth import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected auth error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Aetherstore Engine API Structure...\n")
    
    success = True
    
    print("1. Testing API module imports:")
    success &= test_api_imports()
    
    print("\n2. Testing database module imports:")
    success &= test_database_imports()
    
    print("\n3. Testing auth module imports:")
    success &= test_auth_imports()
    
    if success:
        print("\n[PASS] All tests passed! The new API structure is working correctly.")
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")