// run_sam_3d_test.js
// Node.js script to run the SAM 3D integration test

// This script simulates a browser environment for testing
// In a real browser environment, you would just include the script directly

// Mock browser environment
global.window = {};
global.document = {
    createElement: () => ({
        getContext: () => ({})
    })
};
global.WebAssembly = {};
global.BigInt = function() {};

// Include the SAM 3D integration module
const fs = require('fs');
const path = require('path');

// Read the SAM 3D integration file
const sam3dCode = fs.readFileSync(path.join(__dirname, 'frontend', 'js', 'sam-3d-integration.js'), 'utf8');

// Evaluate the code in the global context
eval(sam3dCode);

// Include the test file
const { testSAM3DIntegration } = require('./test_sam_3d.js');

// Run the test
async function runTest() {
    console.log('Running SAM 3D Integration Test...');
    console.log('=====================================');
    
    try {
        const success = await testSAM3DIntegration();
        
        console.log('=====================================');
        if (success) {
            console.log('✅ All tests passed! SAM 3D Integration is working correctly.');
        } else {
            console.log('❌ Some tests failed. Please check the output above for details.');
        }
    } catch (error) {
        console.error('❌ Test execution failed:', error);
    }
}

// Run the test
runTest();