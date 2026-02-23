// enhanced-analytics.js
// Enhanced Analytics for Aetherstore Engine with IWSDK Integration

class EnhancedAetherstoreAnalytics {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.userId = null;
        this.events = [];
        this.maxEvents = 1000;
        this.isTrackingEnabled = true;
        this.batchSize = 50;
        this.batchInterval = 30000; // 30 seconds
        this.batchTimer = null;
        this.apiEndpoint = '/api/analytics/events';
        
        // Enhanced tracking categories
        this.categories = {
            USER_INTERACTION: 'user-interaction',
            PRODUCT_VIEW: 'product-view',
            TRY_ON: 'try-on',
            CART: 'cart',
            PURCHASE: 'purchase',
            SOCIAL: 'social',
            VR: 'vr',
            AI_ASSISTANT: 'ai-assistant',
            AVATAR: 'avatar',
            PERFORMANCE: 'performance',
            ERROR: 'error',
            CUSTOM: 'custom'
        };
        
        // Enhanced event types
        this.eventTypes = {
            PAGE_VIEW: 'page-view',
            CLICK: 'click',
            HOVER: 'hover',
            SCROLL: 'scroll',
            KEY_PRESS: 'key-press',
            FORM_SUBMIT: 'form-submit',
            TRY_ON_START: 'try-on-start',
            TRY_ON_COMPLETE: 'try-on-complete',
            TRY_ON_CANCEL: 'try-on-cancel',
            ADD_TO_CART: 'add-to-cart',
            REMOVE_FROM_CART: 'remove-from-cart',
            CHECKOUT_START: 'checkout-start',
            PURCHASE_COMPLETED: 'purchase-completed',
            SOCIAL_SHARE: 'social-share',
            SOCIAL_INVITE: 'social-invite',
            VR_ENTER: 'vr-enter',
            VR_EXIT: 'vr-exit',
            AI_CHAT_START: 'ai-chat-start',
            AI_CHAT_END: 'ai-chat-end',
            AI_RECOMMENDATION: 'ai-recommendation',
            AVATAR_SCAN_START: 'avatar-scan-start',
            AVATAR_SCAN_COMPLETE: 'avatar-scan-complete',
            PERFORMANCE_METRIC: 'performance-metric',
            ERROR_OCCURRED: 'error-occurred'
        };
        
