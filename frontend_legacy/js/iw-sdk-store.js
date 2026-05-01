// iw-sdk-store.js
// IWSDK Implementation for Aetherstore Engine 3D Store

class IWSDKStore {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.avatar = null;
        this.currentStore = null;
        this.clock = new THREE.Clock();
        this.productDisplaySystem = null;
        this.iwSdkCore = null;
        this.iwSdkSystems = {};
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK 3D Store...');
        
        // Check for IWSDK availability
        if (typeof IWSDK !== 'undefined' && IWSDK.instance) {
            this.iwSdkCore = IWSDK.instance;
            this.iwSdkSystems.xrInput = IWSDK.instance.getSystem('xrInput');
            this.iwSdkSystems.locomotion = IWSDK.instance.getSystem('locomotion');
            this.iwSdkSystems.grab = IWSDK.instance.getSystem('grab');
            this.iwSdkSystems.spatialAudio = IWSDK.instance.getSystem('spatialAudio');
        }
        
        // Initialize Three.js scene
        this.setupScene();
        
        // Add lighting
        this.addLighting();
        
        // Create store environment
        this.createStoreEnvironment();
        
        // Initialize IWSDK systems
        await this.initIWSDKSystems();
        
        // Initialize product display system
        this.productDisplaySystem = new IWSDKProductDisplay(this);
        
        // Start animation loop
        this.animate();
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('IWSDK 3D Store initialized');
    }
    
    setupScene() {
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
        
        // Add renderer to container
        const container = document.getElementById('iw3d-container');
        if (container) {
            // Clear any existing content
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
            container.appendChild(this.renderer.domElement);
        }
        
        // Add event listeners for window resize
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
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
        this.directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        this.directionalLight.position.set(5, 10, 7);
        this.directionalLight.castShadow = true;
        
        // Configure shadow properties
        this.directionalLight.shadow.mapSize.width = 2048;
        this.directionalLight.shadow.mapSize.height = 2048;
        this.directionalLight.shadow.camera.near = 0.5;
        this.directionalLight.shadow.camera.far = 50;
        this.directionalLight.shadow.camera.left = -10;
        this.directionalLight.shadow.camera.right = 10;
        this.directionalLight.shadow.camera.top = 10;
        this.directionalLight.shadow.camera.bottom = -10;
        
        this.scene.add(this.directionalLight);
        
        // Add a helper for the light (for debugging)
        if (false) { // Set to true for debugging
            const helper = new THREE.DirectionalLightHelper(this.directionalLight, 5);
            this.scene.add(helper);
        }
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
        
        // Create product displays using the new system
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
        // Create multiple product display stands using the product display system
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
            this.productDisplaySystem.createDisplayStand(pos.x, pos.z, pos.rotation, `stand_${i}`);
        }
        
        // Add initial products to stands
        this.addInitialProducts();
    }
    
    addInitialProducts() {
        // Add some initial products to display stands
        const availableStands = this.productDisplaySystem.getAvailableStands();
        
        for (let i = 0; i < Math.min(availableStands.length, 5); i++) {
            const stand = availableStands[i];
            const productId = `prod_${i + 1}`;
            
            // Add product to the stand
            this.productDisplaySystem.addProduct(productId, new THREE.Vector3(stand.x, 1.6, stand.z), stand.id);
        }
    }
    
    async initIWSDKSystems() {
        // Initialize IWSDK locomotion system
        await this.setupLocomotion();
        
        // Initialize IWSDK grab system
        await this.setupGrabSystem();
        
        // Initialize IWSDK UI system
        this.setupUISystem();
        
        // Initialize IWSDK spatial audio
        await this.setupSpatialAudio();
        
        console.log('IWSDK systems initialized');
    }
    
    async setupLocomotion() {
        // Initialize IWSDK locomotion system
        try {
            if (this.iwSdkSystems.locomotion) {
                // Initialize the locomotion system
                this.iwSdkSystems.locomotion.initialize(this.scene, this.camera);
                
                console.log('IWSDK Locomotion system initialized');
            } else {
                // Fallback to basic controls
                console.warn('IWSDK Locomotion not available, using basic controls');
                this.controls = new THREE.PointerLockControls(this.camera, document.body);
            }
        } catch (error) {
            console.warn('IWSDK Locomotion system not available:', error);
        }
    }
    
    async setupGrabSystem() {
        // Initialize IWSDK grab system
        try {
            if (this.iwSdkSystems.grab) {
                // Initialize the grab system
                this.iwSdkSystems.grab.initialize(this.camera, this.scene);
                
                console.log('IWSDK Grab system initialized');
            } else {
                console.warn('IWSDK Grab not available');
            }
        } catch (error) {
            console.warn('IWSDK Grab system not available:', error);
        }
    }
    
    setupUISystem() {
        // Setting up IWSDK UI system
        // This involves creating UI elements that can be positioned in 3D space
        console.log('IWSDK UI system setup');
    }
    
    async setupSpatialAudio() {
        // Initialize IWSDK spatial audio system
        try {
            if (this.iwSdkSystems.spatialAudio) {
                // Initialize the spatial audio system
                this.iwSdkSystems.spatialAudio.initialize(this.camera);
                
                console.log('IWSDK Spatial Audio system initialized');
            } else {
                console.warn('IWSDK Spatial Audio not available');
            }
        } catch (error) {
            console.warn('IWSDK Spatial Audio system not available:', error);
        }
    }
    
    setupEventListeners() {
        // Set up additional event listeners
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix(); // Fixed method name
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        this.update();
        this.render();
    }
    
    update() {
        // Get delta time for frame-rate independent movement
        const delta = this.clock.getDelta();
        
        // Update IWSDK systems
        if (this.iwSdkCore) {
            this.iwSdkCore.update(delta);
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
        
        // Update product display animations
        if (this.productDisplaySystem) {
            this.productDisplaySystem.updateAnimations();
        }
    }
    
    render() {
        this.renderer.render(this.scene, this.camera);
    }
    
    // Public methods for integration with Aetherstore Engine
    addProduct(productData) {
        // Use the product display system to add a product
        if (this.productDisplaySystem) {
            // Find an available stand
            const availableStands = this.productDisplaySystem.getAvailableStands();
            const stand = availableStands.length > 0 ? availableStands[0] : null;
            
            const position = stand ? 
                new THREE.Vector3(stand.x, 1.6, stand.z) : 
                new THREE.Vector3(0, 1.6, -5); // default position
            
            return this.productDisplaySystem.addProduct(
                productData.id || `product_${Date.now()}`, 
                position,
                stand ? stand.id : null
            );
        }
    }
    
    removeProduct(productId) {
        // Use the product display system to remove a product
        if (this.productDisplaySystem) {
            return this.productDisplaySystem.removeProduct(productId);
        }
        return false;
    }
    
    updateProduct(productId, newProperties) {
        // Use the product display system to update a product
        if (this.productDisplaySystem) {
            return this.productDisplaySystem.updateProduct(productId, newProperties);
        }
        return false;
    }
}

// Initialize IWSDK Store when IWSDK is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for IWSDK to be fully loaded
    const checkIWSDK = setInterval(() => {
        if (typeof THREE !== 'undefined') {
            clearInterval(checkIWSDK);
            
            // Ensure product display system is loaded before initializing store
            const checkProductDisplaySystem = setInterval(() => {
                if (typeof IWSDKProductDisplay !== 'undefined') {
                    clearInterval(checkProductDisplaySystem);
                    window.iwSdkStore = new IWSDKStore();
                }
            }, 100);
        }
    }, 100);
});