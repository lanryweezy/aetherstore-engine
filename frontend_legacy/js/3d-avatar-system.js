// 3d-avatar-system.js
// Advanced 3D Avatar System with IWSDK Integration

class Avatar3DSystem {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.avatar = null;
        this.avatarModel = null;
        this.animationMixer = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.avatarParts = {
            head: null,
            body: null,
            arms: { left: null, right: null },
            legs: { left: null, right: null },
            clothing: []
        };
        
        this.avatarMeasurements = {
            height: 175, // cm
            weight: 70, // kg
            chest: 95, // cm
            waist: 80, // cm
            hips: 95 // cm
        };
        
        this.currentOutfit = [];
        this.isInitialized = false;
        
        this.init();
    }
    
    async init() {
        console.log('Initializing 3D Avatar System...');
        
        // Wait for Three.js and IWSDK to be available
        if (typeof THREE === 'undefined') {
            throw new Error('Three.js not loaded');
        }
        
        this.setupScene();
        await this.createAvatar();
        this.setupAnimation();
        this.setupInteraction();
        
        this.isInitialized = true;
        console.log('3D Avatar System initialized');
    }
    
    setupScene() {
        // Set up the 3D environment for avatar
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        this.scene.fog = new THREE.Fog(0xf0f0f0, 10, 20);
        
        // Camera for avatar view
        this.camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
        this.camera.position.set(0, 1.6, 2);
        
        // Renderer optimized for avatar
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(600, 600);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        
        // Add to DOM - create container if it doesn't exist
        let container = document.getElementById('avatar-preview-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'avatar-preview-container';
            container.style.position = 'absolute';
            container.style.top = '10px';
            container.style.right = '10px';
            container.style.width = '300px';
            container.style.height = '300px';
            container.style.zIndex = '1000';
            container.style.display = 'none';
            document.body.appendChild(container);
        }
        
        container.appendChild(this.renderer.domElement);
        
        // Lighting
        this.addAvatarLighting();
        
        // Add to IWSDK scene if available
        if (window.iwSdkIntegration?.scene) {
            window.iwSdkIntegration.scene.add(this.scene);
        }
    }
    
    addAvatarLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        // Key light
        const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        keyLight.position.set(2, 3, 2);
        keyLight.castShadow = true;
        this.scene.add(keyLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
        fillLight.position.set(-2, 1, -2);
        this.scene.add(fillLight);
        
        // Rim light
        const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
        rimLight.position.set(0, 2, -3);
        this.scene.add(rimLight);
    }
    
    async createAvatar() {
        // Create a procedural avatar based on measurements
        this.avatar = new THREE.Group();
        
        // Create avatar parts based on body measurements
        const bodyHeight = this.avatarMeasurements.height / 100; // Convert cm to meters
        const bodyWidth = this.avatarMeasurements.chest / 200; // Use chest for width
        const bodyDepth = this.avatarMeasurements.waist / 200; // Use waist for depth
        
        // Body
        const bodyGeometry = new THREE.BoxGeometry(
            Math.max(0.3, bodyWidth * 0.7),  // width
            bodyHeight * 0.6,               // height (torso)
            Math.max(0.2, bodyDepth * 0.5)  // depth
        );
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0xFDBCB4, // Default skin tone
            roughness: 0.7,
            metalness: 0.3
        });
        
        this.avatarParts.body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        this.avatarParts.body.position.y = bodyHeight * 0.3; // Position in the group
        this.avatarParts.body.castShadow = true;
        this.avatarParts.body.receiveShadow = true;
        this.avatar.add(this.avatarParts.body);
        
        // Head
        const headSize = bodyWidth * 0.8;
        const headGeometry = new THREE.SphereGeometry(headSize * 0.7, 16, 16);
        const headMaterial = new THREE.MeshStandardMaterial({
            color: 0xFDBCB4, // Skin tone
            roughness: 0.6,
            metalness: 0.2
        });
        
        this.avatarParts.head = new THREE.Mesh(headGeometry, headMaterial);
        this.avatarParts.head.position.y = bodyHeight * 0.6 + headSize * 0.7; // Above body
        this.avatarParts.head.castShadow = true;
        this.avatar.add(this.avatarParts.head);
        
        // Arms
        const armLength = bodyHeight * 0.4;
        const armGeometry = new THREE.CylinderGeometry(0.05, 0.05, armLength, 8);
        const armMaterial = new THREE.MeshStandardMaterial({
            color: 0xFDBCB4,
            roughness: 0.6,
            metalness: 0.2
        });
        
        // Left arm
        this.avatarParts.arms.left = new THREE.Mesh(armGeometry, armMaterial);
        this.avatarParts.arms.left.position.set(bodyWidth * 0.4, bodyHeight * 0.4, 0);
        this.avatarParts.arms.left.rotation.z = Math.PI / 2;
        this.avatarParts.arms.left.castShadow = true;
        this.avatar.add(this.avatarParts.arms.left);
        
        // Right arm
        this.avatarParts.arms.right = new THREE.Mesh(armGeometry, armMaterial);
        this.avatarParts.arms.right.position.set(-bodyWidth * 0.4, bodyHeight * 0.4, 0);
        this.avatarParts.arms.right.rotation.z = -Math.PI / 2;
        this.avatarParts.arms.right.castShadow = true;
        this.avatar.add(this.avatarParts.arms.right);
        
        // Legs
        const legLength = bodyHeight * 0.45;
        const legGeometry = new THREE.CylinderGeometry(0.08, 0.08, legLength, 8);
        const legMaterial = new THREE.MeshStandardMaterial({
            color: 0x87CEEB, // Light blue for pants
            roughness: 0.7,
            metalness: 0.3
        });
        
        // Left leg
        this.avatarParts.legs.left = new THREE.Mesh(legGeometry, legMaterial);
        this.avatarParts.legs.left.position.set(bodyWidth * 0.2, -legLength * 0.5, 0);
        this.avatarParts.legs.left.castShadow = true;
        this.avatar.add(this.avatarParts.legs.left);
        
        // Right leg
        this.avatarParts.legs.right = new THREE.Mesh(legGeometry, legMaterial);
        this.avatarParts.legs.right.position.set(-bodyWidth * 0.2, -legLength * 0.5, 0);
        this.avatarParts.legs.right.castShadow = true;
        this.avatar.add(this.avatarParts.legs.right);
        
        // Add to scene
        this.scene.add(this.avatar);
    }
    
    setupAnimation() {
        // Set up animation mixer for avatar
        this.animationMixer = new THREE.AnimationMixer(this.avatar);
        
        // Add basic animations
        this.setupBasicAnimations();
    }
    
    setupBasicAnimations() {
        // Create a simple idle animation
        const idleAction = {
            name: 'idle',
            duration: 3, // seconds
            execute: (delta) => {
                // Subtle breathing motion
                if (this.avatarParts.body) {
                    this.avatarParts.body.position.y = Math.sin(Date.now() * 0.002) * 0.01;
                }
            }
        };
        
        // Create a walking animation
        const walkAction = {
            name: 'walk',
            duration: 1, // seconds
            execute: (delta) => {
                const time = Date.now() * 0.005;
                
                // Simulate walking motion
                if (this.avatarParts.legs.left && this.avatarParts.legs.right) {
                    this.avatarParts.legs.left.rotation.x = Math.sin(time * 2) * 0.3;
                    this.avatarParts.legs.right.rotation.x = Math.sin(time * 2 + Math.PI) * 0.3;
                }
                
                if (this.avatarParts.arms.left && this.avatarParts.arms.right) {
                    this.avatarParts.arms.left.rotation.x = Math.sin(time * 2 + Math.PI) * 0.2;
                    this.avatarParts.arms.right.rotation.x = Math.sin(time * 2) * 0.2;
                }
            }
        };
        
        this.activeAnimations = [idleAction];
        this.currentAnimation = idleAction;
    }
    
    setupInteraction() {
        // Set up interaction with the avatar
        const container = document.getElementById('avatar-preview-container');
        if (!container) return;
        
        container.addEventListener('click', this.handleAvatarClick.bind(this), false);
        container.addEventListener('mousemove', this.handleMouseMove.bind(this), false);
    }
    
    handleMouseMove(event) {
        // Update mouse position for raycasting
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }
    
    handleAvatarClick(event) {
        // Raycast to detect which part of avatar was clicked
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.avatar.children);
        
        if (intersects.length > 0) {
            const clickedObject = intersects[0].object;
            
            // Find which body part was clicked
            for (const [partName, part] of Object.entries(this.avatarParts)) {
                if (part === clickedObject) {
                    console.log(`Avatar ${partName} was clicked`);
                    this.onAvatarPartClick(partName, part);
                    break;
                } else if (part && typeof part === 'object' && part.children) {
                    // Check if the clicked object is a child of a body part
                    if (part.children.includes(clickedObject)) {
                        console.log(`Avatar ${partName} was clicked`);
                        this.onAvatarPartClick(partName, part);
                        break;
                    }
                }
            }
        }
    }
    
    onAvatarPartClick(partName, part) {
        // Handle click on avatar part
        // In real implementation, this could trigger fitting of clothes
        console.log(`Avatar part clicked: ${partName}`);
        
        if (window.iwSdkCommerceAnalytics) {
            window.iwSdkCommerceAnalytics.trackEvent('avatar-part-click', {
                part: partName,
                timestamp: Date.now()
            });
        }
    }
    
    updateAvatarMeasurements(newMeasurements) {
        // Update avatar based on new measurements
        this.avatarMeasurements = { ...this.avatarMeasurements, ...newMeasurements };
        
        // Regenerate avatar parts based on new measurements
        this.updateAvatarGeometry();
    }
    
    updateAvatarGeometry() {
        // Update the avatar's geometry based on measurements
        if (!this.avatarParts.body) return;
        
        const bodyHeight = this.avatarMeasurements.height / 100;
        const bodyWidth = this.avatarMeasurements.chest / 200;
        const bodyDepth = this.avatarMeasurements.waist / 200;
        
        // Update body dimensions
        this.avatarParts.body.scale.set(
            Math.max(0.3, bodyWidth * 0.7),
            bodyHeight * 0.6,
            Math.max(0.2, bodyDepth * 0.5)
        );
        
        // Update head position
        if (this.avatarParts.head) {
            this.avatarParts.head.position.y = bodyHeight * 0.6 + bodyWidth * 0.7;
        }
        
        // Update arms
        if (this.avatarParts.arms.left) {
            this.avatarParts.arms.left.position.x = bodyWidth * 0.4;
        }
        if (this.avatarParts.arms.right) {
            this.avatarParts.arms.right.position.x = -bodyWidth * 0.4;
        }
        
        // Update legs
        if (this.avatarParts.legs.left) {
            this.avatarParts.legs.left.position.x = bodyWidth * 0.2;
        }
        if (this.avatarParts.legs.right) {
            this.avatarParts.legs.right.position.x = -bodyWidth * 0.2;
        }
    }
    
    async addClothingToAvatar(productId, clothingModel) {
        // Add clothing to avatar
        if (!productId || !clothingModel) {
            console.error('Invalid product ID or clothing model');
            return false;
        }
        
        // If IWSDK try-on system is available, use it
        if (window.iwSdkTryOnSystem && window.iwSdkIntegration?.currentStore) {
            try {
                const result = await window.iwSdkTryOnSystem.tryOnItemWithFeedback(
                    window.iwSdkIntegration.currentStore.userId || 'guest',
                    productId
                );
                
                if (result.success) {
                    // Add the clothing to avatar parts
                    this.avatarParts.clothing.push({
                        id: productId,
                        model: clothingModel,
                        addedAt: Date.now()
                    });
                    
                    console.log(`Added clothing ${productId} to avatar`);
                    return true;
                }
            } catch (error) {
                console.error('Error adding clothing to avatar:', error);
            }
        }
        
        // Fallback: add visual representation of clothing
        if (clothingModel) {
            this.avatar.add(clothingModel);
            this.avatarParts.clothing.push({
                id: productId,
                model: clothingModel,
                addedAt: Date.now()
            });
            
            console.log(`Added clothing ${productId} to avatar (fallback mode)`);
            return true;
        }
        
        return false;
    }
    
    removeClothingFromAvatar(productId) {
        // Remove clothing from avatar
        const index = this.avatarParts.clothing.findIndex(item => item.id === productId);
        if (index !== -1) {
            const clothingItem = this.avatarParts.clothing[index];
            
            // Remove from avatar scene
            this.avatar.remove(clothingItem.model);
            
            // Remove from clothing array
            this.avatarParts.clothing.splice(index, 1);
            
            console.log(`Removed clothing ${productId} from avatar`);
            return true;
        }
        
        return false;
    }
    
    getAvatarOutfit() {
        // Get current outfit on avatar
        return [...this.avatarParts.clothing];
    }
    
    setAnimation(animationName) {
        // Switch to a specific animation
        const animation = this.activeAnimations.find(anim => anim.name === animationName);
        if (animation) {
            this.currentAnimation = animation;
            console.log(`Switched to animation: ${animationName}`);
        }
    }
    
    animate() {
        // Animation loop for avatar
        requestAnimationFrame(() => this.animate());
        
        const delta = 0.016; // Assuming 60fps
        
        // Update animation mixer
        if (this.animationMixer) {
            this.animationMixer.update(delta);
        }
        
        // Execute current animation
        if (this.currentAnimation && this.currentAnimation.execute) {
            this.currentAnimation.execute(delta);
        }
        
        // Render the avatar scene
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    show() {
        // Show the avatar preview container
        const container = document.getElementById('avatar-preview-container');
        if (container) {
            container.style.display = 'block';
        }
        
        // Start animation loop
        this.animate();
    }
    
    hide() {
        // Hide the avatar preview container
        const container = document.getElementById('avatar-preview-container');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    // Integrate with AI Fashion Assistant
    async getStyledAvatar() {
        if (!window.aiFashionAssistant) {
            console.warn('AI Fashion Assistant not available');
            return this.avatar;
        }
        
        // Get outfit recommendations from AI
        const occasion = 'casual'; // Default occasion
        const outfit = await window.aiFashionAssistant.getOutfitRecommendations(occasion, 'mild');
        
        // Apply the outfit to the avatar
        if (outfit.top) {
            // In a real implementation, this would load the actual 3D model
            console.log('Applying outfit to avatar:', outfit);
        }
        
        return this.avatar;
    }
    
    // Update avatar based on user profile
    async updateWithUserProfile(userProfile) {
        if (userProfile?.measurements) {
            this.updateAvatarMeasurements(userProfile.measurements);
        }
        
        if (userProfile?.avatarPreferences) {
            this.updateAvatarAppearance(userProfile.avatarPreferences);
        }
    }
    
    updateAvatarAppearance(preferences) {
        // Update avatar appearance based on preferences
        if (preferences?.skinTone && this.avatarParts.body) {
            this.avatarParts.body.material.color = new THREE.Color(preferences.skinTone);
        }
        
        if (preferences?.hairColor && this.avatarParts.head) {
            // Add hair to head (simplified)
            const hairGeometry = new THREE.ConeGeometry(0.3, 0.3, 8);
            const hairMaterial = new THREE.MeshStandardMaterial({
                color: new THREE.Color(preferences.hairColor),
                roughness: 0.8,
                metalness: 0.2
            });
            
            const hair = new THREE.Mesh(hairGeometry, hairMaterial);
            hair.position.y = this.avatarParts.head.position.y + 0.35;
            hair.rotation.x = Math.PI;
            this.avatar.add(hair);
        }
    }
}

// Initialize the 3D Avatar System when IWSDK is ready
document.addEventListener('DOMContentLoaded', () => {
    const initAvatarSystem = () => {
        // Wait for Three.js and IWSDK to be loaded
        if (typeof THREE !== 'undefined') {
            window.avatar3DSystem = new Avatar3DSystem();
        } else {
            console.warn('Three.js not loaded, will retry avatar system initialization');
            setTimeout(initAvatarSystem, 500);
        }
    };
    
    setTimeout(initAvatarSystem, 2000); // Wait for other systems to initialize
    
    console.log('3D Avatar System Ready');
});