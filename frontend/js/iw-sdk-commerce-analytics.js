// iw-sdk-commerce-analytics.js
// IWSDK Commerce and Analytics Integration for Aetherstore Engine

class IWSDKCommerceAnalytics {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.userEvents = [];
        this.productViews = new Map();
        this.sessionData = {
            sessionId: null,
            startTime: null,
            storeId: null,
            userId: null
        };
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK Commerce and Analytics Integration...');
        
        // Generate a session ID
        this.sessionData.sessionId = this.generateSessionId();
        this.sessionData.startTime = new Date();
        
        // Track initial page view
        this.trackEvent('page_view', {
            page: 'store',
            url: window.location.href
        });
        
        console.log('IWSDK Commerce and Analytics Integration initialized');
    }
    
    // Generate a unique session ID
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // Set store and user context for tracking
    setContext(storeId, userId) {
        this.sessionData.storeId = storeId;
        this.sessionData.userId = userId;
    }
    
    // Track a user event
    trackEvent(eventType, eventData = {}) {
        const event = {
            event_type: eventType,
            user_id: this.sessionData.userId || 'anonymous',
            session_id: this.sessionData.sessionId,
            store_id: this.sessionData.storeId || 'unknown',
            timestamp: new Date().toISOString(),
            data: eventData
        };
        
        // Add to local event queue
        this.userEvents.push(event);
        
        // Send to analytics backend
        this.sendEventToBackend(event);
        
        // Also send to any integrated analytics services (like Google Analytics)
        this.sendToIntegratedServices(event);
        
        console.log(`Tracked event: ${eventType}`, eventData);
        return event;
    }
    
    // Send event to backend analytics service
    async sendEventToBackend(event) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/analytics/event`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: event.event_type,
                    user_id: event.user_id,
                    session_id: event.session_id,
                    store_id: event.store_id,
                    timestamp: event.timestamp,
                    additional_data: event.data
                })
            });
            
            if (!response.ok) {
                console.error('Failed to send event to backend:', response.status, await response.text());
            }
        } catch (error) {
            console.error('Error sending event to backend:', error);
        }
    }
    
    // Send event to integrated analytics services (like Google Analytics)
    sendToIntegratedServices(event) {
        // In a real implementation, this would send to services like Google Analytics
        // For now, we'll just log the event would be sent
        
        // Example for Google Analytics 4 (gtag):
        if (typeof gtag !== 'undefined') {
            gtag('event', event.event_type, {
                ...event.data,
                session_id: event.session_id,
                store_id: event.store_id
            });
        }
        
        // Example for other services would go here
    }
    
    // Track product view
    trackProductView(productId, productName) {
        this.trackEvent('product_view', {
            product_id: productId,
            product_name: productName,
            time_spent: 0 // This would be calculated based on how long the product was viewed
        });
        
        // Record that this product has been viewed
        this.productViews.set(productId, {
            firstView: new Date(),
            lastView: new Date(),
            viewCount: (this.productViews.get(productId)?.viewCount || 0) + 1
        });
    }
    
    // Track product interaction (hover, click, etc.)
    trackProductInteraction(productId, interactionType, additionalData = {}) {
        this.trackEvent('product_interaction', {
            product_id: productId,
            interaction_type: interactionType,
            ...additionalData
        });
    }
    
    // Track try-on event
    trackTryOnEvent(userId, productId, fitScore, duration) {
        this.trackEvent('try_on', {
            user_id: userId,
            product_id: productId,
            fit_score: fitScore,
            duration_seconds: duration
        });
    }
    
    // Track purchase event
    async trackPurchase(userId, productId, price, additionalData = {}) {
        const purchaseEvent = this.trackEvent('purchase', {
            user_id: userId,
            product_id: productId,
            price: price,
            ...additionalData
        });
        
        // In a real implementation, this would also call the purchase endpoint
        try {
            const response = await fetch(`${this.apiBaseUrl}/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    product_id: productId,
                    price: price,
                    session_id: this.sessionData.sessionId,
                    ...additionalData
                })
            });
            
            if (!response.ok) {
                console.error('Failed to record purchase in backend:', response.status, await response.text());
            }
        } catch (error) {
            console.error('Error recording purchase in backend:', error);
        }
        
        return purchaseEvent;
    }
    
    // Track item added to cart
    trackAddToCart(userId, productId, additionalData = {}) {
        this.trackEvent('add_to_cart', {
            user_id: userId,
            product_id: productId,
            ...additionalData
        });
    }
    
    // Track item removed from cart
    trackRemoveFromCart(userId, productId, additionalData = {}) {
        this.trackEvent('remove_from_cart', {
            user_id: userId,
            product_id: productId,
            ...additionalData
        });
    }
    
    // Track search event
    trackSearch(userId, searchQuery, resultsCount, additionalData = {}) {
        this.trackEvent('search', {
            user_id: userId,
            search_query: searchQuery,
            results_count: resultsCount,
            ...additionalData
        });
    }
    
    // Track filter/sort event
    trackFilter(userId, filterType, filterValue, additionalData = {}) {
        this.trackEvent('filter', {
            user_id: userId,
            filter_type: filterType,
            filter_value: filterValue,
            ...additionalData
        });
    }
    
    // Track navigation event
    trackNavigation(fromPage, toPage, additionalData = {}) {
        this.trackEvent('navigation', {
            from_page: fromPage,
            to_page: toPage,
            ...additionalData
        });
    }
    
    // Get session metrics
    getSessionMetrics() {
        const now = new Date();
        const sessionDuration = (now - this.sessionData.startTime) / 1000; // in seconds
        
        return {
            sessionId: this.sessionData.sessionId,
            startTime: this.sessionData.startTime,
            duration: sessionDuration,
            userId: this.sessionData.userId,
            storeId: this.sessionData.storeId,
            eventCount: this.userEvents.length,
            productViews: this.productViews.size
        };
    }
    
    // Get product insights
    getProductInsights(productId) {
        const viewData = this.productViews.get(productId);
        if (!viewData) return null;
        
        return {
            productId: productId,
            totalViews: viewData.viewCount,
            firstView: viewData.firstView,
            lastView: viewData.lastView,
            timeOnProduct: (viewData.lastView - viewData.firstView) / 1000 // in seconds
        };
    }
    
    // Get all tracked events
    getTrackedEvents() {
        return [...this.userEvents];
    }
    
    // Get popular products based on view count
    getPopularProducts(limit = 10) {
        const productViewCounts = Array.from(this.productViews.entries())
            .map(([productId, data]) => ({
                productId,
                viewCount: data.viewCount
            }))
            .sort((a, b) => b.viewCount - a.viewCount)
            .slice(0, limit);
        
        return productViewCounts;
    }
    
    // Get user behavior insights
    getUserBehavior(userId) {
        const userEvents = this.userEvents.filter(event => event.user_id === userId);
        
        const behavior = {
            userId: userId,
            totalEvents: userEvents.length,
            pageViews: userEvents.filter(e => e.event_type === 'page_view').length,
            productViews: userEvents.filter(e => e.event_type === 'product_view').length,
            interactions: userEvents.filter(e => e.event_type === 'product_interaction').length,
            tryOns: userEvents.filter(e => e.event_type === 'try_on').length,
            purchases: userEvents.filter(e => e.event_type === 'purchase').length
        };
        
        return behavior;
    }
    
    // Send all pending events to server
    async flushEvents() {
        if (this.userEvents.length === 0) return;
        
        // In a real implementation, we would batch send events to the server
        // For now, we'll just send them one by one
        const eventsToProcess = [...this.userEvents];
        this.userEvents = []; // Clear the queue
        
        for (const event of eventsToProcess) {
            await this.sendEventToBackend(event);
        }
    }
    
    // Cleanup and send any remaining events
    async cleanup() {
        await this.flushEvents();
        console.log('IWSDK Commerce and Analytics cleanup completed');
    }
    
    // Get analytics report
    getAnalyticsReport() {
        const metrics = this.getSessionMetrics();
        const popularProducts = this.getPopularProducts(5);
        const totalPurchases = this.userEvents.filter(e => e.event_type === 'purchase').length;
        
        return {
            reportType: 'session_report',
            generatedAt: new Date().toISOString(),
            metrics: metrics,
            insights: {
                popularProducts: popularProducts,
                totalPurchases: totalPurchases,
                conversionRate: totalPurchases / Math.max(1, this.userEvents.filter(e => e.event_type === 'product_view').length)
            }
        };
    }
}

