// iw-sdk-avatar.js
// IWSDK Avatar System for Aetherstore Engine

class IWSDKAvatarSystem {
    constructor(storeScene) {
        this.storeScene = storeScene;
        this.avatars = {};
        this.avatarLoader = null;
        this.animationMixer = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK Avatar System...');
        
        // Initialize avatar loader
        this.avatarLoader = new THREE.GLTFLoader();
        
        // Initialize animation mixer
        this.animationMixer = new THREE.AnimationMixer();
        
        // Register with store scene
        if (this.storeScene) {
            this.storeScene.avatarSystem = this;
        }
        
        console.log('IWSDK Avatar System initialized');
    }
    
    // Create a basic avatar from user measurements
    createAvatarFromMeasurements(userId, measurements, position = new THREE.Vector3(0, 0, -3)) {
        return new Promise((resolve, reject) => {
            // Create a simple avatar representation based on body measurements
            const avatarGroup = new THREE.Group();
            
            // Create body based on measurements
            const bodyHeight = (measurements.height || 170) / 100; // Convert cm to meters
            const bodyWidth = (measurements.chest || 90) / 200; // Use chest measurement for width
            const bodyDepth = (measurements.waist || 80) / 200; // Use waist measurement for depth
            
            // Create body using measurements
            const bodyGeometry = new THREE.BoxGeometry(
                Math.max(0.3, bodyWidth * 0.8),  // width
                bodyHeight * 0.8,                // height
                Math.max(0.2, bodyDepth * 0.6)   // depth
            );
            
            const bodyMaterial = new THREE.MeshStandardMaterial({
                color: 0x87CEEB, // Light blue for default skin tone
                roughness: 0.7,
                metalness: 0.3
            });
            
            const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
            body.position.y = bodyHeight * 0.4; // Position at bottom of geometry
            body.castShadow = true;
            body.receiveShadow = true;
            avatarGroup.add(body);
            
            // Create head based on measurements
            const headSize = bodyWidth * 0.8;
            const headGeometry = new THREE.SphereGeometry(headSize, 16, 16);
            const headMaterial = new THREE.MeshStandardMaterial({
                color: 0xFDBCB4, // Skin tone
                roughness: 0.6,
                metalness: 0.2
            });
            
            const head = new THREE.Mesh(headGeometry, headMaterial);
            head.position.y = bodyHeight * 0.8 + headSize; // Position above body
            head.castShadow = true;
            avatarGroup.add(head);
            
            // Create simple arms
            const armLength = bodyHeight * 0.4;
            const armGeometry = new THREE.CylinderGeometry(0.05, 0.05, armLength, 8);
            const armMaterial = new THREE.MeshStandardMaterial({
                color: 0xFDBCB4,
                roughness: 0.6,
                metalness: 0.2
            });
            
            // Left arm
            const leftArm = new THREE.Mesh(armGeometry, armMaterial);
            leftArm.position.set(bodyWidth * 0.5 + 0.05, bodyHeight * 0.6, 0);
            leftArm.rotation.z = Math.PI / 2;
            leftArm.castShadow = true;
            avatarGroup.add(leftArm);
            
            // Right arm
            const rightArm = new THREE.Mesh(armGeometry, armMaterial);
            rightArm.position.set(-bodyWidth * 0.5 - 0.05, bodyHeight * 0.6, 0);
            rightArm.rotation.z = -Math.PI / 2;
            rightArm.castShadow = true;
            avatarGroup.add(rightArm);
            
            // Create simple legs
            const legLength = bodyHeight * 0.4;
            const legGeometry = new THREE.CylinderGeometry(0.08, 0.08, legLength, 8);
            const legMaterial = new THREE.MeshStandardMaterial({
                color: 0x87CEEB,
                roughness: 0.7,
                metalness: 0.3
            });
            
            // Left leg
            const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
            leftLeg.position.set(bodyWidth * 0.2, -legLength * 0.5, 0);
            leftLeg.castShadow = true;
            avatarGroup.add(leftLeg);
            
            // Right leg
            const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
            rightLeg.position.set(-bodyWidth * 0.2, -legLength * 0.5, 0);
            rightLeg.castShadow = true;
            avatarGroup.add(rightLeg);
            
            // Position the avatar in the scene
            avatarGroup.position.copy(position);
            
            // Add to store scene
            this.storeScene.scene.add(avatarGroup);
            
            // Store avatar reference
            this.avatars[userId] = {
                mesh: avatarGroup,
                id: userId,
                measurements: measurements,
                wearing: [], // List of items currently worn
                body: body,
                head: head,
                leftArm: leftArm,
                rightArm: rightArm,
                leftLeg: leftLeg,
                rightLeg: rightLeg
            };
            
            resolve(avatarGroup);
        });
    }
    
