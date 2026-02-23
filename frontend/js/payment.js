// Payment and Order Management System for Aetherstore Engine
// Handles payment processing, order management, and transaction tracking

class PaymentOrderManager {
    constructor() {
        this.cart = [];
        this.currentOrder = null;
        this.paymentMethods = [];
        this.orderHistory = [];
        
        this.init();
    }
    
    init() {
        console.log('Initializing Payment and Order Manager...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load payment methods
        this.loadPaymentMethods();
        
        // Load cart from local storage
        this.loadCart();
    }
    
    setupEventListeners() {
        // Event listeners for cart and checkout UI
        document.addEventListener('click', (e) => {
            if (e.target.id === 'checkout-btn') {
                this.initiateCheckout();
            }
            
            if (e.target.classList.contains('add-to-cart')) {
                const productId = e.target.getAttribute('data-product-id');
                this.addToCart(productId);
            }
            
            if (e.target.classList.contains('remove-from-cart')) {
                const productId = e.target.getAttribute('data-product-id');
                this.removeFromCart(productId);
            }
        });
        
        // Form submissions
        document.getElementById('payment-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.processPayment();
        });
        
        // Cart updates
        document.getElementById('update-cart')?.addEventListener('click', () => {
            this.updateCartQuantities();
        });
    }
    
    addToCart(productId, quantity = 1, size = null, color = null) {
        // Add a product to the cart
        console.log(`Adding product ${productId} to cart`);
        
        // Get product details
        const product = this.getProductById(productId);
        if (!product) {
            console.error(`Product ${productId} not found`);
            return;
        }
        
        // Check if item already in cart
        const existingItemIndex = this.cart.findIndex(item => 
            item.productId === productId && 
            item.selectedSize === size && 
            item.selectedColor === color
        );
        
        if (existingItemIndex > -1) {
            // Update quantity
            this.cart[existingItemIndex].quantity += quantity;
        } else {
            // Add new item
            const cartItem = {
                id: `cart_${Date.now()}`,
                productId: product.id,
                productName: product.name,
                price: product.price,
                quantity: quantity,
                selectedSize: size,
                selectedColor: color,
                imageUrl: product.assetUrl || 'images/placeholder.jpg'
            };
            
            this.cart.push(cartItem);
        }
        
        // Save cart to storage
        this.saveCart();
        
        // Update UI
        this.updateCartUI();
        
        console.log(`Cart updated. Total items: ${this.cart.length}`);
        
        // Show success message
        this.showNotification(`${product.name} added to cart!`);
    }
    
    removeFromCart(productId) {
        // Remove item from cart
        this.cart = this.cart.filter(item => item.productId !== productId);
        this.saveCart();
        this.updateCartUI();
        
        console.log(`Product ${productId} removed from cart`);
    }
    
    updateCartQuantities() {
        // Update quantities from cart UI
        const cartItems = document.querySelectorAll('.cart-item-row');
        
        cartItems.forEach(item => {
            const productId = item.getAttribute('data-product-id');
            const quantityInput = item.querySelector('.quantity-input');
            const newQuantity = parseInt(quantityInput.value);
            
            if (newQuantity > 0) {
                const cartItem = this.cart.find(c => c.productId === productId);
                if (cartItem) {
                    cartItem.quantity = newQuantity;
                }
            } else {
                // Remove item if quantity is 0 or less
                this.cart = this.cart.filter(c => c.productId !== productId);
            }
        });
        
        this.saveCart();
        this.updateCartUI();
    }
    
    getCartTotal() {
        // Calculate total price of items in cart
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }
    
    getCartItemCount() {
        // Get total number of items in cart
        return this.cart.reduce((count, item) => count + item.quantity, 0);
    }
    
    saveCart() {
        // Save cart to local storage
        localStorage.setItem('aetherstore_cart', JSON.stringify(this.cart));
    }
    
    loadCart() {
        // Load cart from local storage
        const savedCart = localStorage.getItem('aetherstore_cart');
        if (savedCart) {
            this.cart = JSON.parse(savedCart);
        }
    }
    
    updateCartUI() {
        // Update cart UI with current cart contents
        const cartCountEl = document.querySelector('.cart-count');
        const cartTotalEl = document.querySelector('.cart-total');
        
        if (cartCountEl) {
            cartCountEl.textContent = this.getCartItemCount();
        }
        
        if (cartTotalEl) {
            cartTotalEl.textContent = `$${this.getCartTotal().toFixed(2)}`;
        }
        
        // Update cart modal if it exists
        this.updateCartModal();
    }
    