        // Initialize enhanced analytics
        this.init();
    }
    
    init() {
        console.log('Initializing Enhanced Aetherstore Analytics...');
        
        // Set up automatic session tracking
        this.trackEvent(this.eventTypes.PAGE_VIEW, {
            url: window.location.href,
            referrer: document.referrer,
            title: document.title
        });
        
        // Set up performance tracking
        this.setupPerformanceTracking();
        
        // Set up batch sending
        this.setupBatchSending();
        
        // Set up unload tracking
        this.setupUnloadTracking();
        
        console.log('Enhanced Aetherstore Analytics initialized');
    }
    
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    setUserId(userId) {
        this.userId = userId;
        console.log(`Analytics user ID set to: ${userId}`);
    }
    
    setContext(context, value) {
        // Set contextual information for all events
        this.context = this.context || {};
        this.context[context] = value;
        console.log(`Analytics context updated: ${context} = ${value}`);
    }
    
    // Enhanced tracking methods
    trackEvent(eventType, data = {}) {
        if (!this.isTrackingEnabled) return;
        
        const event = {
            id: `event_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
            type: eventType,
            category: this.categorizeEvent(eventType),
            data: {
                ...data,
                ...this.context // Include contextual information
            },
            userId: this.userId,
            sessionId: this.sessionId,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            screenWidth: screen.width,
            screenHeight: screen.height,
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight
        };
        
        // Add to events queue
        this.events.push(event);
        
        // Maintain queue size
        if (this.events.length > this.maxEvents) {
            this.events.shift();
        }
        
        console.log(`Enhanced analytics event tracked: ${eventType}`, data);
        
        // Send immediately for critical events
        if (this.isCriticalEvent(eventType)) {
            this.sendEventImmediately(event);
        }
        
        return event;
    }
    
    categorizeEvent(eventType) {
        // Categorize events based on type
        const categoryMap = {
            [this.eventTypes.PAGE_VIEW]: this.categories.USER_INTERACTION,
            [this.eventTypes.CLICK]: this.categories.USER_INTERACTION,
            [this.eventTypes.HOVER]: this.categories.USER_INTERACTION,
            [this.eventTypes.SCROLL]: this.categories.USER_INTERACTION,
            [this.eventTypes.KEY_PRESS]: this.categories.USER_INTERACTION,
            [this.eventTypes.FORM_SUBMIT]: this.categories.USER_INTERACTION,
            
            [this.eventTypes.TRY_ON_START]: this.categories.TRY_ON,
            [this.eventTypes.TRY_ON_COMPLETE]: this.categories.TRY_ON,
            [this.eventTypes.TRY_ON_CANCEL]: this.categories.TRY_ON,
            
            [this.eventTypes.ADD_TO_CART]: this.categories.CART,
            [this.eventTypes.REMOVE_FROM_CART]: this.categories.CART,
            [this.eventTypes.CHECKOUT_START]: this.categories.CART,
            
            [this.eventTypes.PURCHASE_COMPLETED]: this.categories.PURCHASE,
            
            [this.eventTypes.SOCIAL_SHARE]: this.categories.SOCIAL,
            [this.eventTypes.SOCIAL_INVITE]: this.categories.SOCIAL,
            
            [this.eventTypes.VR_ENTER]: this.categories.VR,
            [this.eventTypes.VR_EXIT]: this.categories.VR,
            
            [this.eventTypes.AI_CHAT_START]: this.categories.AI_ASSISTANT,
            [this.eventTypes.AI_CHAT_END]: this.categories.AI_ASSISTANT,
            [this.eventTypes.AI_RECOMMENDATION]: this.categories.AI_ASSISTANT,
            
            [this.eventTypes.AVATAR_SCAN_START]: this.categories.AVATAR,
            [this.eventTypes.AVATAR_SCAN_COMPLETE]: this.categories.AVATAR,
            
            [this.eventTypes.PERFORMANCE_METRIC]: this.categories.PERFORMANCE,
            
            [this.eventTypes.ERROR_OCCURRED]: this.categories.ERROR
        };
        
        return categoryMap[eventType] || this.categories.CUSTOM;
    }
    
    isCriticalEvent(eventType) {
        // Certain events should be sent immediately
        const criticalEvents = [
            this.eventTypes.PURCHASE_COMPLETED,
            this.eventTypes.ERROR_OCCURRED,
            this.eventTypes.VR_ENTER,
            this.eventTypes.VR_EXIT,
            this.eventTypes.FORM_SUBMIT
        ];
        
        return criticalEvents.includes(eventType);
    }
    
    sendEventImmediately(event) {
        // Send critical events immediately
        this.sendEvents([event]).catch(error => {
            console.warn('Failed to send critical event:', error);
        });
    }
    
    // Enhanced product interaction tracking
    trackProductView(productId, additionalData = {}) {
        return this.trackEvent('product-view', {
            productId: productId,
            ...additionalData
        });
    }
    
    trackProductInteraction(productId, interactionType, additionalData = {}) {
        return this.trackEvent('product-interaction', {
            productId: productId,
            interactionType: interactionType,
            ...additionalData
        });
    }
    
    trackTryOnEvent(userId, productId, fitScore, durationSeconds, additionalData = {}) {
        return this.trackEvent('try-on', {
            userId: userId,
            productId: productId,
            fitScore: fitScore,
            durationSeconds: durationSeconds,
            ...additionalData
        });
    }
    
    trackAddToCart(userId, productId, additionalData = {}) {
        return this.trackEvent('add-to-cart', {
            userId: userId,
            productId: productId,
            ...additionalData
        });
    }
    
    trackRemoveFromCart(userId, productId, additionalData = {}) {
        return this.trackEvent('remove-from-cart', {
            userId: userId,
            productId: productId,
            ...additionalData
        });
    }
    
    trackPurchase(userId, orderId, amount, items = [], additionalData = {}) {
        return this.trackEvent('purchase-completed', {
            userId: userId,
            orderId: orderId,
            amount: amount,
            itemCount: items.length,
            items: items,
            ...additionalData
        });
    }
    
    // Enhanced AI assistant tracking
    trackAIInteraction(interactionType, requestData, responseData, additionalData = {}) {
        return this.trackEvent('ai-assistant', {
            interactionType: interactionType,
            requestData: requestData,
            responseData: responseData,
            responseTime: responseData?.timestamp ? 
                (responseData.timestamp - requestData.timestamp) : undefined,
            ...additionalData
        });
    }
    
    // Enhanced avatar tracking
    trackAvatarEvent(eventType, avatarData, additionalData = {}) {
        return this.trackEvent(`avatar-${eventType}`, {
            avatarId: avatarData?.id,
            avatarType: avatarData?.type,
            ...avatarData,
            ...additionalData
        });
    }
    
    // Enhanced performance tracking
    setupPerformanceTracking() {
        // Track page load performance
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        this.trackEvent('performance-metric', {
                            metric: 'page-load',
                            value: perfData.loadEventEnd - perfData.fetchStart,
                            domContentLoaded: perfData.domContentLoadedEventEnd - perfData.fetchStart,
                            firstPaint: perfData.responseStart - perfData.fetchStart
                        });
                    }
                    
                    // Track memory usage if available
                    if ('memory' in performance) {
                        const memory = performance.memory;
                        this.trackEvent('performance-metric', {
                            metric: 'memory-usage',
                            used: memory.usedJSHeapSize,
                            total: memory.totalJSHeapSize,
                            limit: memory.jsHeapSizeLimit
                        });
                    }
                }, 1000); // Wait a bit for everything to load
            });
        }
        
        // Track FPS periodically
        let frameCount = 0;
        let lastTime = performance.now();
        let fps = 0;
        
        const trackFPS = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) { // Every second
                fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                frameCount = 0;
                lastTime = currentTime;
                
                // Track FPS as performance metric
                this.trackEvent('performance-metric', {
                    metric: 'fps',
                    value: fps,
                    category: fps < 30 ? 'poor' : fps < 60 ? 'good' : 'excellent'
                });
            }
            
            requestAnimationFrame(trackFPS);
        };
        
        requestAnimationFrame(trackFPS);
    }
    
    // Enhanced error tracking integration
    trackError(errorType, errorData, additionalData = {}) {
        return this.trackEvent('error-occurred', {
            errorType: errorType,
            errorData: errorData,
            ...additionalData
        });
    }
    
    // Batch sending setup
    setupBatchSending() {
        this.batchTimer = setInterval(() => {
            if (this.events.length > 0) {
                const batch = this.events.splice(0, Math.min(this.batchSize, this.events.length));
                this.sendEvents(batch).catch(error => {
                    console.warn('Failed to send analytics batch:', error);
                    // Put events back in queue
                    this.events.unshift(...batch);
                });
            }
        }, this.batchInterval);
    }
    
    // Unload tracking to capture final events
    setupUnloadTracking() {
        window.addEventListener('beforeunload', () => {
            // Send any remaining events immediately
            if (this.events.length > 0) {
                // For synchronous sending, we need to use sendBeacon
                if (navigator.sendBeacon) {
                    const data = JSON.stringify({
                        events: this.events,
                        sessionId: this.sessionId,
                        userId: this.userId
                    });
                    
                    navigator.sendBeacon(this.apiEndpoint, data);
                } else {
                    // Fallback: try to send synchronously
                    this.sendEventsSync(this.events);
                }
            }
        });
    }
    
    // Send events asynchronously
    async sendEvents(events) {
        if (events.length === 0) return;
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    events: events,
                    sessionId: this.sessionId,
                    userId: this.userId,
                    batchTimestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error(`Analytics send failed: ${response.status}`);
            }
            
            console.log(`Sent ${events.length} analytics events`);
        } catch (error) {
            console.warn('Failed to send analytics events:', error);
            throw error;
        }
    }
    
    // Send events synchronously (fallback for unload)
    sendEventsSync(events) {
        if (events.length === 0) return;
        
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', this.apiEndpoint, false); // Synchronous request
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                events: events,
                sessionId: this.sessionId,
                userId: this.userId,
                batchTimestamp: new Date().toISOString()
            }));
            
            console.log(`Sent ${events.length} analytics events synchronously`);
        } catch (error) {
            console.warn('Failed to send analytics events synchronously:', error);
        }
    }
    
    // Enhanced reporting methods
    getEventSummary() {
        const summary = {
            totalEvents: this.events.length,
            eventsByType: {},
            eventsByCategory: {},
            mostActivePages: {},
            sessionDuration: 0
        };
        
        // Count events by type and category
        this.events.forEach(event => {
            summary.eventsByType[event.type] = (summary.eventsByType[event.type] || 0) + 1;
            summary.eventsByCategory[event.category] = (summary.eventsByCategory[event.category] || 0) + 1;
            
            if (event.data?.url) {
                summary.mostActivePages[event.data.url] = (summary.mostActivePages[event.data.url] || 0) + 1;
            }
        });
        
        // Calculate session duration
        if (this.events.length > 0) {
            const firstEvent = new Date(this.events[0].timestamp);
            const lastEvent = new Date(this.events[this.events.length - 1].timestamp);
            summary.sessionDuration = (lastEvent - firstEvent) / 1000; // in seconds
        }
        
        return summary;
    }
    
    // Enhanced user behavior analysis
    getUserBehaviorInsights() {
        const insights = {
            engagementScore: 0,
            preferredCategories: [],
            interactionFrequency: 0,
            avgSessionLength: 0,
            bounceRate: 0
        };
        
        // Calculate engagement score based on event diversity and frequency
        const eventTypes = new Set(this.events.map(e => e.type));
        const uniqueEventCount = eventTypes.size;
        const totalEvents = this.events.length;
        
        insights.engagementScore = Math.min(100, (uniqueEventCount * 10) + (totalEvents / 10));
        
        // Find preferred categories
        const categoryCounts = {};
        this.events.forEach(event => {
            categoryCounts[event.category] = (categoryCounts[event.category] || 0) + 1;
        });
        
        insights.preferredCategories = Object.entries(categoryCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 3)
            .map(([category]) => category);
        
        // Calculate interaction frequency
        if (this.events.length > 1) {
            const timeSpan = new Date(this.events[this.events.length - 1].timestamp) - 
                           new Date(this.events[0].timestamp);
            insights.interactionFrequency = totalEvents / (timeSpan / 1000 / 60); // events per minute
        }
        
        return insights;
    }
    
    // Enhanced export methods
    exportEventData(format = 'json') {
        const exportData = {
            sessionId: this.sessionId,
            userId: this.userId,
            exportTimestamp: new Date().toISOString(),
            events: this.events,
            summary: this.getEventSummary(),
            insights: this.getUserBehaviorInsights()
        };
        
        switch (format.toLowerCase()) {
            case 'json':
                return JSON.stringify(exportData, null, 2);
            case 'csv':
                return this.convertToCSV(exportData.events);
            default:
                throw new Error(`Unsupported export format: ${format}`);
        }
    }
    
    convertToCSV(events) {
        if (events.length === 0) return '';
        
        // Get all possible keys for CSV headers
        const allKeys = new Set();
        events.forEach(event => {
            Object.keys(event).forEach(key => allKeys.add(key));
            if (event.data) {
                Object.keys(event.data).forEach(key => allKeys.add(`data.${key}`));
            }
        });
        
        const headers = Array.from(allKeys);
        const csvRows = [headers.join(',')];
        
        events.forEach(event => {
            const row = headers.map(header => {
                if (header.startsWith('data.')) {
                    const dataKey = header.substring(5);
                    return this.escapeCSVField(event.data?.[dataKey]);
                } else {
                    return this.escapeCSVField(event[header]);
                }
            });
            csvRows.push(row.join(','));
        });
        
        return csvRows.join('\n');
    }
    
    escapeCSVField(field) {
        if (field === null || field === undefined) return '';
        const stringField = String(field);
        if (stringField.includes(',') || stringField.includes('"') || stringField.includes('\n')) {
            return `"${stringField.replace(/"/g, '""')}"`;
        }
        return stringField;
    }
    
    // Enable/disable tracking
    setTracking(enabled) {
        this.isTrackingEnabled = enabled;
        console.log(`Analytics tracking ${enabled ? 'enabled' : 'disabled'}`);
    }
    
    // Clear event data
    clearEvents() {
        this.events = [];
        console.log('Analytics events cleared');
    }
}

