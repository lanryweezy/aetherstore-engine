// iw-sdk-try-on.js
// IWSDK Try-On System with Physics for Aetherstore Engine

class IWSDKTryOnSystem {
    constructor(storeScene, avatarSystem, productDisplaySystem) {
        this.storeScene = storeScene;
        this.avatarSystem = avatarSystem;
        this.productDisplaySystem = productDisplaySystem;
        this.physicsWorld = null;
        this.clothSimulator = null;
        this.currentTryOnSession = null;
        this.fitAnalyzer = null;
        
        this.init();
    }
    
    async init() {
        console.log('Initializing IWSDK Try-On System...');
        
        // Initialize physics world (using Ammo.js or similar physics engine)
        await this.initPhysics();
        
        // Initialize cloth simulator
        this.initClothSimulator();
        
        // Initialize fit analyzer
        this.initFitAnalyzer();
        
        // Register with store scene
        if (this.storeScene) {
            this.storeScene.tryOnSystem = this;
        }
        
        console.log('IWSDK Try-On System initialized');
    }
    
    async initPhysics() {
        // Initialize physics world (simplified implementation)
        // In a real implementation, we would use Ammo.js or another physics engine
        this.physicsWorld = {
            gravity: new THREE.Vector3(0, -9.8, 0),
            objects: [],
            update: (deltaTime) => {
                // Update physics simulation
                this.updatePhysics(deltaTime);
            }
        };
        
        console.log('Physics world initialized');
    }
    
    initClothSimulator() {
        // Initialize cloth simulation system
        // This would simulate realistic cloth physics in a real implementation
        this.clothSimulator = {
            simulate: (clothObject, avatar, movement) => {
                // Simulate how the cloth behaves on the avatar based on movement
                this.simulateClothOnAvatar(clothObject, avatar, movement);
            },
            updateCloth: (clothObject, deltaTime) => {
                // Update the cloth physics
                this.updateClothPhysics(clothObject, deltaTime);
            }
        };
        
        console.log('Cloth simulator initialized');
    }
    
    initFitAnalyzer() {
        // Initialize system to analyze fit based on measurements
        this.fitAnalyzer = {
            analyzeFit: (productData, avatarMeasurements) => {
                return this.analyzeProductFit(productData, avatarMeasurements);
            },
            getFitRecommendations: (productData, avatarMeasurements) => {
                return this.getFitRecommendations(productData, avatarMeasurements);
            }
        };
        
        console.log('Fit analyzer initialized');
    }
    
    // Start a try-on session
    async startTryOnSession(userId, productId) {
        if (!this.avatarSystem || !this.productDisplaySystem) {
            console.error('Avatar system or product display system not available');
            return null;
        }
        
        // Get the avatar and product
        const avatar = this.avatarSystem.getAvatar(userId);
        const product = this.productDisplaySystem.getProduct(productId);
        
        if (!avatar) {
            console.error(`Avatar not found for user: ${userId}`);
            return null;
        }
        
        if (!product) {
            console.error(`Product not found: ${productId}`);
            return null;
        }
        
        // Create try-on session data
        this.currentTryOnSession = {
            userId: userId,
            productId: productId,
            avatar: avatar,
            product: product,
            startTime: Date.now(),
            isOn: false,
            fitScore: 0,
            clothObject: null
        };
        
        console.log(`Started try-on session for user ${userId} and product ${productId}`);
        
        // Analyze fit before trying on
        const fitResult = await this.analyzeFit(userId, productId);
        this.currentTryOnSession.fitScore = fitResult.score;
        
        return this.currentTryOnSession;
    }
    
    // Put an item on the avatar
    async putOnItem(userId, productId) {
        if (!this.currentTryOnSession || 
            this.currentTryOnSession.userId !== userId || 
            this.currentTryOnSession.productId !== productId) {
            await this.startTryOnSession(userId, productId);
        }
        
        const avatar = this.avatarSystem.getAvatar(userId);
        const product = this.productDisplaySystem.getProduct(productId);
        
        if (!avatar || !product) {
            console.error('Avatar or product not found for try-on');
            return false;
        }
        
        // Create the clothing item in 3D
        const clothingItem = await this.createClothingItem(product, avatar);
        
        if (clothingItem) {
            // Add to avatar's mesh
            avatar.mesh.add(clothingItem);
            
            // Track in avatar's wearing list
            await this.avatarSystem.makeAvatarWear(userId, productId);
            
            // Mark as on
            this.currentTryOnSession.isOn = true;
            this.currentTryOnSession.clothObject = clothingItem;
            
            // Apply physics to the clothing item
            this.applyPhysicsToClothing(clothingItem, avatar);
            
            console.log(`Put on item ${productId} for user ${userId}`);
            return true;
        }
        
        return false;
    }
    
