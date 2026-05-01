// security.js
// Security Implementation for Aetherstore Engine with IWSDK

class AetherstoreSecurity {
    constructor() {
        this.jwtToken = null;
        this.userId = null;
        this.permissions = [];
        this.csrfToken = null;
        this.userPreferences = new IWSDK.UserPreferences();
        
        // Initialize security measures
        this.initSecurity();
    }
    
    initSecurity() {
        // Load stored authentication data
        this.loadAuthData();
        
        // Set up security headers monitoring
        this.setupSecurityMonitoring();
        
        // Initialize CSRF protection
        this.initCsrfProtection();
        
        console.log('Aetherstore Security initialized');
    }
    
    // Load authentication data from storage
    loadAuthData() {
        try {
            const storedToken = localStorage.getItem('authToken');
            const storedUserId = localStorage.getItem('userId');
            const storedPermissions = localStorage.getItem('permissions');
            
            if (storedToken) {
                this.jwtToken = storedToken;
                this.userId = storedUserId;
                this.permissions = storedPermissions ? JSON.parse(storedPermissions) : [];
                
                // Verify token is still valid
                if (!this.isTokenValid()) {
                    this.clearAuthData();
                }
            }
        } catch (error) {
            console.error('Error loading auth data:', error);
        }
    }
    
    // Initialize CSRF protection
    initCsrfProtection() {
        // Generate CSRF token if not already present
        if (!this.csrfToken) {
            this.csrfToken = this.generateCsrfToken();
        }
        
        // Store CSRF token
        localStorage.setItem('csrfToken', this.csrfToken);
    }
    
    // Generate CSRF token
    generateCsrfToken() {
        return Array.from({length: 64}, () => 
            Math.random().toString(36)[2] || Math.random().toString(36).substring(2)
        ).join('').substring(0, 64);
    }
    
    // Setup security monitoring
    setupSecurityMonitoring() {
        // Monitor for security-related events
        this.setupContentSecurityMonitoring();
        this.setupInputValidation();
    }
    