// Create global enhanced analytics instance
window.iwSdkCommerceAnalytics = new EnhancedAetherstoreAnalytics();

// Enhance existing IWSDK systems with analytics tracking
if (window.IWSDK) {
    // Add analytics to IWSDK Core system
    const originalUpdate = window.IWSDK.Core.prototype.update;
    window.IWSDK.Core.prototype.update = function(deltaTime) {
        // Call original update
        const result = originalUpdate.call(this, deltaTime);
        
        // Track performance metrics if analytics is available
        if (window.iwSdkCommerceAnalytics && deltaTime) {
            window.iwSdkCommerceAnalytics.trackEvent('performance-metric', {
                metric: 'frame-update',
                value: deltaTime,
                system: 'iw-sdk-core'
            });
        }
        
        return result;
    };
    
    // Add analytics to Locomotion System
    const originalLocomotionUpdate = window.IWSDK.LocomotionSystem.prototype.update;
    window.IWSDK.LocomotionSystem.prototype.update = function(deltaTime, camera) {
        // Track movement events
        if (window.iwSdkCommerceAnalytics && this.moveForward) {
            window.iwSdkCommerceAnalytics.trackEvent('user-interaction', {
                interactionType: 'movement',
                direction: 'forward'
            });
        }
        
        return originalLocomotionUpdate.call(this, deltaTime, camera);
    };
    
    // Add analytics to Grab System
    const originalGrabUpdate = window.IWSDK.GrabSystem.prototype.update;
    window.IWSDK.GrabSystem.prototype.update = function() {
        // Track grab interactions
        if (window.iwSdkCommerceAnalytics && this.grabbedObjects.size > 0) {
            window.iwSdkCommerceAnalytics.trackEvent('user-interaction', {
                interactionType: 'grab-object',
                grabbedCount: this.grabbedObjects.size
            });
        }
        
        return originalGrabUpdate.call(this);
    };
}