    // Load a detailed avatar model from a file
    async loadAvatarModel(userId, modelPath, position = new THREE.Vector3(0, 0, -3)) {
        return new Promise((resolve, reject) => {
            this.avatarLoader.load(
                modelPath,
                (gltf) => {
                    const avatarModel = gltf.scene;
                    
                    // Scale the model appropriately
                    avatarModel.scale.set(0.01, 0.01, 0.01); // Common scale for FBX/GLTF models
                    
                    // Position the avatar in the scene
                    avatarModel.position.copy(position);
                    
                    // Add to store scene
                    this.storeScene.scene.add(avatarModel);
                    
                    // Store avatar reference
                    this.avatars[userId] = {
                        mesh: avatarModel,
                        id: userId,
                        model: gltf,
                        animations: gltf.animations,
                        mixer: new THREE.AnimationMixer(gltf.scene),
                        wearing: []
                    };
                    
                    resolve(avatarModel);
                },
                undefined, // onProgress callback
                (error) => {
                    console.error('Error loading avatar model:', error);
                    reject(error);
                }
            );
        });
    }
    
    // Update avatar position
    updateAvatarPosition(userId, position) {
        const avatar = this.avatars[userId];
        if (avatar) {
            avatar.mesh.position.copy(position);
            return true;
        }
        return false;
    }
    
    // Update avatar rotation
    updateAvatarRotation(userId, rotation) {
        const avatar = this.avatars[userId];
        if (avatar) {
            avatar.mesh.rotation.copy(rotation);
            return true;
        }
        return false;
    }
    
    // Make avatar wear an item
    async makeAvatarWear(userId, productId) {
        const avatar = this.avatars[userId];
        if (!avatar) {
            console.error(`Avatar not found for user: ${userId}`);
            return false;
        }
        
        // Get product details from the product display system
        if (!this.storeScene.productDisplaySystem) {
            console.error('Product display system not available');
            return false;
        }
        
        const product = this.storeScene.productDisplaySystem.getProduct(productId);
        if (!product) {
            console.error(`Product not found: ${productId}`);
            return false;
        }
        
        // In a real implementation, we would position the clothing item on the avatar
        // For now, we'll just track what the avatar is wearing
        if (!avatar.wearing.includes(productId)) {
            avatar.wearing.push(productId);
        }
        
        // In a real implementation, we'd add the 3D model of the clothing to the avatar mesh
        console.log(`Avatar ${userId} is now wearing product ${productId}`);
        return true;
    }
    
    // Make avatar remove an item
    removeAvatarItem(userId, productId) {
        const avatar = this.avatars[userId];
        if (!avatar) {
            console.error(`Avatar not found for user: ${userId}`);
            return false;
        }
        
        const index = avatar.wearing.indexOf(productId);
        if (index > -1) {
            avatar.wearing.splice(index, 1);
            console.log(`Avatar ${userId} removed product ${productId}`);
            return true;
        }
        
        return false;
    }
    
    // Get what an avatar is wearing
    getAvatarWearing(userId) {
        const avatar = this.avatars[userId];
        if (avatar) {
            return [...avatar.wearing]; // Return a copy
        }
        return [];
    }
    
