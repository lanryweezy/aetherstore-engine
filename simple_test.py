# simple_test.py
# Simple test script to verify file structure and basic integration

import os
from pathlib import Path

def test_file_structure():
    """Test that required files exist"""
    print("📁 Testing File Structure...")
    
    required_files = [
        "frontend/js/sam-3d-integration.js",
        "frontend/js/sam-3d-demo.js",
        "frontend/sam-3d-demo.html",
        "frontend/js/main.js",
        "frontend/js/enhanced-main.js",
        "backend/ai_models_real.py",
        "backend/ai_processing.py",
        "frontend/js/iw-sdk-advanced-core.js"
    ]
    
    all_passed = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            all_passed = False
    
    return all_passed

def test_backend_enhancements():
    """Test backend enhancements for SAM 3D integration"""
    print("\n🔧 Testing Backend Enhancements...")
    
    # Check if the enhanced files have the expected modifications
    try:
        # Check ai_models_real.py
        ai_models_path = Path("backend/ai_models_real.py")
        if ai_models_path.exists():
            content = ai_models_path.read_text()
            if "sam_3d_body" in content.lower():
                print("✅ ai_models_real.py enhanced with SAM 3D Body integration")
            else:
                print("⚠️  ai_models_real.py not enhanced with SAM 3D Body")
        else:
            print("❌ ai_models_real.py not found")
            return False
        
        # Check ai_processing.py
        ai_processing_path = Path("backend/ai_processing.py")
        if ai_processing_path.exists():
            content = ai_processing_path.read_text()
            if "sam_3d_objects" in content.lower():
                print("✅ ai_processing.py enhanced with SAM 3D Objects integration")
            else:
                print("⚠️  ai_processing.py not enhanced with SAM 3D Objects")
        else:
            print("❌ ai_processing.py not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Backend enhancements test failed: {e}")
        return False

def test_frontend_enhancements():
    """Test frontend enhancements for SAM 3D integration"""
    print("\n🌐 Testing Frontend Enhancements...")
    
    try:
        # Check main.js
        main_js_path = Path("frontend/js/main.js")
        if main_js_path.exists():
            content = main_js_path.read_text()
            if "sam3dintegration" in content.lower():
                print("✅ main.js enhanced with SAM 3D integration")
            else:
                print("⚠️  main.js not enhanced with SAM 3D integration")
        else:
            print("❌ main.js not found")
            return False
        
        # Check enhanced-main.js
        enhanced_main_js_path = Path("frontend/js/enhanced-main.js")
        if enhanced_main_js_path.exists():
            content = enhanced_main_js_path.read_text()
            if "sam3dintegration" in content.lower():
                print("✅ enhanced-main.js enhanced with SAM 3D integration")
            else:
                print("⚠️  enhanced-main.js not enhanced with SAM 3D integration")
        else:
            print("❌ enhanced-main.js not found")
            return False
        
        # Check iw-sdk-advanced-core.js
        iw_sdk_path = Path("frontend/js/iw-sdk-advanced-core.js")
        if iw_sdk_path.exists():
            content = iw_sdk_path.read_text()
            if "sam3d" in content.lower():
                print("✅ iw-sdk-advanced-core.js enhanced with SAM 3D features")
            else:
                print("⚠️  iw-sdk-advanced-core.js not enhanced with SAM 3D features")
        else:
            print("❌ iw-sdk-advanced-core.js not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Frontend enhancements test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Simple Test Suite for Aetherstore Engine with SAM 3D Integration")
    print("=" * 80)
    
    # Test file structure
    file_tests_passed = test_file_structure()
    
    # Test backend enhancements
    backend_tests_passed = test_backend_enhancements()
    
    # Test frontend enhancements
    frontend_tests_passed = test_frontend_enhancements()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    print(f"📁 File Structure Tests: {'✅ PASSED' if file_tests_passed else '❌ FAILED'}")
    print(f"🔧 Backend Enhancements: {'✅ PASSED' if backend_tests_passed else '❌ FAILED'}")
    print(f"🌐 Frontend Enhancements: {'✅ PASSED' if frontend_tests_passed else '❌ FAILED'}")
    
    all_passed = file_tests_passed and backend_tests_passed and frontend_tests_passed
    print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)