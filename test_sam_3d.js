// test_sam_3d.js
// Simple test script to verify SAM 3D integration

async function testSAM3DIntegration() {
    console.log('Testing SAM 3D Integration...');
    
    try {
        // Check if SAM3DIntegration class is available
        if (typeof SAM3DIntegration === 'undefined') {
            console.error('SAM3DIntegration class not found');
            return false;
        }
        
        // Create an instance
        const sam3d = new SAM3DIntegration();
        console.log('SAM3DIntegration instance created successfully');
        
        // Test initialization
        const initialized = await sam3d.initialize();
        if (!initialized) {
            console.error('SAM3DIntegration failed to initialize');
            return false;
        }
        console.log('SAM3DIntegration initialized successfully');
        
        // Test status method
        const status = sam3d.getStatus();
        console.log('SAM3DIntegration status:', status);
        
        // Test product enhancement (mock data)
        const mockProduct = {
            id: 'test-product',
            name: 'Test Dress',
            images: ['front.jpg', 'side.jpg']
        };
        
        const enhancedProduct = await sam3d.enhanceProduct3DModel(mockProduct);
        console.log('Product enhancement result:', enhancedProduct);
        
        // Test body measurement enhancement (mock data)
        const mockBodyData = {
            userId: 'test-user',
            images: ['front.jpg', 'side.jpg'],
            measurements: {
                height: 170,
                chest: 90,
                waist: 75,
                hips: 95
            }
        };
        
        const enhancedBodyData = await sam3d.enhanceBodyMeasurements(mockBodyData);
        console.log('Body measurement enhancement result:', enhancedBodyData);
        
        // Test scene creation (mock data)
        const mockItems = [
            { id: 'item-1', type: 'product', name: 'Test Dress' },
            { id: 'item-2', type: 'product', name: 'Test Shoes' }
        ];
        
        const scene = await sam3d.create3DSceneVisualization(mockItems);
        console.log('Scene creation result:', scene);
        
        // Test feature toggling
        sam3d.toggleFeature('reconstruction', false);
        sam3d.toggleFeature('body', false);
        console.log('Features toggled off');
        
        sam3d.toggleFeature('reconstruction', true);
        sam3d.toggleFeature('body', true);
        console.log('Features toggled back on');
        
        console.log('All SAM 3D Integration tests passed!');
        return true;
    } catch (error) {
        console.error('Error testing SAM 3D Integration:', error);
        return false;
    }
}

// Run the test if this script is executed directly
if (typeof module !== 'undefined' && !module.parent) {
    testSAM3DIntegration()
        .then(success => {
            if (success) {
                console.log('SAM 3D Integration test completed successfully');
            } else {
                console.log('SAM 3D Integration test failed');
            }
        })
        .catch(error => {
            console.error('Test execution error:', error);
        });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { testSAM3DIntegration };
}