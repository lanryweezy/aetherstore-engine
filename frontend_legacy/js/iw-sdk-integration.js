// iw-sdk-integration.js
// IWSDK Integration for Aetherstore Engine

class IWSDKIntegration {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.products = [];
        this.avatar = null;
        this.currentStore = null;
        this.iwSdkCore = null;
        this.iwSdkSystems = {};
        this.iwSdkModules = {};
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK Integration with real package...');
        
        try {
            if (!window.IWSDK || typeof window.IWSDK.initialize !== 'function') {
                throw new Error('IWSDK core not available');
            }
            // Initialize the real IWSDK
            const realIWSDKCore = await window.IWSDK.initialize({
                targetFPS: 90,
                maxPolyCount: 50000,
                textureResolution: '4k',
                renderQuality: 'high',
                enableShadows: true,
                enablePostProcessing: true,
                enablePhysics: true
            });
            
            this.iwSdkCore = realIWSDKCore;
            this.iwSdkSystems.xrInput = realIWSDKCore.getSystem('xrInput');
            this.iwSdkSystems.locomotion = realIWSDKCore.getSystem('locomotion');
            this.iwSdkSystems.grab = realIWSDKCore.getSystem('grab');
            this.iwSdkSystems.spatialAudio = realIWSDKCore.getSystem('spatialAudio');
            this.iwSdkSystems.sceneUnderstanding = realIWSDKCore.getSystem('sceneUnderstanding');
            this.iwSdkSystems.uiKitML = realIWSDKCore.getSystem('uiKitML');
            
            // Get IWSDK modules
            this.iwSdkModules.analytics = realIWSDKCore.getModule('analytics');
            this.iwSdkModules.accessibility = realIWSDKCore.getModule('accessibility');
            this.iwSdkModules.localization = realIWSDKCore.getModule('localization');
            this.iwSdkModules.performance = realIWSDKCore.getModule('performance');
            
            // Track initialization event
            if (this.iwSdkModules.analytics) {
                this.iwSdkModules.analytics.trackEvent('iw-sdk-initialization', {
                    timestamp: Date.now(),
                    targetFPS: 90,
                    maxPolyCount: 50000
                });
            }
            
            await this.setupIWScene();
            await this.setupIWInput();
            await this.setupIWLocomotion();
            await this.setupIWGrab();
            await this.setupIWSpatialAudio();
            await this.setupIWSceneUnderstanding();
            await this.setupIWUI();
            await this.setupIWAccessibility();
        } catch (error) {
            console.error('Failed to initialize real IWSDK, falling back to traditional 3D:', error);
            this.setupTraditional3D();
        }
    }
    
    async setupIWScene() {
        // Initialize IWSDK scene using Three.js
        const container = document.getElementById('iw3d-container');
        
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        this.scene.fog = new THREE.Fog(0xf0f0f0, 10, 20);
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 1.6, 5);
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        container.appendChild(this.renderer.domElement);
        
        // Add lighting
        this.addLighting();
        
        // Create store environment
        this.createStoreEnvironment();
        
        // Add event listeners for window resize
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // Start animation loop
        this.animate();
        
        console.log('IWSDK Scene initialized');
    }
    
    addLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        // Hemisphere light for more natural lighting
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        hemiLight.position.set(0, 20, 0);
        this.scene.add(hemiLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        
        // Configure shadow properties
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        
        this.scene.add(directionalLight);
    }
    
    createStoreEnvironment() {
        // Create floor with texture
        const floorGeometry = new THREE.PlaneGeometry(30, 30);
        const floorMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xaaaaaa,
            roughness: 0.9,
            metalness: 0.1
        });
        this.floor = new THREE.Mesh(floorGeometry, floorMaterial);
        this.floor.rotation.x = -Math.PI / 2;
        this.floor.receiveShadow = true;
        this.scene.add(this.floor);
        
        // Add grid helper to floor
        const gridHelper = new THREE.GridHelper(30, 30, 0x888888, 0x444444);
        gridHelper.position.y = 0.01;  // Slightly above floor to avoid z-fighting
        this.scene.add(gridHelper);
        
        // Create walls
        this.createWalls();
        
        // Add decorative elements
        this.addDecorativeElements();
        
        // Create product displays
        this.createProductDisplays();
    }
    
    createWalls() {
        const wallMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xdddddd,
            roughness: 0.7,
            metalness: 0.3
        });
        
        // Back wall
        const backWallGeometry = new THREE.BoxGeometry(30, 6, 0.2);
        this.backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
        this.backWall.position.set(0, 3, -15);
        this.backWall.castShadow = true;
        this.backWall.receiveShadow = true;
        this.scene.add(this.backWall);
        
        // Left wall
        const sideWallGeometry = new THREE.BoxGeometry(0.2, 6, 30);
        this.leftWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        this.leftWall.position.set(-15, 3, 0);
        this.leftWall.castShadow = true;
        this.leftWall.receiveShadow = true;
        this.scene.add(this.leftWall);
        
        // Right wall
        this.rightWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        this.rightWall.position.set(15, 3, 0);
        this.rightWall.castShadow = true;
        this.rightWall.receiveShadow = true;
        this.scene.add(this.rightWall);
    }
    
    addDecorativeElements() {
        // Add some decorative elements to make the store more interesting
        // Ceiling lights
        for (let i = -10; i <= 10; i += 5) {
            for (let j = -10; j <= 10; j += 5) {
                if (Math.abs(i) > 1 || Math.abs(j) > 1) { // Avoid center
                    const light = new THREE.PointLight(0xffffff, 0.5, 20);
                    light.position.set(i, 5, j);
                    this.scene.add(light);
                    
                    // Add light bulb visual
                    const bulbGeometry = new THREE.SphereGeometry(0.1, 16, 16);
                    const bulbMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00 });
                    const bulb = new THREE.Mesh(bulbGeometry, bulbMaterial);
                    bulb.position.copy(light.position);
                    this.scene.add(bulb);
                }
            }
        }
        
        // Add some plants or decorations
        this.createPlant(-12, 0, -5);
        this.createPlant(12, 0, -5);
    }
    
    createPlant(x, y, z) {
        // Simple plant representation
        const trunkGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1, 8);
        const trunkMaterial = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
        const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
        trunk.position.set(x, y + 0.5, z);
        trunk.castShadow = true;
        this.scene.add(trunk);
        
        const leavesGeometry = new THREE.SphereGeometry(0.5, 8, 8);
        const leavesMaterial = new THREE.MeshStandardMaterial({ color: 0x228B22 });
        const leaves = new THREE.Mesh(leavesGeometry, leavesMaterial);
        leaves.position.set(x, y + 1.2, z);
        leaves.castShadow = true;
        this.scene.add(leaves);
    }
    
    createProductDisplays() {
        // Create multiple product display stands
        const standPositions = [
            {x: -8, z: -8, rotation: 0},
            {x: 0, z: -10, rotation: Math.PI/2},
            {x: 8, z: -8, rotation: Math.PI},
            {x: -8, z: 0, rotation: 0},
            {x: 8, z: 0, rotation: Math.PI},
            {x: -8, z: 8, rotation: 0},
            {x: 0, z: 10, rotation: -Math.PI/2},
            {x: 8, z: 8, rotation: Math.PI}
        ];
        
        for (let i = 0; i < standPositions.length; i++) {
            const pos = standPositions[i];
            this.createDisplayStand(pos.x, pos.z, pos.rotation, i);
        }
    }
    
    createDisplayStand(x, z, rotation, id) {
        // Create a more detailed display stand
        const group = new THREE.Group();
        
        // Base
        const baseGeometry = new THREE.CylinderGeometry(1.2, 1.2, 0.2, 16);
        const baseMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x8B4513,
            roughness: 0.9,
            metalness: 0.1
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.1;
        base.castShadow = true;
        base.receiveShadow = true;
        group.add(base);
        
        // Stand
        const standGeometry = new THREE.CylinderGeometry(0.1, 0.1, 1.5, 8);
        const standMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x654321,
            roughness: 0.8,
            metalness: 0.2
        });
        const stand = new THREE.Mesh(standGeometry, standMaterial);
        stand.position.y = 0.95;
        stand.castShadow = true;
        group.add(stand);
        
        // Top display surface
        const topGeometry = new THREE.CylinderGeometry(1, 1, 0.1, 16);
        const topMaterial = new THREE.MeshStandardMaterial({ 
            color: 0xA0522D,
            roughness: 0.7,
            metalness: 0.1
        });
        const top = new THREE.Mesh(topGeometry, topMaterial);
        top.position.y = 1.55;
        top.castShadow = true;
        top.receiveShadow = true;
        group.add(top);
        
        // Position and rotate
        group.position.set(x, 0, z);
        group.rotation.y = rotation;
        
        // Add to scene
        this.scene.add(group);
        
        // Add a product placeholder on the stand
        this.createProductPlaceholder(x, 1.6, z, id);
    }
    
    createProductPlaceholder(x, y, z, standId) {
        // Create a capsule-shaped product placeholder
        const geometry = new THREE.CapsuleGeometry(0.4, 0.8, 4, 8);
        const material = new THREE.MeshStandardMaterial({ 
            color: new THREE.Color(Math.random(), Math.random(), Math.random()),
            roughness: 0.2,
            metalness: 0.7
        });
        
        const product = new THREE.Mesh(geometry, material);
        product.position.set(x, y, z);
        product.castShadow = true;
        product.userData = { id: `product_${standId}`, type: 'product', standId: standId, originalY: y };
        
        // Add subtle floating animation
        product.userData.floatOffset = Math.random() * Math.PI * 2;
        product.userData.floatSpeed = 0.5 + Math.random() * 0.5;
        
        // Make the product grabbable using IWSDK system
        if (this.iwSdkSystems.grab) {
            this.iwSdkSystems.grab.makeGrabbable(product, {
                id: `grab_${product.userData.id}`,
                oneHanded: true,
                twoHanded: false,
                distanceGrab: true
            });
        }
        
        this.scene.add(product);
        this.products.push(product);
    }
    
    addProductEventListeners() {
        // Add raycasting for product interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        // Set up mouse move and click events for interaction
        document.addEventListener('click', (event) => {
            // Calculate mouse position in normalized device coordinates
            this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
            
            // Update the picking ray with the camera and mouse position
            this.raycaster.setFromCamera(this.mouse, this.camera);
            
            // Calculate objects intersecting the picking ray
            const intersects = this.raycaster.intersectObjects(this.products);
            
            if (intersects.length > 0) {
                const product = intersects[0].object;
                this.handleProductClick(product.userData.id);
            }
        });
    }
    
    handleProductClick(productId) {
        console.log(`IWSDK Product clicked: ${productId}`);
        
        // Find product in the Aetherstore Engine
        if (window.aetherstoreEngine && window.aetherstoreEngine.products) {
            const product = window.aetherstoreEngine.products.find(p => p.id === productId);
            if (product) {
                // Update UI panel with product info
                document.getElementById('product-title').textContent = product.name;
                document.getElementById('product-description').textContent = product.description;
                document.getElementById('product-price').textContent = `${product.price}`;
                
                // Show product info panel
                document.getElementById('product-info-panel').classList.remove('iw-hidden');
                
                // Set up try button
                document.getElementById('try-now-btn').onclick = () => {
                    window.aetherstoreEngine.handleProductClick(productId);
                };
            }
        }
    }
    
    async setupIWInput() {
        // Initialize IWSDK input management
        try {
            if (this.iwSdkSystems.xrInput) {
                // Initialize the XR input manager
                await this.iwSdkSystems.xrInput.initialize();
                
                // Set up controller tracking
                this.iwSdkSystems.xrInput.on('controllerconnected', (event) => {
                    console.log('Controller connected:', event.data);
                    this.setupController(event.data);
                });
                
                this.iwSdkSystems.xrInput.on('controllerdisconnected', (event) => {
                    console.log('Controller disconnected:', event.data);
                });
                
                console.log('IWSDK Input management initialized');
            }
        } catch (error) {
            console.warn('IWSDK Input management not available:', error);
        }
    }
    
    setupController(controllerData) {
        // Create controller representation in the scene
        const controllerGeometry = new THREE.BufferGeometry().fromPoints([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, 0, -1)
        ]);
        const controllerLine = new THREE.Line(controllerGeometry, new THREE.LineBasicMaterial({ color: 0x00ff00 }));
        
        // Position based on actual controller data
        if (controllerData.position) {
            controllerLine.position.set(
                controllerData.position.x,
                controllerData.position.y,
                controllerData.position.z
            );
        }
        
        this.scene.add(controllerLine);
    }
    
    async setupIWLocomotion() {
        // Initialize IWSDK locomotion system
        try {
            if (this.iwSdkSystems.locomotion) {
                // Initialize the locomotion system
                this.iwSdkSystems.locomotion.initialize(this.scene, this.camera);
                
                console.log('IWSDK Locomotion system initialized');
            }
        } catch (error) {
            console.warn('IWSDK Locomotion system not available:', error);
        }
    }
    
    async setupIWGrab() {
        // Initialize IWSDK grab system
        try {
            if (this.iwSdkSystems.grab) {
                // Initialize the grab system
                this.iwSdkSystems.grab.initialize(this.camera, this.scene);
                
                console.log('IWSDK Grab system initialized');
            }
        } catch (error) {
            console.warn('IWSDK Grab system not available:', error);
        }
    }
    
    async setupIWSpatialAudio() {
        // Initialize IWSDK spatial audio system
        try {
            if (this.iwSdkSystems.spatialAudio) {
                // Initialize the spatial audio system
                this.iwSdkSystems.spatialAudio.initialize(this.camera);
                
                console.log('IWSDK Spatial Audio system initialized');
            }
        } catch (error) {
            console.warn('IWSDK Spatial Audio system not available:', error);
        }
    }
    
    async setupIWUI() {
        // Initialize IWSDK UI system
        try {
            // UIKitML would be used for spatial UI elements
            // This is a simplified implementation for now
            console.log('IWSDK UI system initialized');
            
            // Show interaction panel
            document.getElementById('interaction-panel').classList.remove('iw-hidden');
            
            // Add event listeners to UI elements
            document.querySelector('#social-shopping-btn').addEventListener('click', () => {
                if (window.aetherstoreEngine) {
                    window.aetherstoreEngine.startSocialShopping();
                }
            });
            
            document.querySelector('#vr-mode-btn').addEventListener('click', () => {
                if (window.aetherstoreEngine) {
                    window.aetherstoreEngine.enableVRMode();
                }
            });
            
            document.querySelector('#ai-stylist-btn').addEventListener('click', () => {
                if (window.aetherstoreEngine) {
                    window.aetherstoreEngine.openAIStylist();
                }
            });
            
        } catch (error) {
            console.warn('IWSDK UI system not available:', error);
        }
    }
    
    async setupIWSceneUnderstanding() {
        // Initialize IWSDK Scene Understanding if available
        try {
            if (this.iwSdkSystems.sceneUnderstanding) {
                const isSupported = await this.iwSdkSystems.sceneUnderstanding.initialize();
                
                if (isSupported) {
                    // Detect planes and meshes in the environment
                    const planes = this.iwSdkSystems.sceneUnderstanding.detectPlanes();
                    const meshes = this.iwSdkSystems.sceneUnderstanding.detectMeshes();
                    
                    console.log('IWSDK Scene Understanding detected:', { planes, meshes });
                    
                    // Use detected planes to adjust store layout if needed
                    planes.forEach(plane => {
                        if (plane.type === 'floor' && plane.confidence > 0.8) {
                            // Adjust floor position based on detected plane
                            this.floor.position.y = plane.position.y;
                        }
                    });
                }
                
                console.log('IWSDK Scene Understanding system initialized');
            }
        } catch (error) {
            console.warn('IWSDK Scene Understanding system not available:', error);
        }
    }
    
    async setupIWAccessibility() {
        // Initialize accessibility features
        try {
            if (this.iwSdkModules.accessibility) {
                await this.iwSdkModules.accessibility.initialize();
                
                // Apply accessibility settings from user preferences
                const accessibilityPrefs = window.aetherstoreSecurity.userPreferences.getPreference('accessibility');
                if (accessibilityPrefs) {
                    if (accessibilityPrefs.highContrast) {
                        this.iwSdkModules.accessibility.setHighContrast(true);
                    }
                    if (accessibilityPrefs.reducedMotion) {
                        this.iwSdkModules.accessibility.setReduceMotion(true);
                    }
                }
                
                console.log('IWSDK Accessibility features initialized');
            }
        } catch (error) {
            console.warn('IWSDK Accessibility module not available:', error);
        }
    }
    
    setupTraditional3D() {
        // Fallback to traditional 3D if IWSDK is not available
        console.log('Setting up traditional 3D fallback');
        
        // Reveal the A-Frame scene if IWSDK is not available
        const aframeScene = document.querySelector('#fashion-scene');
        if (aframeScene) {
            aframeScene.style.display = 'block';
        }
        
        // Hide IWSDK-specific elements
        document.getElementById('iw3d-container').style.display = 'none';
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const delta = 0.016; // assuming 60fps, adjust as needed
        
        // Update IWSDK systems
        if (this.iwSdkCore) {
            this.iwSdkCore.update(delta);
        }
        
        // Update performance module with current FPS
        if (this.iwSdkModules.performance) {
            const stats = this.iwSdkCore.getPerformanceStats();
            this.iwSdkModules.performance.adaptToPerformance(stats.fps);
        }
        
        if (this.iwSdkSystems.locomotion) {
            this.iwSdkSystems.locomotion.update(delta, this.camera);
        }
        
        if (this.iwSdkSystems.grab) {
            this.iwSdkSystems.grab.update();
        }
        
        if (this.iwSdkSystems.spatialAudio) {
            this.iwSdkSystems.spatialAudio.update(this.camera);
        }
        
        if (this.iwSdkSystems.sceneUnderstanding) {
            this.iwSdkSystems.sceneUnderstanding.update();
        }
        
        // Update floating animation for products
        const time = Date.now() * 0.001;
        
        for (const product of this.products) {
            if (product.userData && product.userData.originalY) {
                const floatOffset = product.userData.floatOffset || 0;
                const floatSpeed = product.userData.floatSpeed || 1;
                
                // Apply reduced motion setting if enabled
                if (this.iwSdkModules.accessibility?.reduceMotion) {
                    product.position.y = product.userData.originalY;
                } else {
                    product.position.y = product.userData.originalY + Math.sin(time * floatSpeed + floatOffset) * 0.1;
                }
                
                // Add subtle rotation
                product.rotation.y += 0.005;
            }
        }
        
        // Render the scene
        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize IWSDK integration when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.iwSdkIntegration = new IWSDKIntegration();
    }, 1000);
});