// Initialize commerce and analytics system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.iwSdkCommerceAnalytics = new IWSDKCommerceAnalytics();
    
    // Set up event listeners for tracking
    setupIWSDKEventTracking();
});

// Function to set up event tracking for IWSDK integration
function setupIWSDKEventTracking() {
    // Track when try-on sessions start
    if (window.iwSdkTryOnSystem) {
        // Set up listener for try-on events
        const originalTryOn = window.iwSdkTryOnSystem.tryOnItemWithFeedback;
        window.iwSdkTryOnSystem.tryOnItemWithFeedback = async function(userId, productId) {
            const start = Date.now();
            const result = await originalTryOn.call(this, userId, productId);
            const duration = (Date.now() - start) / 1000;
            
            if (window.iwSdkCommerceAnalytics && result.success) {
                window.iwSdkCommerceAnalytics.trackTryOnEvent(
                    userId, 
                    productId, 
                    result.fitAnalysis?.score || 0, 
                    duration
                );
            }
            
            return result;
        };
    }
    
    // Track when products are added to cart
    if (window.aetherstoreEngine) {
        const originalAddToCart = window.aetherstoreEngine.addToCart;
        window.aetherstoreEngine.addToCart = function(product) {
            if (window.iwSdkCommerceAnalytics) {
                window.iwSdkCommerceAnalytics.trackAddToCart(
                    window.aetherstoreEngine.user?.id || 'unknown', 
                    product.id,
                    { product_name: product.name, price: product.price }
                );
                
                // Track purchase (since add to cart immediately adds to cart in our demo)
                window.iwSdkCommerceAnalytics.trackPurchase(
                    window.aetherstoreEngine.user?.id || 'unknown',
                    product.id,
                    product.price,
                    { product_name: product.name }
                );
            }
            
            return originalAddToCart.call(this, product);
        };
    }
    
    // Track product views when they are displayed
    if (window.iwSdkStore && window.iwSdkStore.productDisplaySystem) {
        const originalShowProductInfo = window.iwSdkStore.productDisplaySystem.showProductInfo;
        window.iwSdkStore.productDisplaySystem.showProductInfo = function(productId) {
            if (window.iwSdkCommerceAnalytics) {
                const product = this.getProduct(productId);
                if (product && product.data) {
                    window.iwSdkCommerceAnalytics.trackProductView(
                        productId, 
                        product.data.name
                    );
                }
            }
            
            return originalShowProductInfo.call(this, productId);
        };
    }
}

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IWSDKCommerceAnalytics;
}