    // Remove an item from the avatar
    removeItem(userId, productId) {
        const avatar = this.avatarSystem.getAvatar(userId);
        if (!avatar) {
            console.error(`Avatar not found for user: ${userId}`);
            return false;
        }
        
        // Remove from avatar's wearing list
        this.avatarSystem.removeAvatarItem(userId, productId);
        
        // Remove the clothing item from the avatar mesh
        // This requires tracking which meshes belong to which clothing items
        // In a real implementation, we would have a more sophisticated system
        
        if (this.currentTryOnSession && this.currentTryOnSession.clothObject) {
            avatar.mesh.remove(this.currentTryOnSession.clothObject);
            this.currentTryOnSession.isOn = false;
            this.currentTryOnSession.clothObject = null;
        }
        
        console.log(`Removed item ${productId} from user ${userId}`);
        return true;
    }
    
    // Create a 3D representation of the clothing item
    async createClothingItem(product, avatar) {
        return new Promise((resolve) => {
            // In a real implementation, this would create a detailed 3D model
            // that fits the avatar's body shape
            // For now, we'll create a simple representation based on category
            
            let clothingGeometry, clothingMaterial;
            
            if (product.data && product.data.category) {
                // Create geometry based on product category
                switch(product.data.category.toLowerCase()) {
                    case 'dresses':
                    case 'dresses':
                        // Create a dress-like shape
                        clothingGeometry = new THREE.ConeGeometry(0.5, 1.2, 8);
                        break;
                    case 'tops':
                    case 'shirts':
                        // Create a torso-like shape
                        clothingGeometry = new THREE.CylinderGeometry(0.4, 0.5, 0.8, 8);
                        break;
                    case 'pants':
                    case 'jeans':
                        // Create pants-like shape
                        const pantsGroup = new THREE.Group();
                        
                        // Two leg cylinders
                        const legGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.8, 8);
                        const leftLeg = new THREE.Mesh(legGeometry, new THREE.MeshStandardMaterial({
                            color: 0x0000ff,
                            roughness: 0.5,
                            metalness: 0.2
                        }));
                        leftLeg.position.set(0.15, -0.4, 0);
                        leftLeg.castShadow = true;
                        
                        const rightLeg = new THREE.Mesh(legGeometry, new THREE.MeshStandardMaterial({
                            color: 0x0000ff,
                            roughness: 0.5,
                            metalness: 0.2
                        }));
                        rightLeg.position.set(-0.15, -0.4, 0);
                        rightLeg.castShadow = true;
                        
                        pantsGroup.add(leftLeg);
                        pantsGroup.add(rightLeg);
                        
                        resolve(pantsGroup);
                        return;
                    case 'shoes':
                        // Create shoe-like shapes
                        const shoesGroup = new THREE.Group();
                        
                        const shoeGeometry = new THREE.BoxGeometry(0.3, 0.2, 0.6);
                        const leftShoe = new THREE.Mesh(shoeGeometry, new THREE.MeshStandardMaterial({
                            color: 0x2F4F4F,
                            roughness: 0.8,
                            metalness: 0.1
                        }));
                        leftShoe.position.set(0.2, -0.9, 0);
                        leftShoe.castShadow = true;
                        
                        const rightShoe = new THREE.Mesh(shoeGeometry, new THREE.MeshStandardMaterial({
                            color: 0x2F4F4F,
                            roughness: 0.8,
                            metalness: 0.1
                        }));
                        rightShoe.position.set(-0.2, -0.9, 0);
                        rightShoe.castShadow = true;
                        
                        shoesGroup.add(leftShoe);
                        shoesGroup.add(rightShoe);
                        
                        resolve(shoesGroup);
                        return;
                    case 'jackets':
                    case 'outerwear':
                        // Create a jacket-like shape
                        clothingGeometry = new THREE.CapsuleGeometry(0.5, 0.8, 4, 8);
                        break;
                    default:
                        clothingGeometry = new THREE.SphereGeometry(0.4, 16, 16);
                }
            } else {
                clothingGeometry = new THREE.SphereGeometry(0.4, 16, 16);
            }
            
            // Create material based on product details
            const color = product.data && product.data.colors 
                ? this.getProductColor(product.data.colors[0]) 
                : new THREE.Color(Math.random(), Math.random(), Math.random());
            
            clothingMaterial = new THREE.MeshStandardMaterial({
                color: color,
                roughness: 0.4,
                metalness: 0.1,
                transparent: true,
                opacity: 0.9
            });
            
            const clothingItem = new THREE.Mesh(clothingGeometry, clothingMaterial);
            clothingItem.castShadow = true;
            clothingItem.receiveShadow = true;
            
            // Position the clothing on the avatar based on type
            this.positionClothingOnAvatar(clothingItem, avatar, product);
            
            resolve(clothingItem);
        });
    }
    
    // Get color based on product color description
    getProductColor(colorName) {
        const colorMap = {
            'red': new THREE.Color(0xFF0000),
            'blue': new THREE.Color(0x0000FF),
            'green': new THREE.Color(0x00FF00),
            'black': new THREE.Color(0x000000),
            'white': new THREE.Color(0xFFFFFF),
            'yellow': new THREE.Color(0xFFFF00),
            'purple': new THREE.Color(0x800080),
            'pink': new THREE.Color(0xFFC0CB),
            'orange': new THREE.Color(0xFFA500),
            'brown': new THREE.Color(0xA52A2A),
            'gray': new THREE.Color(0x808080),
            'silver': new THREE.Color(0xC0C0C0),
            'gold': new THREE.Color(0xFFD700)
        };
        
        return colorMap[colorName.toLowerCase()] || new THREE.Color(Math.random(), Math.random(), Math.random());
    }
    
    // Position clothing on avatar based on type
    positionClothingOnAvatar(clothingItem, avatar, product) {
        if (!avatar.body) return;
        
        const bodyPos = avatar.body.position;
        const bodySize = avatar.body.geometry.parameters;
        
        if (product.data && product.data.category) {
            switch(product.data.category.toLowerCase()) {
                case 'dresses':
                    clothingItem.position.set(bodyPos.x, bodyPos.y + bodySize.height/2, bodyPos.z);
                    clothingItem.scale.set(1.1, 1.1, 1.1);
                    break;
                case 'tops':
                case 'shirts':
                    clothingItem.position.set(bodyPos.x, bodyPos.y + bodySize.height/3, bodyPos.z);
                    clothingItem.scale.set(1.05, 0.9, 1.05);
                    break;
                case 'jackets':
                case 'outerwear':
                    clothingItem.position.set(bodyPos.x, bodyPos.y + bodySize.height/2, bodyPos.z);
                    clothingItem.scale.set(1.15, 1.0, 1.15);
                    break;
                default:
                    clothingItem.position.set(bodyPos.x, bodyPos.y + bodySize.height/2, bodyPos.z);
                    break;
            }
        } else {
            clothingItem.position.set(bodyPos.x, bodyPos.y + bodySize.height/2, bodyPos.z);
        }
    }
    
    // Apply physics simulation to clothing
    applyPhysicsToClothing(clothingItem, avatar) {
        // In a real implementation with physics engine, we would:
        // - Set the clothing item as a cloth or soft body
        // - Constrain it to the avatar's body/skeleton
        // - Apply gravity, wind, and movement forces
        // For now, we'll just simulate simple hanging physics
        
        // Add a simple "gravity" effect to make clothing hang naturally
        if (clothingItem.children.length > 0) {
            // For complex clothing items with multiple parts
            clothingItem.children.forEach(part => {
                this.applySimpleClothPhysics(part);
            });
        } else {
            this.applySimpleClothPhysics(clothingItem);
        }
    }
    
    // Apply simple physics to a clothing part
    applySimpleClothPhysics(clothingPart) {
        // In a real implementation, this would connect to a physics engine
        // For now, just record that this item should have physics applied
        clothingPart.userData.hasPhysics = true;
        clothingPart.userData.originalPosition = clothingPart.position.clone();
    }
    
    // Analyze how well a product fits an avatar
    async analyzeFit(userId, productId) {
        const avatar = this.avatarSystem.getAvatar(userId);
        const product = this.productDisplaySystem.getProduct(productId);
        
        if (!avatar || !product || !product.data) {
            console.error('Cannot analyze fit: avatar or product not found');
            return { score: 0, recommendations: [] };
        }
        
        // Perform fit analysis based on measurements
        const fitAnalysis = this.fitAnalyzer.analyzeFit(product.data, avatar.measurements);
        
        console.log(`Fit analysis for user ${userId} and product ${productId}:`, fitAnalysis);
        
        return fitAnalysis;
    }
    
    // Analyze product fit based on measurements
    analyzeProductFit(productData, avatarMeasurements) {
        // Calculate fit score based on size and measurements
        let fitScore = 0.5; // Base score
        
        if (avatarMeasurements && productData.size_chart) {
            // Compare avatar measurements with product size chart
            const chestDiff = Math.abs((avatarMeasurements.chest || 90) - 
                                     (productData.size_chart.chest || 90));
            const waistDiff = Math.abs((avatarMeasurements.waist || 70) - 
                                     (productData.size_chart.waist || 70));
            
            // Calculate fit score based on measurement differences
            const maxDiff = Math.max(chestDiff, waistDiff);
            
            // Lower difference = better fit (scale to 0-1)
            fitScore = Math.max(0, Math.min(1, (20 - maxDiff) / 20));
        }
        
        // Get size recommendations
        const sizeRecommendations = this.fitAnalyzer.getFitRecommendations(productData, avatarMeasurements);
        
        return {
            score: fitScore,
            confidence: 0.8, // Base confidence
            sizeRecommendations: sizeRecommendations,
            measurementDifferences: {
                chest: Math.abs((avatarMeasurements?.chest || 90) - (productData.size_chart?.chest || 90)),
                waist: Math.abs((avatarMeasurements?.waist || 70) - (productData.size_chart?.waist || 70)),
                hips: Math.abs((avatarMeasurements?.hips || 95) - (productData.size_chart?.hips || 95))
            }
        };
    }
    
    // Get size recommendations based on fit analysis
    getFitRecommendations(productData, avatarMeasurements) {
        if (!productData.size_chart || !avatarMeasurements) {
            return { recommendedSize: "M", alternatives: [] };
        }
        
        // Determine which size best fits based on measurements
        const sizes = Object.keys(productData.size_chart);
        if (sizes.length === 0) {
            return { recommendedSize: "M", alternatives: [] };
        }
        
        // Find the size that best matches the avatar's measurements
        let bestSize = sizes[0];
        let bestScore = Infinity;
        
        for (const size of sizes) {
            const sizeData = productData.size_chart[size];
            if (!sizeData) continue;
            
            // Calculate difference score for this size
            const chestDiff = Math.abs((avatarMeasurements.chest || 90) - (sizeData.chest || 90));
            const waistDiff = Math.abs((avatarMeasurements.waist || 70) - (sizeData.waist || 70));
            const hipDiff = Math.abs((avatarMeasurements.hips || 95) - (sizeData.hips || 95));
            
            const totalDiff = chestDiff + waistDiff + hipDiff;
            
            if (totalDiff < bestScore) {
                bestScore = totalDiff;
                bestSize = size;
            }
        }
        
        // Find alternative sizes (within acceptable range)
        const alternatives = sizes
            .filter(size => size !== bestSize)
            .map(size => {
                const sizeData = productData.size_chart[size];
                const chestDiff = Math.abs((avatarMeasurements.chest || 90) - (sizeData.chest || 90));
                const waistDiff = Math.abs((avatarMeasurements.waist || 70) - (sizeData.waist || 70));
                const hipDiff = Math.abs((avatarMeasurements.hips || 95) - (sizeData.hips || 95));
                const totalDiff = chestDiff + waistDiff + hipDiff;
                
                return { size, diff: totalDiff };
            })
            .sort((a, b) => a.diff - b.diff)
            .slice(0, 2)
            .map(item => item.size);
        
        return {
            recommendedSize: bestSize,
            alternatives: alternatives
        };
    }
    
    // Simulate cloth on avatar based on movement
    simulateClothOnAvatar(clothObject, avatar, movement) {
        // In a real implementation, this would simulate how the cloth moves
        // based on the avatar's body movements
        // For now, we'll just simulate a simple movement effect
        
        if (clothObject.userData.hasPhysics) {
            // Apply movement to the cloth based on avatar movement
            // This is a simplified simulation
            if (movement && movement.velocity) {
                // Add a slight movement to the cloth based on avatar velocity
                clothObject.position.y -= movement.velocity.y * 0.01;
                clothObject.position.x -= movement.velocity.x * 0.005;
            }
        }
    }
    
    // Update cloth physics
    updateClothPhysics(clothObject, deltaTime) {
        // Update the position of cloth elements based on physics
        if (clothObject.userData.hasPhysics) {
            // Apply simple physics: gravity and slight movement
            clothObject.position.y -= 0.1 * deltaTime;
            
            // Reset if it falls too far
            if (clothObject.position.y < -10) {
                if (clothObject.userData.originalPosition) {
                    clothObject.position.copy(clothObject.userData.originalPosition);
                }
            }
        }
    }
    
    // Update physics simulation
    updatePhysics(deltaTime) {
        // Update all physics objects
        // In a real implementation with Ammo.js, we would step the physics world
        // For now, we'll update any cloth physics
        if (this.currentTryOnSession && this.currentTryOnSession.clothObject) {
            this.clothSimulator.updateCloth(this.currentTryOnSession.clothObject, deltaTime);
        }
    }
    
    // Get current try-on session
    getCurrentSession() {
        return this.currentTryOnSession;
    }
    
    // End current try-on session
    endTryOnSession() {
        if (this.currentTryOnSession) {
            // Remove clothing from avatar if still wearing
            if (this.currentTryOnSession.isOn) {
                this.removeItem(
                    this.currentTryOnSession.userId, 
                    this.currentTryOnSession.productId
                );
            }
            
            this.currentTryOnSession = null;
            console.log('Ended try-on session');
        }
    }
    
    // Update the try-on system
    update(deltaTime) {
        // Update physics simulation
        this.physicsWorld.update(deltaTime);
        
        // Update cloth simulation
        if (this.currentTryOnSession && this.currentTryOnSession.clothObject && this.avatarSystem) {
            const avatar = this.avatarSystem.getAvatar(this.currentTryOnSession.userId);
            if (avatar) {
                // In a real implementation, we would pass actual movement data
                this.clothSimulator.simulate(this.currentTryOnSession.clothObject, avatar, {});
            }
        }
    }
    
    // Try on an item and get feedback
    async tryOnItemWithFeedback(userId, productId) {
        // Start the try-on session
        const session = await this.startTryOnSession(userId, productId);
        if (!session) {
            return { success: false, message: "Could not start try-on session" };
        }
        
        // Put the item on the avatar
        const success = await this.putOnItem(userId, productId);
        if (!success) {
            return { success: false, message: "Could not put on item" };
        }
        
        // Get fit analysis
        const fitAnalysis = await this.analyzeFit(userId, productId);
        
        return {
            success: true,
            message: "Item successfully put on avatar",
            fitAnalysis: fitAnalysis,
            session: session
        };
    }
}

// Initialize the try-on system when other systems are ready
document.addEventListener('DOMContentLoaded', () => {
    const checkSystems = setInterval(() => {
        if (window.iwSdkStore && window.iwSdkStore.avatarSystem && window.iwSdkStore.productDisplaySystem) {
            clearInterval(checkSystems);
            
            // Ensure Three.js is available
            if (typeof THREE !== 'undefined') {
                window.iwSdkTryOnSystem = new IWSDKTryOnSystem(
                    window.iwSdkStore,
                    window.iwSdkStore.avatarSystem,
                    window.iwSdkStore.productDisplaySystem
                );
            }
        }
    }, 100);
});