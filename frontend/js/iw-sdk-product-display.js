// iw-sdk-product-display.js
// IWSDK Product Display System for Aetherstore Engine

class IWSDKProductDisplay {
    constructor(storeScene) {
        this.storeScene = storeScene;
        this.products = {};
        this.displayStands = {};
        this.interactionManager = null;
        this.animationController = null;
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK Product Display System...');
        
        // Initialize interaction manager
        this.initInteractionManager();
        
        // Initialize animation controller
        this.initAnimationController();
        
        // Register with store scene
        if (this.storeScene) {
            this.storeScene.productDisplaySystem = this;
        }
        
        console.log('IWSDK Product Display System initialized');
    }
    
    initInteractionManager() {
        // Initialize IWSDK's interaction system
        this.interactionManager = {
            raycaster: new THREE.Raycaster(),
            mouse: new THREE.Vector2(),
            selectedObject: null,
            
            // Set up interaction event listeners
            initEvents: () => {
                document.addEventListener('click', this.handleInteraction.bind(this), false);
                document.addEventListener('mousemove', this.onMouseMove.bind(this), false);
            },
            
            // Mouse move handler for hover effects
            onMouseMove: (event) => {
                // Calculate mouse position in normalized device coordinates
                this.interactionManager.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                this.interactionManager.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
                
                // Update the picking ray with the camera and mouse position
                this.interactionManager.raycaster.setFromCamera(
                    this.interactionManager.mouse, 
                    this.storeScene.camera
                );
                
                // Calculate objects intersecting the picking ray
                const intersects = this.interactionManager.raycaster.intersectObjects(
                    Object.values(this.products).map(p => p.mesh)
                );
                
                // Handle hover effects
                this.handleHover(intersects);
            },
            
            // Handle interaction (click) events
            handleInteraction: (event) => {
                // Calculate mouse position in normalized device coordinates
                this.interactionManager.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                this.interactionManager.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
                
                // Update the picking ray with the camera and mouse position
                this.interactionManager.raycaster.setFromCamera(
                    this.interactionManager.mouse, 
                    this.storeScene.camera
                );
                
                // Calculate objects intersecting the picking ray
                const intersects = this.interactionManager.raycaster.intersectObjects(
                    Object.values(this.products).map(p => p.mesh)
                );
                
                if (intersects.length > 0) {
                    const product = intersects[0].object;
                    this.handleProductClick(product.userData.productId);
                }
            },
            
            // Handle hover effects
            handleHover: (intersects) => {
                // Reset previous hover state
                if (this.interactionManager.selectedObject) {
                    this.resetHoverState(this.interactionManager.selectedObject);
                }
                
                // Set hover state for new object
                if (intersects.length > 0) {
                    const product = intersects[0].object;
                    this.setHoverState(product);
                    this.interactionManager.selectedObject = product;
                } else {
                    this.interactionManager.selectedObject = null;
                }
            },
            
            // Set hover state for product
            setHoverState: (product) => {
                if (product.userData && product.userData.originalMaterial) {
                    // Make material slightly brighter on hover
                    product.material.emissive = new THREE.Color(0x333333);
                }
            },
            
            // Reset hover state for product
            resetHoverState: (product) => {
                if (product.userData && product.userData.originalMaterial) {
                    product.material.emissive = new THREE.Color(0x000000);
                }
            }
        };
        
        // Initialize event listeners
        this.interactionManager.initEvents();
    }
    