    updateCartModal() {
        // Update cart modal with cart contents
        const cartModal = document.getElementById('cart-modal');
        if (!cartModal) return;
        
        const cartItemsContainer = cartModal.querySelector('.cart-items');
        if (!cartItemsContainer) return;
        
        if (this.cart.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
            return;
        }
        
        let cartHTML = '';
        this.cart.forEach(item => {
            cartHTML += `
                <div class="cart-item-row" data-product-id="${item.productId}">
                    <img src="${item.imageUrl}" alt="${item.productName}" class="cart-item-image">
                    <div class="cart-item-details">
                        <h4>${item.productName}</h4>
                        <p>Size: ${item.selectedSize || 'N/A'}</p>
                        <p>Color: ${item.selectedColor || 'N/A'}</p>
                        <p class="cart-item-price">$${item.price.toFixed(2)} each</p>
                    </div>
                    <div class="cart-item-quantity">
                        <input type="number" class="quantity-input" value="${item.quantity}" min="1">
                        <button class="remove-from-cart" data-product-id="${item.productId}">Remove</button>
                    </div>
                    <div class="cart-item-subtotal">
                        $${(item.price * item.quantity).toFixed(2)}
                    </div>
                </div>
            `;
        });
        
        cartItemsContainer.innerHTML = cartHTML;
        
        // Add event listeners for quantity updates and removals
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', () => this.updateCartQuantities());
        });
        
        document.querySelectorAll('.remove-from-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const productId = e.target.getAttribute('data-product-id');
                this.removeFromCart(productId);
            });
        });
    }
    
    initiateCheckout() {
        // Start the checkout process
        console.log('Initiating checkout process...');
        
        if (this.cart.length === 0) {
            this.showNotification('Your cart is empty!', 'error');
            return;
        }
        
        // Validate all cart items are available
        for (const item of this.cart) {
            if (!this.validateCartItem(item)) {
                this.showNotification(`Item ${item.productName} is unavailable`, 'error');
                return;
            }
        }
        
        // Show checkout modal or page
        this.showCheckoutProcess();
    }
    
    validateCartItem(item) {
        // Validate that cart item is still available
        const product = this.getProductById(item.productId);
        if (!product) return false;
        
        // Check stock availability
        if (product.stock_quantity !== undefined && product.stock_quantity < item.quantity) {
            return false;
        }
        
        return true;
    }
    
    showCheckoutProcess() {
        // Show the checkout process (could be a modal or new page)
        console.log('Showing checkout process');
        
        // In a real implementation, this would show a checkout form
        // For now, we'll simulate with a modal
        alert('Proceeding to checkout...\nIn a real implementation, this would show shipping and payment details.');
        
        this.showShippingAddressForm();
    }
    
    showShippingAddressForm() {
        // Show shipping address form
        console.log('Showing shipping address form');
        
        // In a real implementation, this would show a form
        // For now, we'll use a simple form simulation
        const address = this.getSavedAddress();
        
        if (address) {
            console.log('Using saved address:', address);
            this.showPaymentForm(address);
        } else {
            console.log('No saved address, showing form');
            this.showAddressForm();
        }
    }
    
    async showAddressForm() {
        // Show address form
        const address = await this.getAddressFromUser();
        if (address) {
            this.saveAddress(address);
            this.showPaymentForm(address);
        }
    }
    
    showPaymentForm(address) {
        // Show payment form
        console.log('Showing payment form');
        
        // In a real implementation, this would integrate with payment providers
        // For now, we'll simulate with a form
        const paymentMethod = this.selectPaymentMethod();
        if (paymentMethod) {
            this.processPayment(address, paymentMethod);
        }
    }
    
    selectPaymentMethod() {
        // Show payment method selection
        // In a real implementation, this would show saved payment methods and form for new ones
        console.log('Selecting payment method');
        
        // Simulate payment method selection
        return {
            id: 'pm_' + Date.now(),
            type: 'credit_card',
            last4: '1234',
            brand: 'Visa'
        };
    }
    
    async processPayment(address, paymentMethod) {
        // Process the payment
        console.log('Processing payment...');
        
        // Create order object
        const order = {
            id: 'order_' + Date.now(),
            userId: window.aetherstoreEngine?.user?.id || 'guest',
            items: this.cart.map(item => ({
                productId: item.productId,
                quantity: item.quantity,
                price: item.price,
                selectedSize: item.selectedSize,
                selectedColor: item.selectedColor
            })),
            totalAmount: this.getCartTotal(),
            shippingAddress: address,
            billingAddress: address, // Using same for simplicity
            paymentMethod: paymentMethod,
            status: 'processing',
            createdAt: new Date().toISOString()
        };
        
        console.log('Processing order:', order);
        
        try {
            // Simulate payment processing
            const paymentResult = await this.simulatePayment(order);
            
            if (paymentResult.success) {
                // Update order status
                order.status = 'paid';
                order.paymentStatus = 'completed';
                order.paymentId = paymentResult.transactionId;
                
                // Save order to history
                this.orderHistory.push(order);
                this.saveOrderHistory();
                
                // Clear cart
                this.cart = [];
                this.saveCart();
                this.updateCartUI();
                
                console.log('Payment successful:', paymentResult);
                this.showOrderConfirmation(order);
                
                return order;
            } else {
                console.error('Payment failed:', paymentResult.error);
                this.showNotification('Payment failed. Please try again.', 'error');
                return null;
            }
        } catch (error) {
            console.error('Payment error:', error);
            this.showNotification('An error occurred during payment. Please try again.', 'error');
            return null;
        }
    }
    
    async simulatePayment(order) {
        // Simulate payment processing
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulate 90% success rate
                const success = Math.random() > 0.1;
                
                if (success) {
                    resolve({
                        success: true,
                        transactionId: 'txn_' + Date.now(),
                        amount: order.totalAmount,
                        method: order.paymentMethod.type
                    });
                } else {
                    resolve({
                        success: false,
                        error: 'Payment declined by bank',
                        code: 'PAYMENT_DECLINED'
                    });
                }
            }, 2000); // Simulate processing time
        });
    }
    
    showOrderConfirmation(order) {
        // Show order confirmation
        console.log('Showing order confirmation:', order);
        
        // In a real implementation, this would show a nice confirmation page
        // For now, we'll show an alert
        const itemsList = order.items.map(item => `- ${item.quantity}x ${this.getProductName(item.productId)}`).join('\n');
        
        alert(`Order Confirmed!\n\nOrder ID: ${order.id}\nItems:\n${itemsList}\nTotal: $${order.totalAmount.toFixed(2)}\n\nThank you for your purchase!`);
    }
    
    async loadPaymentMethods() {
        // Load saved payment methods
        // In a real implementation, this would fetch from the backend
        this.paymentMethods = [
            {
                id: 'pm_1',
                type: 'credit_card',
                brand: 'Visa',
                last4: '1234',
                expiryMonth: '12',
                expiryYear: '2027',
                isDefault: true
            },
            {
                id: 'pm_2',
                type: 'credit_card',
                brand: 'Mastercard',
                last4: '5678',
                expiryMonth: '06',
                expiryYear: '2026',
                isDefault: false
            }
        ];
        
        console.log('Payment methods loaded:', this.paymentMethods.length);
    }
    
    async addPaymentMethod(paymentData) {
        // Add a new payment method
        const newMethod = {
            id: 'pm_' + Date.now(),
            type: paymentData.type,
            brand: paymentData.brand,
            last4: paymentData.last4,
            expiryMonth: paymentData.expiryMonth,
            expiryYear: paymentData.expiryYear,
            isDefault: this.paymentMethods.length === 0 // Set as default if first
        };
        
        this.paymentMethods.push(newMethod);
        console.log('New payment method added:', newMethod);
        
        // In a real implementation, this would save to backend
        return newMethod;
    }
    
    getDefaultPaymentMethod() {
        // Get the default payment method
        return this.paymentMethods.find(method => method.isDefault) || this.paymentMethods[0];
    }
    
    saveAddress(address) {
        // Save address to local storage
        localStorage.setItem('aetherstore_shipping_address', JSON.stringify(address));
    }
    
    getSavedAddress() {
        // Get saved address from local storage
        const addressStr = localStorage.getItem('aetherstore_shipping_address');
        return addressStr ? JSON.parse(addressStr) : null;
    }
    
    async getAddressFromUser() {
        // Get address from user (in a real implementation, this would show a form)
        // For simulation, we'll return a mock address
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    name: window.aetherstoreEngine?.user?.name || 'John Doe',
                    address1: '123 Main St',
                    address2: 'Apt 4B',
                    city: 'New York',
                    state: 'NY',
                    country: 'USA',
                    zipCode: '10001',
                    phone: '+1 (555) 123-4567'
                });
            }, 500);
        });
    }
    
    async getOrderHistory(userId = null) {
        // Get order history for user
        const targetUserId = userId || window.aetherstoreEngine?.user?.id || 'guest';
        
        // In a real implementation, this would fetch from the backend
        // For now, return the local order history
        return this.orderHistory.filter(order => order.userId === targetUserId);
    }
    
    async getOrderDetails(orderId) {
        // Get details for a specific order
        return this.orderHistory.find(order => order.id === orderId);
    }
    
    saveOrderHistory() {
        // Save order history to local storage
        localStorage.setItem('aetherstore_order_history', JSON.stringify(this.orderHistory));
    }
    
    loadOrderHistory() {
        // Load order history from local storage
        const historyStr = localStorage.getItem('aetherstore_order_history');
        if (historyStr) {
            this.orderHistory = JSON.parse(historyStr);
        }
    }
    
    async trackOrder(orderId) {
        // Track an order
        const order = await this.getOrderDetails(orderId);
        if (!order) {
            console.error('Order not found:', orderId);
            return null;
        }
        
        // In a real implementation, this would track with the shipping provider
        // For now, simulate with mock tracking data
        return {
            orderId: order.id,
            status: 'shipped',
            carrier: 'FedEx',
            trackingNumber: '1234567890',
            estimatedDelivery: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days
            shippedDate: new Date(),
            progress: [
                { status: 'Order Placed', date: order.createdAt, location: 'Processing Center' },
                { status: 'Processed', date: new Date(), location: 'Processing Center' },
                { status: 'Shipped', date: new Date(), location: 'Shipping Facility' }
            ]
        };
    }
    
    getProductById(productId) {
        // Get product by ID from the main application
        if (window.aetherstoreEngine && window.aetherstoreEngine.products) {
            return window.aetherstoreEngine.products.find(p => p.id === productId);
        }
        return null;
    }
    
    getProductName(productId) {
        // Get product name by ID
        const product = this.getProductById(productId);
        return product ? product.name : 'Unknown Product';
    }
    
    showNotification(message, type = 'success') {
        // Show a notification message
        console.log(`${type}: ${message}`);
        
        // In a real implementation, this would show a visual notification
        // For now, we'll use console and potentially an alert for errors
        if (type === 'error') {
            alert(message);
        }
    }
    
    // Integration methods for other modules
    async process3DTryOnPurchase(productId, size, color) {
        // Process a purchase that came from the 3D try-on experience
        console.log(`3D Try-on purchase: ${productId}, size: ${size}, color: ${color}`);
        
        // Add to cart with selected options
        this.addToCart(productId, 1, size, color);
        
        // Proceed to checkout
        this.initiateCheckout();
    }
    
    async getRecommendedProductsForOrder(orderId) {
        // Get recommended products based on an order
        const order = await this.getOrderDetails(orderId);
        if (!order) return [];
        
        // Use AI engine to get recommendations
        if (window.aiEngine) {
            const userId = order.userId;
            const firstProductId = order.items[0]?.productId;
            return await window.aiEngine.getPersonalizedRecommendations(userId, firstProductId);
        }
        
        // Fallback to simple recommendations
        return [
            { id: 'rec_001', name: 'Complementary Accessory', score: 0.85 },
            { id: 'rec_002', name: 'Similar Style Item', score: 0.78 }
        ];
    }
    
    // Refund and return handling
    async initiateReturn(orderId, productId, reason) {
        // Initiate a return for an order
        const order = await this.getOrderDetails(orderId);
        if (!order) {
            throw new Error('Order not found');
        }
        
        // Find the specific item in the order
        const orderItem = order.items.find(item => item.productId === productId);
        if (!orderItem) {
            throw new Error('Product not found in order');
        }
        
        // Create return request
        const returnRequest = {
            id: 'return_' + Date.now(),
            orderId: orderId,
            productId: productId,
            quantity: orderItem.quantity,
            reason: reason,
            status: 'pending',
            requestedAt: new Date().toISOString(),
            processedAt: null
        };
        
        console.log('Return requested:', returnRequest);
        
        // In a real implementation, this would be sent to the backend
        return returnRequest;
    }
    
    // Payment method validation
    validatePaymentDetails(paymentMethod) {
        // Validate payment method details
        if (!paymentMethod) return { valid: false, error: 'No payment method provided' };
        
        if (paymentMethod.type === 'credit_card') {
            if (!paymentMethod.cardNumber || paymentMethod.cardNumber.length < 16) {
                return { valid: false, error: 'Invalid card number' };
            }
            
            if (!paymentMethod.cvv || paymentMethod.cvv.length < 3) {
                return { valid: false, error: 'Invalid CVV' };
            }
            
            if (!paymentMethod.expiryMonth || !paymentMethod.expiryYear) {
                return { valid: false, error: 'Invalid expiry date' };
            }
        }
        
        return { valid: true };
    }
}

// Initialize payment order manager
document.addEventListener('DOMContentLoaded', () => {
    window.paymentOrderManager = new PaymentOrderManager();
});