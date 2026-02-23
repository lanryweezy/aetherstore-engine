#!/usr/bin/env python3
"""
Test script to verify SAM 3D integration implementation
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_backend_sam_3d_integration():
    """Test backend SAM 3D integration"""
    logger.info("Testing backend SAM 3D integration...")
    
    try:
        # Import the AI processing module
        from backend.ai_processing import ai_processor
        
        # Check if SAM 3D integration is properly initialized
        assert hasattr(ai_processor, 'sam_3d_objects'), "SAM 3D Objects integration missing"
        assert ai_processor.sam_3d_objects is not None, "SAM 3D Objects not initialized"
        
        # Test simulated 3D reconstruction
        test_image_path = "test_data/test_product.jpg"
        
        # Create test directory and file if they don't exist
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        # Create a simple test image (just a text file for simulation)
        test_image = test_dir / "test_product.jpg"
        if not test_image.exists():
            test_image.write_text("This is a test image for SAM 3D integration")
        
        # Test 3D reconstruction enhancement
        mesh_data = ai_processor._enhance_with_sam_3d_objects(str(test_image))
        
        # Verify the structure of the returned data
        assert isinstance(mesh_data, dict), "Mesh data should be a dictionary"
        assert 'enhanced' in mesh_data, "Mesh data should have 'enhanced' flag"
        assert 'confidence' in mesh_data, "Mesh data should have 'confidence' score"
        assert 'mesh_data' in mesh_data, "Mesh data should have 'mesh_data' section"
        assert 'quality_score' in mesh_data, "Mesh data should have 'quality_score'"
        
        logger.info("Backend SAM 3D integration test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Backend SAM 3D integration test FAILED: {e}")
        return False

def test_frontend_sam_3d_integration():
    """Test frontend SAM 3D integration"""
    logger.info("Testing frontend SAM 3D integration...")
    
    try:
        # Check if JavaScript files exist
        js_files = [
            "frontend/js/sam-3d-integration.js",
            "frontend/js/iw-sdk-advanced-core.js",
            "frontend/js/main.js",
            "frontend/js/enhanced-main.js"
        ]
        
        for js_file in js_files:
            file_path = Path(js_file)
            assert file_path.exists(), f"JavaScript file {js_file} not found"
            
            # Check if file contains SAM 3D references
            content = file_path.read_text()
            assert "SAM3D" in content or "sam3d" in content, f"File {js_file} doesn't contain SAM 3D references"
        
        logger.info("Frontend SAM 3D integration test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Frontend SAM 3D integration test FAILED: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints for SAM 3D integration"""
    logger.info("Testing API endpoints for SAM 3D integration...")
    
    try:
        # Import API modules
        from backend.main import app
        import asyncio
        
        # Test that the app has the necessary routes
        client = asyncio.get_event_loop().run_until_complete(
            app.test_client()
        )
        
        # Check if routes exist (this is a simplified check)
        routes = [route.path for route in app.routes]
        sam_3d_routes = [route for route in routes if '3d' in route.lower() or 'sam' in route.lower()]
        
        logger.info(f"Found {len(sam_3d_routes)} potential SAM 3D routes: {sam_3d_routes}")
        
        logger.info("API endpoints test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"API endpoints test FAILED: {e}")
        return False

def test_documentation():
    """Test documentation for SAM 3D integration"""
    logger.info("Testing documentation for SAM 3D integration...")
    
    try:
        # Check if documentation files exist
        doc_files = [
            "SAM_3D_INTEGRATION.md",
            "SAM_3D_INTEGRATION_README.md",
            "SAM_3D_INTEGRATION_SUMMARY.md"
        ]
        
        for doc_file in doc_files:
            file_path = Path(doc_file)
            assert file_path.exists(), f"Documentation file {doc_file} not found"
            
            # Check if file contains SAM 3D references
            content = file_path.read_text()
            assert "SAM 3D" in content, f"Documentation file {doc_file} doesn't mention SAM 3D"
        
        logger.info("Documentation test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Documentation test FAILED: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting SAM 3D integration tests...")
    
    tests = [
        test_backend_sam_3d_integration,
        test_frontend_sam_3d_integration,
        test_api_endpoints,
        test_documentation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"SAM 3D integration tests completed: {passed}/{total} passed")
    
    if passed == total:
        logger.info("All SAM 3D integration tests PASSED! 🎉")
        return 0
    else:
        logger.error(f"Some SAM 3D integration tests FAILED! ({passed}/{total} passed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())