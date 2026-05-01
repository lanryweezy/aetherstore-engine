// Store Management Module for Aetherstore Engine
// Handles 3D store environment, product displays, and interactions

class StoreManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.products = [];
        this.currentStore = null;
        this.storeEnvironment = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Store Manager...');
        
        // Wait for A-Frame scene to load
        const sceneEl = document.querySelector('a-scene');
        if (sceneEl) {
            sceneEl.addEventListener('loaded', async () => {
                this.scene = sceneEl;
                this.camera = document.getElementById('main-camera');
                this.storeEnvironment = document.getElementById('store-environment');
                
                // Fetch custom layout from API
                const storeId = window.location.pathname.split('/').pop();
                await this.loadCustomLayout(storeId);

                this.setupStoreEnvironment();
                this.loadStoreProducts();
            });
        }
    }

    async loadCustomLayout(storeId) {
        console.log('Fetching custom 3D layout for store:', storeId);
        try {
            const response = await fetch(`/api/stores/${storeId}/layout`);
            const layout = await response.json();
            if (layout && Object.keys(layout).length > 0) {
                this.applyCustomLayout(layout);
            }
        } catch (error) {
            console.warn('Could not load custom layout, using default template.');
        }
    }

    applyCustomLayout(layout) {
        // Dynamic repositioning of store props (mannequins, racks, etc.)
        Object.entries(layout).forEach(([id, transform]) => {
            const el = document.getElementById(id);
            if (el) {
                if (transform.position) el.setAttribute('position', transform.position);
                if (transform.rotation) el.setAttribute('rotation', transform.rotation);
                if (transform.scale) el.setAttribute('scale', transform.scale);
            }
        });
        console.log('Custom 3D layout applied successfully');
    }
    
    setupStoreEnvironment() {
        console.log('Setting up store environment...');
        
        // Set up lighting
        this.setupLighting();
        
        // Set up navigation
        this.setupNavigation();
        
        // Set up interaction system
        this.setupInteractionSystem();
    }
    
    setupLighting() {
        // Dynamic lighting system based on time of day or brand preference
        const ambientLight = document.querySelector('a-light[type="ambient"]');
        const directionalLight = document.querySelector('a-light[type="directional"]');
        
        // For now, use default settings from HTML
        console.log('Lighting system initialized');
    }
    
    setupNavigation() {
        // Set up basic movement controls
        const cameraRig = document.getElementById('camera-rig');
        
        // Add keyboard controls
        document.addEventListener('keydown', (e) => {
            const speed = 0.2;
            const position = cameraRig.getAttribute('position');
            
            switch(e.key.toLowerCase()) {
                case 'w':
                    position.z -= speed;
                    break;
                case 's':
                    position.z += speed;
                    break;
                case 'a':
                    position.x -= speed;
                    break;
                case 'd':
                    position.x += speed;
                    break;
                case 'q':
                    position.y -= speed;
                    break;
                case 'e':
                    position.y += speed;
                    break;
            }
            
            cameraRig.setAttribute('position', position);
        });
    }
    
    setupInteractionSystem() {
        // Set up raycasting for product interaction
        const cursor = document.getElementById('cursor');
        
        // Listen for intersections with products
        cursor.addEventListener('click', (e) => {
            if (e.detail.intersectedEl) {
                const intersectedEl = e.detail.intersectedEl;
                
                // Check if it's a product or try-on mirror
                if (intersectedEl.classList.contains('product')) {
                    const productId = intersectedEl.getAttribute('data-product-id');

                    // Track 3D intersection coordinates for Heatmap
                    const intersection = e.detail.intersection;
                    if (intersection) {
                        const coords = intersection.point;
                        console.log('3D Click at:', coords);
                        // In a real app, this would be a fetch() call to track the event
                    }

                    window.aetherstoreEngine.handleProductClick(productId);
                } 
                else if (intersectedEl.getAttribute('data-action') === 'tryon') {
                    window.aetherstoreEngine.startTryOnSession();
                }
            }
        });
        
        // Update cursor position and raycaster
        document.addEventListener('mousemove', (e) => {
            // For desktop, we'll use mouse movement to aim the raycaster
            // In VR, this would be handled by the headset orientation
        });
    }
    
    async loadStoreProducts() {
        // In real implementation, this would fetch products from the backend
        // For demo, we'll use the products already loaded in main.js
        this.products = window.aetherstoreEngine?.products || [];
        
        if (this.products.length > 0) {
            console.log(`Loaded ${this.products.length} products into the store`);
            this.positionProducts();
        }
    }
    
    positionProducts() {
        // Position products in the 3D space
        // This would be more sophisticated in a real implementation
        const displayAreas = [
            { id: 'display-1', position: { x: -5, y: 0, z: -5 } },
            { id: 'display-2', position: { x: 0, y: 0, z: -5 } },
            { id: 'display-3', position: { x: 5, y: 0, z: -5 } }
        ];
        
        this.products.forEach((product, index) => {
            if (index < displayAreas.length) {
                const displayArea = displayAreas[index];
                
                // Update the display area with product information
                const productEntity = document.querySelector(`#product-${index+1}`);
                if (productEntity) {
                    // Set product-specific attributes
                    productEntity.setAttribute('data-product-id', product.id);
                    
                    // Update the 3D model (in real implementation)
                    // For now, just log it
                    console.log(`Positioned ${product.name} at display ${displayArea.id}`);
                }
            }
        });
    }
    
    updateStoreLayout(storeSettings) {
        // Update the store environment based on brand preferences
        // This would include lighting, color scheme, layout, etc.
        if (!storeSettings) return;
        
        // Update environment based on template
        if (storeSettings.template) {
            this.applyStoreTemplate(storeSettings.template);
        }
        
        // Update products display
        if (storeSettings.products) {
            this.updateProductDisplays(storeSettings.products);
        }
        
        // Update ambient settings
        if (storeSettings.settings) {
            this.updateAmbientSettings(storeSettings.settings);
        }
    }
    
    applyStoreTemplate(templateName) {
        // Apply different visual themes based on store template
        const environment = this.storeEnvironment;
        
        switch(templateName) {
            case 'modern-gallery':
                // Clean, minimalist look
                document.querySelector('#store-floor').setAttribute('color', '#f0f0f0');
                document.querySelector('#back-wall').setAttribute('color', '#e8e8e8');
                break;
                
            case 'vintage-loft':
                // Industrial, brick-like textures
                document.querySelector('#store-floor').setAttribute('color', '#d2b48c');
                document.querySelector('#back-wall').setAttribute('color', '#a9a9a9');
                break;
                
            case 'luxury-palace':
                // Opulent, golden textures
                document.querySelector('#store-floor').setAttribute('color', '#f5f5dc');
                document.querySelector('#back-wall').setAttribute('color', '#dcdcdc');
                break;
                
            default:
                // Default template
                document.querySelector('#store-floor').setAttribute('color', '#f0f0f0');
                document.querySelector('#back-wall').setAttribute('color', '#e0e0e0');
        }
    }
    
    updateProductDisplays(products) {
        // Update which products are displayed based on the store's inventory
        this.products = products;
        this.positionProducts();
    }
    
    updateAmbientSettings(settings) {
        // Update ambient lighting, music, etc.
        if (settings.lighting) {
            // Update lighting based on settings
        }
        
        if (settings.music) {
            // Add background music if needed
        }
    }
    
    animateStore() {
        // Add subtle animations to make the store feel alive
        // This could include gently rotating products, changing lights, etc.
        
        // Rotate products slowly
        this.products.forEach((product, index) => {
            const productEntity = document.querySelector(`#product-${index+1}`);
            if (productEntity) {
                // Add a slow rotation animation
                productEntity.setAttribute('animation', {
                    property: 'rotation',
                    to: '0 360 0',
                    loop: 'true',
                    dur: 10000,
                    easing: 'linear'
                });
            }
        });
    }
    
    // Brand store creation tools
    createCustomStore(brandInfo) {
        // This would be part of the admin/brand interface
        // Create a new store layout based on brand's specifications
        const newStore = {
            id: `store_${Date.now()}`,
            name: brandInfo.name,
            brandId: brandInfo.id,
            template: brandInfo.template || 'modern-gallery',
            settings: {
                colorScheme: brandInfo.colors || {},
                lighting: brandInfo.lighting || 'default',
                layout: brandInfo.layout || 'grid'
            },
            products: [],
            createdAt: new Date()
        };
        
        return newStore;
    }
    
    updateStoreProducts(storeId, newProducts) {
        // Update products in a specific store
        console.log(`Updating products for store: ${storeId}`);
        
        // This would be called from the admin interface
        // when a brand wants to change their inventory
        
        // Update the local store
        this.products = newProducts;
        this.positionProducts();
    }
}

// Initialize store manager
document.addEventListener('DOMContentLoaded', () => {
    window.storeManager = new StoreManager();
});