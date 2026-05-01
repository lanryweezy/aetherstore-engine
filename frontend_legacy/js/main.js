// main.js
// Main application entry point with enhanced 3D capabilities
// Enhanced with Meta's SAM 3D integration

console.log('Loading Main Application with SAM 3D Integration...');

// Import required modules
import { IWSDKAdvanced } from './iw-sdk-advanced-core.js';
import { SAM3DIntegration } from './sam-3d-integration.js';

// Global application state
const appState = {
    sdk: null,
    sam3d: null,
    isInitialized: false,
    currentUser: null,
    currentAvatar: null,
    currentProduct: null
};

/**
 * Initialize the main application
 */
async function initializeApp() {
    try {
        console.log('Initializing main application...');
        
        // Initialize IW SDK Advanced
        appState.sdk = new IWSDKAdvanced();
        await appState.sdk.initialize();
        
        // Initialize SAM 3D Integration
        appState.sam3d = new SAM3DIntegration();
        await appState.sam3d.initialize();
        
        // Set up event listeners
        setupEventListeners();
        
        // Mark as initialized
        appState.isInitialized = true;
        
        console.log('Main application initialized successfully');
        
        // Dispatch initialization event
        document.dispatchEvent(new CustomEvent('appInitialized', {
            detail: { status: 'success' }
        }));
        
        return true;
    } catch (error) {
        console.error('Failed to initialize main application:', error);
        
        // Dispatch initialization error event
        document.dispatchEvent(new CustomEvent('appInitializationError', {
            detail: { error: error.message }
        }));
        
        return false;
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Listen for 3D scan requests
    document.addEventListener('request3DScan', handle3DScanRequest);
    
    // Listen for body measurement requests
    document.addEventListener('requestBodyMeasurement', handleBodyMeasurementRequest);
    
    // Listen for avatar creation requests
    document.addEventListener('requestAvatarCreation', handleAvatarCreationRequest);
    
    // Listen for virtual try-on requests
    document.addEventListener('requestVirtualTryOn', handleVirtualTryOnRequest);
    
    console.log('Event listeners set up successfully');
}

/**
 * Handle 3D scan request
 */
async function handle3DScanRequest(event) {
    try {
        console.log('Handling 3D scan request...', event.detail);
        
        const { imagePath, options } = event.detail;
        
        // Perform enhanced 3D scan with SAM 3D
        const result = await appState.sdk.enhanced3DScan(imagePath, options);
        
        // Dispatch result
        document.dispatchEvent(new CustomEvent('3DScanComplete', {
            detail: { result }
        }));
    } catch (error) {
        console.error('3D scan failed:', error);
        
        // Dispatch error
        document.dispatchEvent(new CustomEvent('3DScanError', {
            detail: { error: error.message }
        }));
    }
}

/**
 * Handle body measurement request
 */
async function handleBodyMeasurementRequest(event) {
    try {
        console.log('Handling body measurement request...', event.detail);
        
        const { imagePath, referenceHeight } = event.detail;
        
        // Perform enhanced body measurement with SAM 3D
        const result = await appState.sdk.enhancedBodyMeasurement(imagePath, referenceHeight);
        
        // Dispatch result
        document.dispatchEvent(new CustomEvent('bodyMeasurementComplete', {
            detail: { result }
        }));
    } catch (error) {
        console.error('Body measurement failed:', error);
        
        // Dispatch error
        document.dispatchEvent(new CustomEvent('bodyMeasurementError', {
            detail: { error: error.message }
        }));
    }
}

/**
 * Handle avatar creation request
 */
async function handleAvatarCreationRequest(event) {
    try {
        console.log('Handling avatar creation request...', event.detail);
        
        const { bodyMeasurements, options } = event.detail;
        
        // Create enhanced avatar with SAM 3D
        const avatar = await appState.sdk.createEnhancedAvatar(bodyMeasurements, options);
        
        // Store current avatar
        appState.currentAvatar = avatar;
        
        // Dispatch result
        document.dispatchEvent(new CustomEvent('avatarCreationComplete', {
            detail: { avatar }
        }));
    } catch (error) {
        console.error('Avatar creation failed:', error);
        
        // Dispatch error
        document.dispatchEvent(new CustomEvent('avatarCreationError', {
            detail: { error: error.message }
        }));
    }
}

/**
 * Handle virtual try-on request
 */
async function handleVirtualTryOnRequest(event) {
    try {
        console.log('Handling virtual try-on request...', event.detail);
        
        const { avatar, product3D, options } = event.detail;
        
        // Perform enhanced virtual try-on with SAM 3D
        const result = await appState.sdk.enhancedVirtualTryOn(
            avatar || appState.currentAvatar,
            product3D,
            options
        );
        
        // Dispatch result
        document.dispatchEvent(new CustomEvent('virtualTryOnComplete', {
            detail: { result }
        }));
    } catch (error) {
        console.error('Virtual try-on failed:', error);
        
        // Dispatch error
        document.dispatchEvent(new CustomEvent('virtualTryOnError', {
            detail: { error: error.message }
        }));
    }
}

/**
 * Perform enhanced 3D reconstruction
 * @param {string} imagePath - Path to the input image
 * @param {Object} options - Reconstruction options
 */
async function performEnhanced3DReconstruction(imagePath, options = {}) {
    try {
        console.log('Performing enhanced 3D reconstruction with SAM 3D...');
        
        if (!appState.isInitialized) {
            throw new Error('Application not initialized');
        }
        
        // Use SAM 3D Integration for enhanced reconstruction
        const result = await appState.sam3d.reconstruct3D(imagePath, {
            quality: 'ultra-high',
            ...options
        });
        
        console.log('Enhanced 3D reconstruction completed successfully');
        return result;
    } catch (error) {
        console.error('Enhanced 3D reconstruction failed:', error);
        throw error;
    }
}

/**
 * Perform enhanced body measurement
 * @param {string} imagePath - Path to the body scan image
 * @param {number} referenceHeight - Known height in cm (optional)
 */
async function performEnhancedBodyMeasurement(imagePath, referenceHeight = null) {
    try {
        console.log('Performing enhanced body measurement with SAM 3D...');
        
        if (!appState.isInitialized) {
            throw new Error('Application not initialized');
        }
        
        // Use SAM 3D Integration for enhanced measurement
        const result = await appState.sam3d.measureBody(imagePath, referenceHeight);
        
        console.log('Enhanced body measurement completed successfully');
        return result;
    } catch (error) {
        console.error('Enhanced body measurement failed:', error);
        throw error;
    }
}

/**
 * Integrate 3D model with Three.js scene
 * @param {THREE.Scene} scene - Three.js scene
 * @param {Object} meshData - 3D mesh data
 */
function integrateWithThreeJSScene(scene, meshData) {
    if (!appState.sam3d) {
        console.warn('SAM 3D Integration not available');
        return null;
    }
    
    return appState.sam3d.integrateWithThreeJSScene(scene, meshData);
}

/**
 * Integrate 3D model with A-Frame entity
 * @param {AFRAME.Entity} entity - A-Frame entity
 * @param {Object} meshData - 3D mesh data
 */
function integrateWithAFrameEntity(entity, meshData) {
    if (!appState.sam3d) {
        console.warn('SAM 3D Integration not available');
        return false;
    }
    
    return appState.sam3d.integrateWithAFrameEntity(entity, meshData);
}

/**
 * Get enhanced analytics
 * @param {string} userId - User ID
 * @param {Object} options - Analytics options
 */
async function getEnhancedAnalytics(userId, options = {}) {
    try {
        console.log('Getting enhanced analytics with SAM 3D insights...');
        
        if (!appState.isInitialized) {
            throw new Error('Application not initialized');
        }
        
        // Get enhanced analytics from SDK
        const analytics = await appState.sdk.getEnhancedAnalytics(userId, options);
        
        console.log('Enhanced analytics retrieved successfully');
        return analytics;
    } catch (error) {
        console.error('Failed to get enhanced analytics:', error);
        throw error;
    }
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeApp,
        performEnhanced3DReconstruction,
        performEnhancedBodyMeasurement,
        integrateWithThreeJSScene,
        integrateWithAFrameEntity,
        getEnhancedAnalytics
    };
} else if (typeof window !== 'undefined') {
    window.AetherstoreApp = {
        initializeApp,
        performEnhanced3DReconstruction,
        performEnhancedBodyMeasurement,
        integrateWithThreeJSScene,
        integrateWithAFrameEntity,
        getEnhancedAnalytics
    };
}

// Initialize app when DOM is loaded
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', async () => {
        console.log('Initializing application on DOM load');
        await initializeApp();
    });
}

console.log('Main Application loaded successfully');