    // Animate avatar
    animateAvatar(userId, animationName) {
        const avatar = this.avatars[userId];
        if (!avatar || !avatar.mixer || !avatar.model) {
            return false;
        }
        
        // Find the animation
        const animationAction = avatar.mixer.clipAction(animationName);
        if (animationAction) {
            animationAction.play();
            return true;
        }
        
        return false;
    }
    
    // Update animations
    updateAnimations(deltaTime) {
        Object.values(this.avatars).forEach(avatar => {
            if (avatar.mixer) {
                avatar.mixer.update(deltaTime);
            }
        });
    }
    
    // Update avatar pose based on user body tracking
    updateAvatarPose(userId, poseData) {
        const avatar = this.avatars[userId];
        if (!avatar || !poseData || !poseData.keypoints) {
            return false;
        }
        
        // Update avatar based on pose keypoints
        // This would map the 2D/3D pose data to the avatar's skeleton
        const keypoints = poseData.keypoints;
        
        // In a real implementation, we would update the avatar's joint positions
        // based on the pose data from body tracking
        
        // For example, updating the head position based on nose/keypoints
        if (avatar.head && keypoints.nose) {
            avatar.head.position.x = keypoints.nose.x;
            avatar.head.position.y = keypoints.nose.y + 1.5; // Adjust for avatar height
            avatar.head.position.z = keypoints.nose.z;
        }
        
        console.log(`Updated pose for avatar ${userId}`);
        return true;
    }
    
    // Remove an avatar from the scene
    removeAvatar(userId) {
        const avatar = this.avatars[userId];
        if (!avatar) return false;
        
        // Remove from scene
        this.storeScene.scene.remove(avatar.mesh);
        
        // Remove from internal storage
        delete this.avatars[userId];
        
        return true;
    }
    
    // Get avatar by user ID
    getAvatar(userId) {
        return this.avatars[userId];
    }
    
    // Get all avatars
    getAvatars() {
        return Object.values(this.avatars);
    }
    
    // Setup avatar interaction
    setupAvatarInteraction() {
        document.addEventListener('click', this.handleAvatarInteraction.bind(this), false);
    }
    
    // Handle avatar interaction (click)
    handleAvatarInteraction(event) {
        // Calculate mouse position in normalized device coordinates
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;
        
        // Update the picking ray with the camera and mouse position
        this.raycaster.setFromCamera(this.mouse, this.storeScene.camera);
        
        // Calculate objects intersecting the picking ray
        const intersects = this.raycaster.intersectObjects(
            Object.values(this.avatars).map(avatar => avatar.mesh)
        );
        
        if (intersects.length > 0) {
            const clickedAvatar = intersects[0].object;
            
            // Find which avatar was clicked
            for (const [userId, avatar] of Object.entries(this.avatars)) {
                if (avatar.mesh === clickedAvatar || avatar.mesh.children.includes(clickedAvatar)) {
                    console.log(`Avatar ${userId} clicked`);
                    this.onAvatarClick(userId);
                    break;
                }
            }
        }
    }
    
    // Handler for when an avatar is clicked
    onAvatarClick(userId) {
        console.log(`Avatar ${userId} was clicked`);
        
        // Trigger any necessary actions when avatar is clicked
        // For example, show avatar controls or options
    }
    
    // Update all avatars
    updateAllAvatars() {
        // In a real implementation, this would update all avatars with current data
        // from the backend or other sources
    }
}

// Initialize the avatar system when the store scene is ready
document.addEventListener('DOMContentLoaded', () => {
    const checkStoreScene = setInterval(() => {
        if (window.iwSdkStore && window.iwSdkStore.scene) {
            clearInterval(checkStoreScene);
            
            // Ensure Three.js is available
            if (typeof THREE !== 'undefined') {
                window.iwSdkAvatarSystem = new IWSDKAvatarSystem(window.iwSdkStore);
            }
        }
    }, 100);
});