// Enhance AI Fashion Assistant with analytics
if (window.AIFashionAssistant) {
    const originalAIResponse = window.AIFashionAssistant.ChatBot.prototype.respond;
    window.AIFashionAssistant.ChatBot.prototype.respond = async function(message) {
        const startTime = Date.now();
        
        try {
            const response = await originalAIResponse.call(this, message);
            
            // Track AI interaction
            if (window.iwSdkCommerceAnalytics) {
                window.iwSdkCommerceAnalytics.trackAIInteraction(
                    'chat-response',
                    { message: message, timestamp: startTime },
                    { response: response, timestamp: Date.now() }
                );
            }
            
            return response;
        } catch (error) {
            // Track AI error
            if (window.iwSdkCommerceAnalytics) {
                window.iwSdkCommerceAnalytics.trackError(
                    'ai-chat-error',
                    { message: error.message, stack: error.stack }
                );
            }
            
            throw error;
        }
    };
}

// Enhance 3D Avatar System with analytics
if (window.Avatar3DSystem) {
    const originalAvatarUpdate = window.Avatar3DSystem.prototype.animate;
    window.Avatar3DSystem.prototype.animate = function() {
        // Track avatar rendering performance
        if (window.iwSdkCommerceAnalytics) {
            const animateStartTime = performance.now();
            
            // Call original animation
            const result = originalAvatarUpdate.call(this);
            
            const animateEndTime = performance.now();
            window.iwSdkCommerceAnalytics.trackEvent('performance-metric', {
                metric: 'avatar-render',
                value: animateEndTime - animateStartTime,
                system: '3d-avatar'
            });
            
            return result;
        }
        
        return originalAvatarUpdate.call(this);
    };
}

console.log('Enhanced Aetherstore Analytics System Ready');