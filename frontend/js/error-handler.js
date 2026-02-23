// error-handler.js
// Comprehensive Error Handling for Aetherstore Engine with IWSDK

class AetherstoreErrorHandler {
    constructor() {
        this.errorLog = [];
        this.maxLogSize = 100;
        this.isLoggingEnabled = true;
        
        // Set up global error handlers
        this.setupGlobalErrorHandlers();
    }
    
    setupGlobalErrorHandlers() {
        // Handle uncaught exceptions
        window.addEventListener('error', (event) => {
            this.logError({
                type: 'uncaught-exception',
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack || 'No stack trace',
                timestamp: new Date().toISOString()
            });
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError({
                type: 'unhandled-promise-rejection',
                message: event.reason?.message || event.reason || 'Unknown reason',
                stack: event.reason?.stack || 'No stack trace',
                timestamp: new Date().toISOString()
            });
        });
        
        // Handle React-specific errors if React is available
        if (window.React) {
            // This would be implemented if using React error boundaries
        }
    }
    
    logError(error) {
        if (!this.isLoggingEnabled) return;
        
        console.error('Aetherstore Error:', error);
        
        // Add error to log
        this.errorLog.push(error);
        
        // Maintain log size
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.shift();
        }
        
        // Send error to analytics if available
        if (window.iwSdkCommerceAnalytics) {
            window.iwSdkCommerceAnalytics.trackEvent('error', {
                error_type: error.type,
                error_message: error.message,
                error_details: error
            });
        }
    }
    
    // Validate API responses
    validateApiResponse(response, expectedProperties = []) {
        if (!response) {
            throw new Error('API response is null or undefined');
        }
        
        for (const prop of expectedProperties) {
            if (!(prop in response)) {
                throw new Error(`API response missing expected property: ${prop}`);
            }
        }
        
        return true;
    }
    
    // Safe API request wrapper
    async safeApiRequest(url, options = {}, expectedResponseProps = []) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Validate response structure if expected properties are provided
            if (expectedResponseProps.length > 0) {
                this.validateApiResponse(data, expectedResponseProps);
            }
            
            return data;
        } catch (error) {
            this.logError({
                type: 'api-request-error',
                message: error.message,
                url: url,
                options: options,
                timestamp: new Date().toISOString(),
                stack: error.stack
            });
            
            throw error; // Re-throw so calling code can handle it
        }
    }
    
    // Safe 3D asset loading
    async safeLoad3DAsset(loader, assetPath, onProgress = null) {
        try {
            return await new Promise((resolve, reject) => {
                loader.load(
                    assetPath,
                    (result) => {
                        console.log(`Asset loaded successfully: ${assetPath}`);
                        resolve(result);
                    },
                    (progress) => {
                        if (onProgress) onProgress(progress);
                    },
                    (error) => {
                        this.logError({
                            type: 'asset-load-error',
                            message: `Failed to load asset: ${assetPath}`,
                            error: error.message,
                            assetPath: assetPath,
                            timestamp: new Date().toISOString()
                        });
                        reject(error);
                    }
                );
            });
        } catch (error) {
            this.logError({
                type: '3d-asset-load-error',
                message: error.message,
                assetPath: assetPath,
                timestamp: new Date().toISOString(),
                stack: error.stack
            });
            throw error;
        }
    }
    
    // Safe Three.js operation
    safeThreeJSCall(operation, operationName = 'Three.js operation') {
        try {
            return operation();
        } catch (error) {
            this.logError({
                type: 'threejs-error',
                message: `${operationName} failed: ${error.message}`,
                operation: operationName,
                timestamp: new Date().toISOString(),
                stack: error.stack
            });
            throw error;
        }
    }
    
    // Safe IWSDK operation
    safeIwSdkCall(operation, operationName = 'IWSDK operation') {
        try {
            return operation();
        } catch (error) {
            this.logError({
                type: 'iw-sdk-error',
                message: `${operationName} failed: ${error.message}`,
                operation: operationName,
                timestamp: new Date().toISOString(),
                stack: error.stack
            });
            throw error;
        }
    }
    
    // Validation utilities
    validateUserInput(input, rules) {
        const errors = [];
        
        for (const [field, rule] of Object.entries(rules)) {
            const value = input[field];
            
            if (rule.required && (value === undefined || value === null || value === '')) {
                errors.push(`${field} is required`);
            }
            
            if (value !== undefined && value !== null) {
                if (rule.type && typeof value !== rule.type) {
                    errors.push(`${field} must be of type ${rule.type}`);
                }
                
                if (rule.minLength && value.length < rule.minLength) {
                    errors.push(`${field} must be at least ${rule.minLength} characters`);
                }
                
                if (rule.maxLength && value.length > rule.maxLength) {
                    errors.push(`${field} must be no more than ${rule.maxLength} characters`);
                }
                
                if (rule.pattern && !rule.pattern.test(value)) {
                    errors.push(`${field} does not match required pattern`);
                }
            }
        }
        
        if (errors.length > 0) {
            throw new Error(`Validation failed: ${errors.join(', ')}`);
        }
        
        return true;
    }
    
    // Get error log
    getErrorLog() {
        return [...this.errorLog]; // Return a copy
    }
    
    // Clear error log
    clearErrorLog() {
        this.errorLog = [];
    }
    
    // Report error to backend
    async reportErrorToBackend(error) {
        try {
            await this.safeApiRequest('/api/errors', {
                method: 'POST',
                body: JSON.stringify({
                    error: error,
                    userAgent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });
        } catch (reportError) {
            console.warn('Failed to report error to backend:', reportError);
        }
    }
    
    // Enable/disable logging
    setLogging(enabled) {
        this.isLoggingEnabled = enabled;
    }
}

// Create global error handler instance
window.aetherstoreErrorHandler = new AetherstoreErrorHandler();

// Enhance the IWSDK Core with error handling
if (window.IWSDK) {
    // Add error handling to IWSDK Core
    const originalInitialize = window.IWSDK.Core.prototype.initialize;
    window.IWSDK.Core.prototype.initialize = async function(config = {}) {
        return window.aetherstoreErrorHandler.safeIwSdkCall(async () => {
            return await originalInitialize.call(this, config);
        }, 'IWSDK Core initialize');
    };
    
    // Add error handling to IWSDK XR Input Manager
    const originalInputInitialize = window.IWSDK.XRInputManager.prototype.initialize;
    window.IWSDK.XRInputManager.prototype.initialize = async function() {
        return window.aetherstoreErrorHandler.safeIwSdkCall(async () => {
            return await originalInputInitialize.call(this);
        }, 'IWSDK XR Input Manager initialize');
    };
    
    // Add error handling to Locomotion System
    const originalLocomotionInitialize = window.IWSDK.LocomotionSystem.prototype.initialize;
    window.IWSDK.LocomotionSystem.prototype.initialize = function(scene, camera) {
        return window.aetherstoreErrorHandler.safeIwSdkCall(() => {
            return originalLocomotionInitialize.call(this, scene, camera);
        }, 'IWSDK Locomotion System initialize');
    };
    
    // Add error handling to Grab System
    const originalGrabInitialize = window.IWSDK.GrabSystem.prototype.initialize;
    window.IWSDK.GrabSystem.prototype.initialize = function(camera, scene) {
        return window.aetherstoreErrorHandler.safeIwSdkCall(() => {
            return originalGrabInitialize.call(this, camera, scene);
        }, 'IWSDK Grab System initialize');
    };
    
    // Add error handling to Spatial Audio System
    const originalAudioInitialize = window.IWSDK.SpatialAudioSystem.prototype.initialize;
    window.IWSDK.SpatialAudioSystem.prototype.initialize = function(camera) {
        return window.aetherstoreErrorHandler.safeIwSdkCall(() => {
            return originalAudioInitialize.call(this, camera);
        }, 'IWSDK Spatial Audio System initialize');
    };
}

console.log('Aetherstore Error Handler Initialized');