    initAnimationController() {
        // Initialize animation system for products
        this.animationController = {
            // Animate product selection
            animateSelection: (productMesh) => {
                if (!productMesh) return;
                
                // Store original scale
                const originalScale = productMesh.scale.clone();
                
                // Scale up
                this.animateScale(productMesh, originalScale.clone().multiplyScalar(1.3), 0.2);
                
                // Scale back down after delay
                setTimeout(() => {
                    this.animateScale(productMesh, originalScale, 0.2);
                }, 200);
            },
            
            // Animate scale change
            animateScale: (productMesh, targetScale, duration) => {
                const startScale = productMesh.scale.clone();
                const startTime = Date.now();
                
                const animate = () => {
                    const elapsed = (Date.now() - startTime) / 1000; // in seconds
                    const progress = Math.min(elapsed / duration, 1);
                    
                    // Ease function for smooth animation
                    const easeProgress = 1 - Math.pow(1 - progress, 3);
                    
                    // Update scale
                    productMesh.scale.lerpVectors(startScale, targetScale, easeProgress);
                    
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    }
                };
                
                animate();
            },
            
            // Animate floating effect for products
            animateFloating: (productMesh) => {
                if (!productMesh || !productMesh.userData) return;
                
                const floatOffset = productMesh.userData.floatOffset || Math.random() * Math.PI * 2;
                const floatSpeed = productMesh.userData.floatSpeed || 1;
                const originalY = productMesh.userData.originalY || productMesh.position.y;
                
                const time = Date.now() * 0.001;
                productMesh.position.y = originalY + Math.sin(time * floatSpeed + floatOffset) * 0.1;
                
                // Add subtle rotation
                productMesh.rotation.y += 0.005;
            }
        };
    }
    
    // Create a product display stand
    createDisplayStand(x, z, rotation = 0, standId = null) {
        if (!standId) {
            standId = `stand_${Date.now()}`;
        }
        
        // Create a group for the stand
        const standGroup = new THREE.Group();
        
        // Base platform
        const baseGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.2, 16);
        const baseMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x8B4513,
            roughness: 0.9,
            metalness: 0.1
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.1;
        base.castShadow = true;
        base.receiveShadow = true;
        standGroup.add(base);
        
        // Stand pole
        const poleGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1.5, 8);
        const poleMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x654321,
            roughness: 0.8,
            metalness: 0.2
        });
        const pole = new THREE.Mesh(poleGeometry, poleMaterial);
        pole.position.y = 0.95;
        pole.castShadow = true;
        standGroup.add(pole);
        
        // Display top
        const topGeometry = new THREE.CylinderGeometry(1.2, 1.2, 0.1, 16);
        const topMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xA0522D,
            roughness: 0.7,
            metalness: 0.1
        });
        const top = new THREE.Mesh(topGeometry, topMaterial);
        top.position.y = 1.55;
        top.castShadow = true;
        top.receiveShadow = true;
        standGroup.add(top);
        
        // Position and rotate the stand
        standGroup.position.set(x, 0, z);
        standGroup.rotation.y = rotation;
        
        // Add to store scene
        this.storeScene.scene.add(standGroup);
        
        // Store reference
        this.displayStands[standId] = {
            mesh: standGroup,
            id: standId,
            x: x,
            z: z,
            occupied: false,
            productId: null
        };
        
        return standGroup;
    }
    
    // Load a 3D product model into the scene
    async loadProductModel(productId, modelPath, position, standId = null) {
        return new Promise((resolve, reject) => {
            // In a real implementation, we would load the actual 3D model
            // For now, we'll create a placeholder based on product data
            const productData = this.getProductData(productId);
            
            // Create a product mesh based on type
            let geometry, material;
            
            if (productData && productData.category) {
                // Different geometries based on product category
                switch(productData.category.toLowerCase()) {
                    case 'dresses':
                    case 'tops':
                    case 'shirts':
                        geometry = new THREE.ConeGeometry(0.5, 1.2, 8);
                        break;
                    case 'pants':
                    case 'jeans':
                        geometry = new THREE.CylinderGeometry(0.3, 0.5, 1.0, 8);
                        break;
                    case 'shoes':
                        geometry = new THREE.BoxGeometry(0.6, 0.4, 0.8);
                        break;
                    case 'jackets':
                    case 'outerwear':
                        geometry = new THREE.CapsuleGeometry(0.5, 0.8, 4, 8);
                        break;
                    default:
                        geometry = new THREE.SphereGeometry(0.6, 16, 16);
                }
            } else {
                geometry = new THREE.SphereGeometry(0.6, 16, 16);
            }
            
            // Create material with product-specific color
            const color = productData ? this.getCategoryColor(productData.category) : 
                         new THREE.Color(Math.random(), Math.random(), Math.random());
            material = new THREE.MeshStandardMaterial({ 
                color: color,
                roughness: 0.3,
                metalness: 0.7,
                transparent: true,
                opacity: 0.95
            });
            
            const productMesh = new THREE.Mesh(geometry, material);
            productMesh.position.copy(position);
            productMesh.castShadow = true;
            productMesh.userData = { 
                productId: productId, 
                type: 'product',
                originalY: position.y,
                originalMaterial: material.clone()
            };
            
            // Add subtle floating animation
            productMesh.userData.floatOffset = Math.random() * Math.PI * 2;
            productMesh.userData.floatSpeed = 0.5 + Math.random() * 0.5;
            
            // Add to store scene
            this.storeScene.scene.add(productMesh);
            
            // Store reference
            this.products[productId] = {
                mesh: productMesh,
                id: productId,
                data: productData,
                standId: standId
            };
            
            // If standId is provided, mark stand as occupied
            if (standId && this.displayStands[standId]) {
                this.displayStands[standId].occupied = true;
                this.displayStands[standId].productId = productId;
            }
            
            resolve(productMesh);
        });
    }
    
    // Get product data from Aetherstore Engine or mock data
    getProductData(productId) {
        // First, try to get from Aetherstore Engine
        if (window.aetherstoreEngine && window.aetherstoreEngine.products) {
            return window.aetherstoreEngine.products.find(p => p.id === productId);
        }
        
        // If not found, return mock data
        return {
            id: productId,
            name: `Product ${productId}`,
            description: 'Beautiful fashion item',
            price: (Math.random() * 500 + 50).toFixed(2),
            category: ['Dresses', 'Tops', 'Shoes', 'Jackets'][Math.floor(Math.random() * 4)],
            brand: 'Fashion Brand',
            sizes: ['S', 'M', 'L'],
            colors: ['Red', 'Blue', 'Green']
        };
    }
    
    // Get color based on product category
    getCategoryColor(category) {
        const colorMap = {
            'dresses': new THREE.Color(0xFF69B4), // Pink
            'tops': new THREE.Color(0x87CEEB),   // Sky Blue
            'shirts': new THREE.Color(0x98FB98), // Pale Green
            'pants': new THREE.Color(0xDDA0DD),  // Plum
            'jeans': new THREE.Color(0x4169E1), // Royal Blue
            'shoes': new THREE.Color(0x2F4F4F), // Dark Slate Gray
            'jackets': new THREE.Color(0x800000), // Maroon
            'outerwear': new THREE.Color(0x228B22) // Forest Green
        };
        
        return colorMap[category.toLowerCase()] || new THREE.Color(Math.random(), Math.random(), Math.random());
    }
    
    // Handle product click
    handleProductClick(productId) {
        console.log(`Product clicked: ${productId}`);
        
        // Trigger haptic feedback simulation
        this.simulateHapticFeedback();
        
        // Animate the product
        const product = this.products[productId];
        if (product && product.mesh) {
            this.animationController.animateSelection(product.mesh);
        }
        
        // Show product info in IWSDK UI panel
        this.showProductInfo(productId);
        
        // If Aetherstore Engine exists, trigger product click
        if (window.aetherstoreEngine) {
            window.aetherstoreEngine.handleProductClick(productId);
        }
    }
    
    // Simulate haptic feedback
    simulateHapticFeedback() {
        // In a real implementation, this would interface with IWSDK haptics
        console.log('Haptic feedback triggered');
        
        // Visual feedback
        document.body.style.animation = 'shake 0.5s';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 500);
    }
    
    // Show product info in UI panel
    showProductInfo(productId) {
        const product = this.products[productId];
        if (!product || !product.data) {
            console.error(`Product data not found for ID: ${productId}`);
            return;
        }
        
        const productData = product.data;
        const infoPanel = document.getElementById('product-info-panel');
        const titleElement = document.getElementById('product-title');
        const descElement = document.getElementById('product-description');
        const priceElement = document.getElementById('product-price');
        const tryButton = document.getElementById('try-now-btn');
        
        if (infoPanel && titleElement && descElement && priceElement && tryButton) {
            // Update content
            titleElement.textContent = productData.name;
            descElement.textContent = productData.description || 'Beautiful fashion item';
            priceElement.textContent = `$${productData.price}`;
            
            // Show panel
            infoPanel.classList.remove('iw-hidden');
            
            // Set up try button
            tryButton.onclick = () => {
                if (window.aetherstoreEngine) {
                    window.aetherstoreEngine.handleProductClick(productId);
                }
            };
        }
    }
    
    // Handle hover effect
    handleHover(intersects) {
        // This is handled by the interaction manager
    }
    
    // Update all product animations
    updateAnimations() {
        // Update floating animation for all products
        Object.values(this.products).forEach(product => {
            if (product.mesh) {
                this.animationController.animateFloating(product.mesh);
            }
        });
    }
    
    // Add a product to the scene
    addProduct(productId, position, standId = null) {
        return this.loadProductModel(productId, null, position, standId);
    }
    
    // Remove a product from the scene
    removeProduct(productId) {
        const product = this.products[productId];
        if (!product) return false;
        
        // Remove from scene
        this.storeScene.scene.remove(product.mesh);
        
        // If product was on a stand, mark stand as unoccupied
        if (product.standId && this.displayStands[product.standId]) {
            this.displayStands[product.standId].occupied = false;
            this.displayStands[product.standId].productId = null;
        }
        
        // Remove from internal storage
        delete this.products[productId];
        
        return true;
    }
    
    // Update a product in the scene
    updateProduct(productId, newProperties) {
        const product = this.products[productId];
        if (!product) return false;
        
        if (newProperties.position) {
            product.mesh.position.copy(newProperties.position);
        }
        if (newProperties.material) {
            product.mesh.material = newProperties.material;
        }
        if (newProperties.scale) {
            product.mesh.scale.copy(newProperties.scale);
        }
        if (newProperties.rotation) {
            product.mesh.rotation.copy(newProperties.rotation);
        }
        
        return true;
    }
    
    // Get all products
    getProducts() {
        return Object.values(this.products);
    }
    
    // Get product by ID
    getProduct(productId) {
        return this.products[productId];
    }
    
    // Get available stands
    getAvailableStands() {
        return Object.values(this.displayStands).filter(stand => !stand.occupied);
    }
    
    // Place product on a display stand
    placeProductOnStand(productId, standId) {
        const product = this.products[productId];
        const stand = this.displayStands[standId];
        
        if (!product || !stand || stand.occupied) {
            console.error('Cannot place product on stand:', { productExists: !!product, standExists: !!stand, standOccupied: stand?.occupied });
            return false;
        }
        
        // Position product on stand
        product.mesh.position.set(stand.x, 1.6, stand.z);
        
        // Mark stand as occupied
        stand.occupied = true;
        stand.productId = productId;
        product.standId = standId;
        
        return true;
    }
}

// Add shake animation for haptic feedback simulation
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0% { transform: translate(1px, 1px) rotate(0deg); }
    10% { transform: translate(-1px, -1px) rotate(-1deg); }
    20% { transform: translate(-3px, 0px) rotate(1deg); }
    30% { transform: translate(3px, 2px) rotate(0deg); }
    40% { transform: translate(1px, -1px) rotate(1deg); }
    50% { transform: translate(-1px, 2px) rotate(-1deg); }
    60% { transform: translate(-3px, 1px) rotate(0deg); }
    70% { transform: translate(3px, 1px) rotate(-1deg); }
    80% { transform: translate(-1px, -1px) rotate(1deg); }
    90% { transform: translate(1px, 2px) rotate(0deg); }
    100% { transform: translate(0px, 0px) rotate(0deg); }
  }
`;
document.head.appendChild(style);