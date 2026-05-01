// enhanced-error-handler.js
// Enhanced Error Handler for Aetherstore Engine with IWSDK Integration

class EnhancedAetherstoreErrorHandler {
    constructor() {
        this.errorLog = [];
        this.maxLogSize = 200;
        this.isLoggingEnabled = true;
        this.isAnalyticsEnabled = true;
        
        // Enhanced error categorization
        this.errorCategories = {
            IWSDK: 'iw-sdk-errors',
            AI: 'ai-errors',
            AVATAR: 'avatar-errors',
            NETWORK: 'network-errors',
            SECURITY: 'security-errors',
            RENDERING: 'rendering-errors',
            USER_INPUT: 'user-input-errors',
            SYSTEM: 'system-errors'
        };
        
        // Set up global error handlers with enhanced categorization
        this.setupGlobalErrorHandlers();
        
        console.log('Enhanced Aetherstore Error Handler initialized');
    }
    
    setupGlobalErrorHandlers() {
        // Handle uncaught exceptions with enhanced categorization
        window.addEventListener('error', (event) => {
            const errorInfo = {
                type: 'uncaught-exception',
                category: this.categorizeError(event.error),
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack || 'No stack trace',
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            this.logError(errorInfo);
        });
        
        // Handle unhandled promise rejections with enhanced categorization
        window.addEventListener('unhandledrejection', (event) => {
            const errorInfo = {
                type: 'unhandled-promise-rejection',
                category: this.categorizeError(event.reason),
                message: event.reason?.message || event.reason || 'Unknown reason',
                stack: event.reason?.stack || 'No stack trace',
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            this.logError(errorInfo);
        });
        
        // Handle React-specific errors if React is available
        if (window.React) {
            // This would be implemented if using React error boundaries
        }
    }
    
    categorizeError(error) {
        // Enhanced error categorization based on error content
        if (!error) return this.errorCategories.SYSTEM;
        
        const errorMessage = (error.message || error.toString()).toLowerCase();
        
        // IWSDK errors
        if (errorMessage.includes('iw-sdk') || 
            errorMessage.includes('iwsdk') ||
            errorMessage.includes('immersive web')) {
            return this.errorCategories.IWSDK;
        }
        
        // AI errors
        if (errorMessage.includes('ai') || 
            errorMessage.includes('machine learning') ||
            errorMessage.includes('neural') ||
            errorMessage.includes('prediction')) {
            return this.errorCategories.AI;
        }
        
        // Avatar errors
        if (errorMessage.includes('avatar') || 
            errorMessage.includes('3d model') ||
            errorMessage.includes('mesh') ||
            errorMessage.includes('geometry')) {
            return this.errorCategories.AVATAR;
        }
        
        // Network errors
        if (errorMessage.includes('network') || 
            errorMessage.includes('fetch') ||
            errorMessage.includes('api') ||
            errorMessage.includes('xhr') ||
            errorMessage.includes('timeout')) {
            return this.errorCategories.NETWORK;
        }
        
        // Security errors
        if (errorMessage.includes('security') || 
            errorMessage.includes('authentication') ||
            errorMessage.includes('authorization') ||
            errorMessage.includes('csrf') ||
            errorMessage.includes('xss')) {
            return this.errorCategories.SECURITY;
        }
        
        // Rendering errors
        if (errorMessage.includes('three.js') || 
            errorMessage.includes('webgl') ||
            errorMessage.includes('render') ||
            errorMessage.includes('shader')) {
            return this.errorCategories.RENDERING;
        }
        
        // User input errors
        if (errorMessage.includes('input') || 
            errorMessage.includes('validation') ||
            errorMessage.includes('form')) {
            return this.errorCategories.USER_INPUT;
        }
        
        // Default to system errors
        return this.errorCategories.SYSTEM;
    }
    
    logError(error) {
        if (!this.isLoggingEnabled) return;
        
        console.error('Aetherstore Enhanced Error:', error);
        
        // Add error to log with category
        this.errorLog.push(error);
        
        // Maintain log size
        if (this.errorLog.length > this.maxLogSize) {
            this.errorLog.shift();
        }
        
        // Send error to analytics if available and enabled
        if (this.isAnalyticsEnabled && window.iwSdkCommerceAnalytics) {
            window.iwSdkCommerceAnalytics.trackEvent('error', {
                error_type: error.type,
                error_category: error.category,
                error_message: error.message,
                error_details: {
                    stack: error.stack,
                    filename: error.filename,
                    line: error.line,
                    column: error.column
                },
                user_context: {
                    userAgent: error.userAgent,
                    url: error.url,
                    timestamp: error.timestamp
                }
            });
        }
        
        // Report critical errors to backend
        if (this.shouldReportError(error)) {
            this.reportErrorToBackend(error);
        }
    }
    
    shouldReportError(error) {
        // Determine if an error should be reported to backend
        // Critical errors, frequent errors, and security errors should always be reported
        const criticalCategories = [
            this.errorCategories.SECURITY,
            this.errorCategories.SYSTEM
        ];
        
        const criticalErrorTypes = [
            'uncaught-exception',
            'unhandled-promise-rejection'
        ];
        
        // Report critical errors
        if (criticalCategories.includes(error.category) || 
            criticalErrorTypes.includes(error.type)) {
            return true;
        }
        
        // Report errors that occur frequently
        const recentErrors = this.errorLog.filter(e => 
            e.message === error.message && 
            Date.now() - new Date(e.timestamp).getTime() < 300000 // Last 5 minutes
        );
        
        return recentErrors.length > 3; // Report if same error occurs more than 3 times in 5 minutes
    }
    
    // Enhanced API request wrapper with comprehensive error handling
    async safeApiRequest(url, options = {}, expectedResponseProps = []) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            // Handle HTTP errors
            if (!response.ok) {
                const error = new Error(`API request failed: ${response.status} ${response.statusText}`);
                error.category = this.errorCategories.NETWORK;
                error.statusCode = response.status;
                
                // Special handling for authentication errors
                if (response.status === 401 || response.status === 403) {
                    error.category = this.errorCategories.SECURITY;
                    // Trigger re-authentication if needed
                    this.handleAuthenticationError();
                }
                
                throw error;
            }
            
            const data = await response.json();
            
            // Validate response structure if expected properties are provided
            if (expectedResponseProps.length > 0) {
                this.validateApiResponse(data, expectedResponseProps);
            }
            
            return data;
        } catch (error) {
            // Categorize and log the error
            error.category = error.category || this.errorCategories.NETWORK;
            this.logError({
                type: 'api-request-error',
                category: error.category,
                message: error.message,
                url: url,
                options: options,
                timestamp: new Date().toISOString(),
                stack: error.stack,
                statusCode: error.statusCode
            });
            
            // Rethrow so calling code can handle it
            throw error;
        }
    }
    
