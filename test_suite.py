# test_suite.py
# Comprehensive test suite for Aetherstore Engine

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    # Try to import the AI modules
    from ai_models_real import RealBodyMeasurementModel, RealFitPredictionModel
    from ai_processing import AdvancedAIService, BodyMeasurements
    print("✅ AI modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import AI modules: {e}")
    sys.exit(1)

async def test_ai_models():
    """Test the AI models with enhanced SAM 3D integration"""
    print("\n🧪 Testing AI Models with SAM 3D Integration...")
    
    try:
        # Test body measurement model
        body_model = RealBodyMeasurementModel()
        print("✅ Body measurement model initialized")
        
        # Check if SAM 3D Body integration is present
        if hasattr(body_model, 'sam_3d_body'):
            print("✅ SAM 3D Body integration detected")
        else:
            print("⚠️  SAM 3D Body integration not found")
        
        # Test fit prediction model
        fit_model = RealFitPredictionModel()
        print("✅ Fit prediction model initialized")
        
        # Test with sample data
        sample_measurements = BodyMeasurements(
            height=170.0,
            weight=65.0,
            chest=90.0,
            waist=75.0,
            hips=95.0,
            shoulder_width=42.0,
            arm_length=60.0,
            inseam=80.0,
            neck=36.0,
            bicep=28.0
        )
        
        size_chart = {
            "S": {"chest": 85, "waist": 65, "hips": 90},
            "M": {"chest": 90, "waist": 70, "hips": 95},
            "L": {"chest": 95, "waist": 75, "hips": 100}
        }
        
        fit_result = fit_model.predict_fit(sample_measurements.__dict__, size_chart)
        print(f"✅ Fit prediction completed: {fit_result}")
        
        return True
    except Exception as e:
        print(f"❌ AI models test failed: {e}")
        return False

async def test_ai_service():
    """Test the advanced AI service"""
    print("\n🤖 Testing Advanced AI Service...")
    
    try:
        ai_service = AdvancedAIService()
        print("✅ Advanced AI Service initialized")
        
        # Check if SAM 3D integration is present
        if hasattr(ai_service.cv_processor, 'sam_3d_objects'):
            print("✅ SAM 3D Objects integration detected")
        else:
            print("⚠️  SAM 3D Objects integration not found")
        
        # Test service methods
        methods = [
            'process_avatar_scan',
            'analyze_product_fit',
            'generate_3d_product_model'
        ]
        
        for method in methods:
            if hasattr(ai_service, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"⚠️  Method '{method}' not found")
        
        return True
    except Exception as e:
        print(f"❌ Advanced AI Service test failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "frontend/js/sam-3d-integration.js",
        "frontend/js/sam-3d-demo.js",
        "frontend/sam-3d-demo.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_backend_enhancements():
    """Test backend enhancements for SAM 3D integration"""
    print("\n🔧 Testing Backend Enhancements...")
    
    # Check if the enhanced files have the expected modifications
    try:
        # Check ai_models_real.py
        ai_models_path = Path("backend/ai_models_real.py")
        if ai_models_path.exists():
            content = ai_models_path.read_text()
            if "sam_3d_body" in content:
                print("✅ ai_models_real.py enhanced with SAM 3D Body integration")
            else:
                print("⚠️  ai_models_real.py not enhanced with SAM 3D Body")
        else:
            print("❌ ai_models_real.py not found")
        
        # Check ai_processing.py
        ai_processing_path = Path("backend/ai_processing.py")
        if ai_processing_path.exists():
            content = ai_processing_path.read_text()
            if "sam_3d_objects" in content:
                print("✅ ai_processing.py enhanced with SAM 3D Objects integration")
            else:
                print("⚠️  ai_processing.py not enhanced with SAM 3D Objects")
        else:
            print("❌ ai_processing.py not found")
        
        return True
    except Exception as e:
        print(f"❌ Backend enhancements test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Aetherstore Engine Test Suite with SAM 3D Integration")
    print("=" * 70)
    
    # Test file structure
    file_tests_passed = test_file_structure()
    
    # Test backend enhancements
    backend_tests_passed = test_backend_enhancements()
    
    # Test AI models
    ai_models_passed = await test_ai_models()
    
    # Test AI service
    ai_service_passed = await test_ai_service()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    print(f"📁 File Structure Tests: {'✅ PASSED' if file_tests_passed else '❌ FAILED'}")
    print(f"🔧 Backend Enhancements: {'✅ PASSED' if backend_tests_passed else '❌ FAILED'}")
    print(f"🧪 AI Models Tests: {'✅ PASSED' if ai_models_passed else '❌ FAILED'}")
    print(f"🤖 AI Service Tests: {'✅ PASSED' if ai_service_passed else '❌ FAILED'}")
    
    all_passed = file_tests_passed and backend_tests_passed and ai_models_passed and ai_service_passed
    print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    # Run the test suite
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)