    // Setup content security monitoring
    setupContentSecurityMonitoring() {
        // Monitor for potential XSS attempts
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            // Validate that listener is a function to prevent XSS
            if (typeof listener !== 'function') {
                console.warn('Potential XSS attempt detected: non-function listener');
                return;
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
    }
    
    // Setup input validation
    setupInputValidation() {
        // Add validation to form inputs
        document.addEventListener('input', (event) => {
            if (event.target.type === 'text' || event.target.type === 'textarea') {
                // Sanitize input to prevent XSS
                const sanitizedValue = this.sanitizeInput(event.target.value);
                if (sanitizedValue !== event.target.value) {
                    event.target.value = sanitizedValue;
                    console.warn('Potentially unsafe input detected and sanitized');
                }
            }
        });
    }
    
    // Sanitize input to prevent XSS
    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Remove potential script tags and other dangerous content
        return input
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/javascript:/gi, '')
            .replace(/on\w+\s*=/gi, '')
            .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
            .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
            .replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '');
    }
    
    // Authenticate user
    async authenticate(credentials) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrfToken
                },
                body: JSON.stringify(credentials)
            });
            
            if (!response.ok) {
                throw new Error(`Authentication failed: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Validate response structure
            if (!data.token || !data.user) {
                throw new Error('Invalid authentication response');
            }
            
            // Store authentication data
            this.jwtToken = data.token;
            this.userId = data.user.id;
            this.permissions = data.user.permissions || [];
            
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userId', data.user.id);
            localStorage.setItem('permissions', JSON.stringify(this.permissions));
            
            return { success: true, user: data.user };
        } catch (error) {
            console.error('Authentication error:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Logout user
    logout() {
        this.clearAuthData();
        window.location.href = '/login';
    }
    
    // Clear authentication data
    clearAuthData() {
        this.jwtToken = null;
        this.userId = null;
        this.permissions = [];
        
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('permissions');
    }
    
    // Check if token is valid
    isTokenValid() {
        if (!this.jwtToken) return false;
        
        try {
            // Decode JWT token to check expiration
            const payload = this.parseJwt(this.jwtToken);
            const currentTime = Math.floor(Date.now() / 1000);
            
            return payload.exp > currentTime;
        } catch (error) {
            console.error('Error validating token:', error);
            return false;
        }
    }
    
    // Parse JWT token
    parseJwt(token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        
        return JSON.parse(jsonPayload);
    }
    
    // Get auth headers for API requests
    getAuthHeaders() {
        const headers = {
            'X-CSRF-Token': this.csrfToken
        };
        
        if (this.jwtToken) {
            headers['Authorization'] = `Bearer ${this.jwtToken}`;
        }
        
        return headers;
    }
    
    // Check user permission
    hasPermission(permission) {
        return this.permissions.includes(permission) || this.permissions.includes('admin');
    }
    
    // Validate user input
    validateInput(input, rules) {
        const errors = [];
        
        for (const [field, rule] of Object.entries(rules)) {
            const value = input[field];
            
            if (rule.required && (value === undefined || value === null || value === '')) {
                errors.push(`${field} is required`);
            }
            
            if (value !== undefined && value !== null && value !== '') {
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
                
                if (rule.sanitize) {
                    input[field] = this.sanitizeInput(value);
                }
            }
        }
        
        if (errors.length > 0) {
            throw new Error(`Validation failed: ${errors.join(', ')}`);
        }
        
        return input;
    }
    
    // Validate 3D asset URL (to prevent malicious asset loading)
    validateAssetUrl(url) {
        // Only allow same-origin or trusted CDN domains
        try {
            const parsedUrl = new URL(url);
            const allowedDomains = [
                window.location.origin,
                'https://cdn.aetherstore.com',
                'https://models.aetherstore.com',
                'https://assets.example.com'
            ];
            
            if (!allowedDomains.includes(parsedUrl.origin)) {
                throw new Error(`Asset URL not from allowed domain: ${parsedUrl.origin}`);
            }
            
            return true;
        } catch (error) {
            throw new Error(`Invalid asset URL: ${error.message}`);
        }
    }
    
    // Validate API request
    validateApiRequest(url, options) {
        // Validate URL
        if (!url.startsWith('/api/')) {
            throw new Error('Invalid API endpoint');
        }
        
        // Validate HTTP method
        const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
        if (options.method && !allowedMethods.includes(options.method.toUpperCase())) {
            throw new Error(`Invalid HTTP method: ${options.method}`);
        }
        
        return true;
    }
    
    // Secure API request wrapper
    async secureApiRequest(endpoint, options = {}) {
        try {
            // Validate the request first
            this.validateApiRequest(endpoint, options);
            
            // Add authentication headers
            const headers = {
                ...this.getAuthHeaders(),
                ...(options.headers || {})
            };
            
            const requestUrl = endpoint.startsWith('http') ? endpoint : `/api${endpoint}`;
            
            const response = await fetch(requestUrl, {
                ...options,
                headers
            });
            
            if (response.status === 401) {
                // Unauthorized - token may be expired
                this.clearAuthData();
                window.location.href = '/login';
                return null;
            }
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Secure API request failed:', error);
            throw error;
        }
    }
    
    // Encrypt sensitive data
    encryptData(data) {
        // In a real implementation, use proper encryption
        // For now, just return base64 encoded data
        return btoa(encodeURIComponent(JSON.stringify(data)));
    }
    
    // Decrypt sensitive data
    decryptData(encryptedData) {
        // In a real implementation, use proper decryption
        // For now, just return base64 decoded data
        try {
            return JSON.parse(decodeURIComponent(atob(encryptedData)));
        } catch (error) {
            console.error('Error decrypting data:', error);
            return null;
        }
    }
    
    // Get security audit log
    getSecurityAuditLog() {
        // In a real implementation, this would return security events
        return [
            {
                timestamp: new Date().toISOString(),
                event: 'Security initialized',
                level: 'info'
            }
        ];
    }
}

// Initialize security system
window.aetherstoreSecurity = new AetherstoreSecurity();

// Enhance existing API request functions with security
if (window.aetherstoreErrorHandler) {
    // Wrap the error handler's safeApiRequest with security
    const originalSafeApiRequest = window.aetherstoreErrorHandler.safeApiRequest;
    window.aetherstoreErrorHandler.safeApiRequest = async function(url, options = {}, expectedResponseProps = []) {
        return window.aetherstoreSecurity.secureApiRequest(url, options);
    };
}

console.log('Aetherstore Security System Initialized');