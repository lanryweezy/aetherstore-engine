# verify_integration.py
# Final verification script for SAM 3D integration

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return appropriate status emoji"""
    if Path(filepath).exists():
        return "✅", filepath
    else:
        return "❌", filepath

def verify_backend_integration():
    """Verify backend files have SAM 3D integration"""
    print("🔧 Verifying Backend Integration...")
    
    # Check ai_models_real.py
    ai_models_path = Path("backend/ai_models_real.py")
    if ai_models_path.exists():
        content = ai_models_path.read_text().lower()
        if "sam_3d_body" in content:
            print("  ✅ ai_models_real.py contains SAM 3D Body integration")
        else:
            print("  ❌ ai_models_real.py missing SAM 3D Body integration")
    else:
        print("  ❌ ai_models_real.py not found")
    
    # Check ai_processing.py
    ai_processing_path = Path("backend/ai_processing.py")
    if ai_processing_path.exists():
        content = ai_processing_path.read_text().lower()
        if "sam_3d_objects" in content:
            print("  ✅ ai_processing.py contains SAM 3D Objects integration")
        else:
            print("  ❌ ai_processing.py missing SAM 3D Objects integration")
    else:
        print("  ❌ ai_processing.py not found")

def verify_frontend_integration():
    """Verify frontend files have SAM 3D integration"""
    print("\n🌐 Verifying Frontend Integration...")
    
    # Check main application files
    main_files = [
        "frontend/js/main.js",
        "frontend/js/enhanced-main.js",
        "frontend/js/iw-sdk-advanced-core.js"
    ]
    
    for file_path in main_files:
        full_path = Path(file_path)
        if full_path.exists():
            content = full_path.read_text().lower()
            if "sam3d" in content or "sam_3d" in content:
                print(f"  ✅ {file_path} contains SAM 3D integration")
            else:
                print(f"  ⚠️  {file_path} may be missing SAM 3D integration")
        else:
            print(f"  ❌ {file_path} not found")
    
    # Check new SAM 3D specific files
    sam3d_files = [
        "frontend/js/sam-3d-integration.js",
        "frontend/js/sam-3d-demo.js"
    ]
    
    for file_path in sam3d_files:
        status, path = check_file_exists(file_path)
        print(f"  {status} {path}")

def verify_demo_and_documentation():
    """Verify demo and documentation files"""
    print("\n📄 Verifying Demo and Documentation...")
    
    # Check demo files
    demo_files = [
        "frontend/sam-3d-demo.html"
    ]
    
    for file_path in demo_files:
        status, path = check_file_exists(file_path)
        print(f"  {status} {path}")
    
    # Check documentation
    doc_files = [
        "SAM_3D_INTEGRATION.md",
        "SAM_3D_INTEGRATION_SUMMARY.md"
    ]
    
    for file_path in doc_files:
        status, path = check_file_exists(file_path)
        print(f"  {status} {path}")

def verify_configuration():
    """Verify configuration files have SAM 3D entries"""
    print("\n⚙️  Verifying Configuration...")
    
    # Check package.json
    package_path = Path("frontend/package.json")
    if package_path.exists():
        try:
            with open(package_path, 'r') as f:
                package_data = json.load(f)
            
            # Check keywords
            keywords = package_data.get('keywords', [])
            if 'sam-3d' in keywords:
                print("  ✅ package.json contains SAM 3D keyword")
            else:
                print("  ⚠️  package.json missing SAM 3D keyword")
        except Exception as e:
            print(f"  ❌ Error reading package.json: {e}")
    else:
        print("  ❌ package.json not found")
    
    # Check webpack configurations
    webpack_files = [
        "frontend/webpack.config.js",
        "frontend/webpack.prod.config.js"
    ]
    
    for file_path in webpack_files:
        full_path = Path(file_path)
        if full_path.exists():
            content = full_path.read_text()
            if "sam-3d" in content:
                print(f"  ✅ {file_path} contains SAM 3D entry")
            else:
                print(f"  ⚠️  {file_path} may be missing SAM 3D entry")
        else:
            print(f"  ❌ {file_path} not found")

def verify_navigation():
    """Verify navigation includes SAM 3D demo link"""
    print("\n🧭 Verifying Navigation...")
    
    index_path = Path("frontend/index.html")
    if index_path.exists():
        content = index_path.read_text()
        if "sam-3d-demo.html" in content:
            print("  ✅ index.html contains link to SAM 3D demo")
        else:
            print("  ⚠️  index.html missing link to SAM 3D demo")
    else:
        print("  ❌ index.html not found")

def verify_tests():
    """Verify test files exist"""
    print("\n🧪 Verifying Tests...")
    
    test_files = [
        "simple_test.py",
        "test_sam_3d.js",
        "run_sam_3d_test.js",
        "frontend/tests/sam-3d-integration.test.js"
    ]
    
    for file_path in test_files:
        status, path = check_file_exists(file_path)
        print(f"  {status} {path}")

def main():
    """Main verification function"""
    print("🔍 Aetherstore Engine SAM 3D Integration Verification")
    print("=" * 60)
    
    # Verify all components
    verify_backend_integration()
    verify_frontend_integration()
    verify_demo_and_documentation()
    verify_configuration()
    verify_navigation()
    verify_tests()
    
    print("\n" + "=" * 60)
    print("✅ Verification complete!")
    print("\nNext steps:")
    print("1. Run the simple test suite: python simple_test.py")
    print("2. Test the frontend demo by opening frontend/sam-3d-demo.html in a browser")
    print("3. When actual SAM 3D models are available, replace the placeholders")
    print("4. Run performance tests to optimize the integration")

if __name__ == "__main__":
    main()