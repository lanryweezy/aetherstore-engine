# test_api_imports.py
# Test script to verify API module imports work correctly

def test_api_module_imports():
    """Test that all API modules can be imported without errors"""
    print("Testing API module imports...")
    
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
        
        # Test importing main API router
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

if __name__ == "__main__":
    success = test_api_module_imports()
    if success:
        print("\n[PASS] API module import test completed successfully!")
    else:
        print("\n[FAIL] API module import test failed. Please check the errors above.")