# verify_structure.py
# Simple script to verify the new modular structure

def verify_modular_structure():
    """Verify that all components can be imported without errors"""
    print("Verifying Aetherstore Engine Modular Structure...")
    
    try:
        # Test importing database components
        print("\n1. Testing database components:")
        from database import Base, engine, SessionLocal, get_db_session, init_db
        print("   [PASS] Database components imported successfully")
        
        # Test importing models
        print("\n2. Testing database models:")
        from models import User, Brand, Store, Product, ProductImage, UserAvatar
        from models import TryOnSession, ShoppingCart, CartItem, Order, OrderItem
        from models import StoreAnalytics, ProductAnalytics, AIModelPerformance
        from models import Asset, BrandTemplate
        print("   [PASS] All database models imported successfully")
        
        # Test importing CRUD operations
        print("\n3. Testing CRUD operations:")
        from crud import get_user, create_user, update_user, delete_user
        from crud import get_brand, create_brand, update_brand, delete_brand
        from crud import get_store, create_store, update_store, delete_store
        from crud import get_product, create_product, update_product, delete_product
        from crud import get_user_avatar, create_user_avatar, update_user_avatar, delete_user_avatar
        print("   [PASS] CRUD operations imported successfully")
        
        # Test importing auth components
        print("\n4. Testing authentication components:")
        from auth import get_password_hash, verify_password, create_access_token
        from auth import get_current_active_user, create_user_account, change_user_password
        print("   [PASS] Authentication components imported successfully")
        
        # Test importing API modules
        print("\n5. Testing API modules:")
        from api import users, stores, products, avatars, tryon
        print("   [PASS] API modules imported successfully")
        
        # Test importing main API router
        print("\n6. Testing main API router:")
        from api import api_router
        print("   [PASS] Main API router imported successfully")
        
        print("\n[PASS] All components verified successfully!")
        print("The modular structure is ready for implementation.")
        return True
        
    except ImportError as e:
        print(f"\n[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = verify_modular_structure()
    if success:
        print("\n[PASS] Verification completed successfully!")
    else:
        print("\n[FAIL] Verification failed. Please check the errors above.")