    // Enhanced 3D asset loading with comprehensive error handling
    async safeLoad3DAsset(loader, assetPath, onProgress = null) {
        try {
            return await new Promise((resolve, reject) => {
                loader.load(
                    assetPath,
                    (result) => {
                        console.log(`3D Asset loaded successfully: ${assetPath}`);
                        resolve(result);
                    },
                    (progress) => {
                        if (onProgress) onProgress(progress);
                    },
                    (error) => {
                        const assetError = {
                            type: 'asset-load-error',
                            category: this.errorCategories.AVATAR,
                            message: `Failed to load 3D asset: ${assetPath}`,
                            error: error.message,
                            assetPath: assetPath,
                            timestamp: new Date().toISOString()
                        };
                        
                        this.logError(assetError);
                        reject(new Error(assetError.message));
                    }
                );
            });
        } catch (error) {
            const assetError = {
                type: '3d-asset-load-error',
                category: this.errorCategories.AVATAR,
                message: error.message,
                assetPath: assetPath,
                timestamp: new Date().toISOString(),
                stack: error.stack
            };
            
            this.logError(assetError);
            throw new Error(`Failed to load 3D asset: ${assetPath}`);
        }
    }
    
    // Enhanced Three.js operation with error handling
    safeThreeJSCall(operation, operationName = 'Three.js operation') {
        try {
            return operation();
        } catch (error) {
            const threeError = {
                type: 'threejs-error',
                category: this.errorCategories.RENDERING,
                message: `${operationName} failed: ${error.message}`,
                operation: operationName,
                timestamp: new Date().toISOString(),
                stack: error.stack
            };
            
            this.logError(threeError);
            throw new Error(threeError.message);
        }
    }
    
    // Enhanced IWSDK operation with error handling
    safeIwSdkCall(operation, operationName = 'IWSDK operation') {
        try {
            return operation();
        } catch (error) {
            const iwSdkError = {
                type: 'iw-sdk-error',
                category: this.errorCategories.IWSDK,
                message: `${operationName} failed: ${error.message}`,
                operation: operationName,
                timestamp: new Date().toISOString(),
                stack: error.stack
            };
            
            this.logError(iwSdkError);
            throw new Error(iwSdkError.message);
        }
    }
    
    // Enhanced AI operation with error handling
    safeAiCall(operation, operationName = 'AI operation') {
        try {
            return operation();
        } catch (error) {
            const aiError = {
                type: 'ai-error',
                category: this.errorCategories.AI,
                message: `${operationName} failed: ${error.message}`,
                operation: operationName,
                timestamp: new Date().toISOString(),
                stack: error.stack
            };
            
            this.logError(aiError);
            throw new Error(aiError.message);
        }
    }
    
    // Validation utilities with enhanced error handling
    validateApiResponse(response, expectedProperties = []) {
        if (!response) {
            const error = new Error('API response is null or undefined');
            error.category = this.errorCategories.NETWORK;
            throw error;
        }
        
        for (const prop of expectedProperties) {
            if (!(prop in response)) {
                const error = new Error(`API response missing expected property: ${prop}`);
                error.category = this.errorCategories.SYSTEM;
                throw error;
            }
        }
        
        return true;
    }
    
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
                
                // Additional validation rules
                if (rule.customValidator && !rule.customValidator(value)) {
                    errors.push(rule.customErrorMessage || `${field} failed custom validation`);
                }
            }
        }
        
        if (errors.length > 0) {
            const error = new Error(`Validation failed: ${errors.join(', ')}`);
            error.category = this.errorCategories.USER_INPUT;
            throw error;
        }
        
        return true;
    }
    
    // Enhanced error recovery methods
    handleAuthenticationError() {
        // Handle authentication errors by clearing tokens and redirecting to login
        console.warn('Authentication error detected, clearing credentials');
        
        // Clear authentication tokens
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('permissions');
        
        // Redirect to login or refresh token
        if (confirm('Your session has expired. Would you like to log in again?')) {
            window.location.href = '/login';
        }
    }
    
    // Get error log with filtering
    getErrorLog(filter = {}) {
        let filteredLogs = [...this.errorLog];
        
        // Filter by category
        if (filter.category) {
            filteredLogs = filteredLogs.filter(log => log.category === filter.category);
        }
        
        // Filter by type
        if (filter.type) {
            filteredLogs = filteredLogs.filter(log => log.type === filter.type);
        }
        
        // Filter by time range
        if (filter.since) {
            const sinceTime = new Date(filter.since).getTime();
            filteredLogs = filteredLogs.filter(log => 
                new Date(log.timestamp).getTime() >= sinceTime
            );
        }
        
        return filteredLogs;
    }
    
    // Clear error log
    clearErrorLog() {
        this.errorLog = [];
    }
    
    // Enhanced error reporting to backend
    async reportErrorToBackend(error) {
        try {
            // Don't report if already reporting to avoid infinite loops
            if (error.beingReported) return;
            
            error.beingReported = true;
            
            await this.safeApiRequest('/api/errors/report', {
                method: 'POST',
                body: JSON.stringify({
                    error: {
                        type: error.type,
                        category: error.category,
                        message: error.message,
                        details: {
                            stack: error.stack,
                            filename: error.filename,
                            line: error.line,
                            column: error.column,
                            statusCode: error.statusCode
                        },
                        context: {
                            userAgent: error.userAgent || navigator.userAgent,
                            url: error.url || window.location.href,
                            timestamp: error.timestamp
                        }
                    },
                    environment: {
                        appVersion: '1.0.0-enhanced',
                        platform: navigator.platform,
                        language: navigator.language
                    }
                })
            });
            
            console.log('Error reported to backend:', error.message);
        } catch (reportError) {
            console.warn('Failed to report error to backend:', reportError);
        } finally {
            delete error.beingReported;
        }
    }
    
    // Get error statistics
    getErrorStatistics() {
        const stats = {
            totalErrors: this.errorLog.length,
            errorsByCategory: {},
            errorsByType: {},
            mostCommonErrors: []
        };
        
        // Count errors by category
        this.errorLog.forEach(error => {
            const category = error.category || 'unknown';
            stats.errorsByCategory[category] = (stats.errorsByCategory[category] || 0) + 1;
            
            const type = error.type || 'unknown';
            stats.errorsByType[type] = (stats.errorsByType[type] || 0) + 1;
        });
        
        // Find most common errors
        const errorMessages = {};
        this.errorLog.forEach(error => {
            const message = error.message;
            errorMessages[message] = (errorMessages[message] || 0) + 1;
        });
        
        stats.mostCommonErrors = Object.entries(errorMessages)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([message, count]) => ({ message, count }));
        
        return stats;
    }
    
    // Enable/disable logging
    setLogging(enabled) {
        this.isLoggingEnabled = enabled;
    }
    
    // Enable/disable analytics reporting
    setAnalytics(enabled) {
        this.isAnalyticsEnabled = enabled;
    }
}

// Create global enhanced error handler instance
window.aetherstoreErrorHandler = new EnhancedAetherstoreErrorHandler();

// Enhance existing IWSDK systems with error handling
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

// Enhance AI Fashion Assistant with error handling
if (window.AIFashionAssistant) {
    const originalAICall = window.AIFashionAssistant.prototype.getRecommendations;
    window.AIFashionAssistant.prototype.getRecommendations = async function(filters = {}) {
        return window.aetherstoreErrorHandler.safeAiCall(async () => {
            return await originalAICall.call(this, filters);
        }, 'AI Fashion Assistant getRecommendations');
    };
}

console.log('Enhanced Aetherstore Error Handler Initialized');