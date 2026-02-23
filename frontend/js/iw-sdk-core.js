// iw-sdk-core.js
// Mock IWSDK Core Implementation for Aetherstore Engine

// IWSDK Core Namespace
window.IWSDK = window.IWSDK || {};

// IWSDK Core System
IWSDK.Core = class {
    constructor() {
        this.initialized = false;
        this.config = null;
        this.systems = {};
        console.log('IWSDK Core initialized');
    }

    async initialize(config = {}) {
        this.config = {
            targetFPS: config.targetFPS || 90,
            maxPolyCount: config.maxPolyCount || 100000,
            textureResolution: config.textureResolution || '4k',
            renderQuality: config.renderQuality || 'high',
            ...config
        };

        // Initialize core systems
        this.systems.xrInput = new IWSDK.XRInputManager();
        this.systems.locomotion = new IWSDK.LocomotionSystem();
        this.systems.grab = new IWSDK.GrabSystem();
        this.systems.spatialAudio = new IWSDK.SpatialAudioSystem();

        this.initialized = true;
        console.log('IWSDK Core initialized with config:', this.config);
        return true;
    }

    isInitialized() {
        return this.initialized;
    }

    getSystem(systemName) {
        return this.systems[systemName];
    }

    update(deltaTime) {
        // Update all registered systems
        for (const system of Object.values(this.systems)) {
            if (system.update) {
                system.update(deltaTime);
            }
        }
    }
};

// IWSDK XR Input Manager
IWSDK.XRInputManager = class {
    constructor() {
        this.controllers = new Map();
        this.hands = new Map();
        this.events = new Map();
        this.inputSources = [];
        console.log('IWSDK XR Input Manager initialized');
    }

    async initialize() {
        // Check for WebXR support
        if (!navigator.xr) {
            console.warn('WebXR not supported, using fallback input methods');
            return false;
        }

        // Set up input event handling
        this.setupInputEventHandlers();
        return true;
    }

    setupInputEventHandlers() {
        // Set up event listeners for input
        this.addEventListener = (event, callback) => {
            if (!this.events.has(event)) {
                this.events.set(event, []);
            }
            this.events.get(event).push(callback);
        };

        // Simulate controller connection/disconnection
        this.simulateControllerConnection = (controllerId, position, orientation) => {
            const controller = {
                id: controllerId,
                connected: true,
                position: position || new THREE.Vector3(0, 0, 0),
                orientation: orientation || new THREE.Quaternion(),
                handedness: controllerId.includes('left') ? 'left' : 'right',
                inputSources: []
            };

            this.controllers.set(controllerId, controller);

            // Trigger connection event
            this.triggerEvent('controllerconnected', { data: controller });
            return controller;
        };

        this.simulateControllerDisconnection = (controllerId) => {
            const controller = this.controllers.get(controllerId);
            if (controller) {
                controller.connected = false;
                this.triggerEvent('controllerdisconnected', { data: controller });
                this.controllers.delete(controllerId);
            }
        };
    }

    triggerEvent(eventName, data) {
        const callbacks = this.events.get(eventName);
        if (callbacks) {
            for (const callback of callbacks) {
                callback(data);
            }
        }
    }

    on(event, callback) {
        this.addEventListener(event, callback);
    }

    update() {
        // Update controller and hand tracking data
        // In a real implementation, this would interface with actual XR input
    }
};

// IWSDK Locomotion System
IWSDK.LocomotionSystem = class {
    constructor() {
        this.movementModes = {
            SLIDE: 'slide',
            TELEPORT: 'teleport',
            WALK: 'walk'
        };
        this.currentMode = this.movementModes.SLIDE;
        this.config = {
            slideSpeed: 2.0,
            teleportRange: 10.0,
            turnSpeed: 2.0,
            vignettingEnabled: true,
            vignettingIntensity: 0.5
        };
        console.log('IWSDK Locomotion System initialized');
    }

    initialize(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.setupLocomotionControls();
        return true;
    }

    setupLocomotionControls() {
        // Set up locomotion controls based on movement mode
        this.setMovementMode(this.currentMode);
    }

    setMovementMode(mode) {
        this.currentMode = mode;
        switch(mode) {
            case this.movementModes.SLIDE:
                this.enableSlideLocomotion();
                break;
            case this.movementModes.TELEPORT:
                this.enableTeleportLocomotion();
                break;
            case this.movementModes.WALK:
                this.enableWalkLocomotion();
                break;
        }
        console.log(`Locomotion mode set to: ${mode}`);
    }

    enableSlideLocomotion() {
        // Implementation for slide locomotion
        this.slideControls = {
            moveForward: false,
            moveBackward: false,
            moveLeft: false,
            moveRight: false,
            velocity: new THREE.Vector3(),
            direction: new THREE.Vector3()
        };

        // Set up keyboard controls for demo purposes
        document.addEventListener('keydown', this.onKeyDown.bind(this), false);
        document.addEventListener('keyup', this.onKeyUp.bind(this), false);
    }

    enableTeleportLocomotion() {
        // Implementation for teleport locomotion
        console.log('Teleport locomotion enabled');
    }

    enableWalkLocomotion() {
        // Implementation for walk locomotion
        console.log('Walk locomotion enabled');
    }

    onKeyDown(event) {
        switch (event.code) {
            case 'ArrowUp':
            case 'KeyW':
                this.slideControls.moveForward = true;
                break;
            case 'ArrowLeft':
            case 'KeyA':
                this.slideControls.moveLeft = true;
                break;
            case 'ArrowDown':
            case 'KeyS':
                this.slideControls.moveBackward = true;
                break;
            case 'ArrowRight':
            case 'KeyD':
                this.slideControls.moveRight = true;
                break;
        }
    }

    onKeyUp(event) {
        switch (event.code) {
            case 'ArrowUp':
            case 'KeyW':
                this.slideControls.moveForward = false;
                break;
            case 'ArrowLeft':
            case 'KeyA':
                this.slideControls.moveLeft = false;
                break;
            case 'ArrowDown':
            case 'KeyS':
                this.slideControls.moveBackward = false;
                break;
            case 'ArrowRight':
            case 'KeyD':
                this.slideControls.moveRight = false;
                break;
        }
    }

    update(deltaTime, camera) {
        if (this.currentMode === this.movementModes.SLIDE && this.slideControls) {
            // Apply movement based on input
            this.slideControls.velocity.x -= this.slideControls.velocity.x * 10.0 * deltaTime;
            this.slideControls.velocity.z -= this.slideControls.velocity.z * 10.0 * deltaTime;

            this.slideControls.direction.z = Number(this.slideControls.moveForward) - Number(this.slideControls.moveBackward);
            this.slideControls.direction.x = Number(this.slideControls.moveRight) - Number(this.slideControls.moveLeft);
            this.slideControls.direction.normalize();

            if (this.slideControls.moveForward || this.slideControls.moveBackward) {
                this.slideControls.velocity.z -= this.slideControls.direction.z * this.config.slideSpeed * deltaTime;
            }
            if (this.slideControls.moveLeft || this.slideControls.moveRight) {
                this.slideControls.velocity.x -= this.slideControls.direction.x * this.config.slideSpeed * deltaTime;
            }

            // Apply movement to camera (in a real implementation, would be the player rig)
            if (camera) {
                camera.position.x += this.slideControls.velocity.x;
                camera.position.z += this.slideControls.velocity.z;
            }
        }
    }
};

// IWSDK Grab System
IWSDK.GrabSystem = class {
    constructor() {
        this.grabbableObjects = new Map();
        this.grabbedObjects = new Map();
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        console.log('IWSDK Grab System initialized');
    }

    initialize(camera, scene) {
        this.camera = camera;
        this.scene = scene;
        this.setupGrabControls();
        return true;
    }

    setupGrabControls() {
        // Set up grab controls using mouse for demo, would use XR controllers in real implementation
        document.addEventListener('mousedown', this.startGrab.bind(this), false);
        document.addEventListener('mouseup', this.endGrab.bind(this), false);
    }

    makeGrabbable(object3D, config = {}) {
        const objectId = config.id || `grab_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
        
        const grabbable = {
            id: objectId,
            object: object3D,
            config: {
                oneHanded: config.oneHanded !== false, // default true
                twoHanded: config.twoHanded || false,
                distanceGrab: config.distanceGrab || false,
                constraints: config.constraints || {}
            },
            originalParent: object3D.parent,
            originalPosition: object3D.position.clone(),
            originalRotation: object3D.rotation.clone()
        };

        this.grabbableObjects.set(objectId, grabbable);
        return objectId;
    }

    startGrab(event) {
        // Calculate mouse position in normalized device coordinates
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;

        // Update the picking ray with the camera and mouse position
        this.raycaster.setFromCamera(this.mouse, this.camera);

        // Calculate objects intersecting the picking ray
        const intersects = this.raycaster.intersectObjects(
            Array.from(this.grabbableObjects.values()).map(g => g.object)
        );

        if (intersects.length > 0) {
            const object = intersects[0].object;
            
            // Find the grabbable object
            for (const [id, grabbable] of this.grabbableObjects) {
                if (grabbable.object === object || grabbable.object.contains(object)) {
                    this.grabbedObjects.set(id, grabbable);
                    grabbable.object.userData.isGrabbed = true;
                    
                    // Move object to camera position for initial grab
                    const direction = new THREE.Vector3(0, 0, -1);
                    direction.unproject(this.camera);
                    const ray = new THREE.Ray(this.camera.position, direction.sub(this.camera.position).normalize());
                    const grabPoint = ray.at(2, new THREE.Vector3()); // 2 units in front of camera
                    
                    grabbable.object.position.copy(grabPoint);
                    
                    console.log(`Started grab on object: ${id}`);
                    break;
                }
            }
        }
    }

    endGrab() {
        // End all active grabs
        for (const [id, grabbable] of this.grabbedObjects) {
            grabbable.object.userData.isGrabbed = false;
            // In a real implementation, we might want to apply physics here
            console.log(`Ended grab on object: ${id}`);
        }
        this.grabbedObjects.clear();
    }

    update() {
        // Update grabbed objects positions based on camera/controller position
        for (const [id, grabbable] of this.grabbedObjects) {
            if (this.camera) {
                // Move grabbed object slightly in front of camera
                const direction = new THREE.Vector3(0, 0, -1);
                direction.unproject(this.camera);
                const ray = new THREE.Ray(this.camera.position, direction.sub(this.camera.position).normalize());
                const grabPoint = ray.at(2, new THREE.Vector3()); // 2 units in front of camera
                
                grabbable.object.position.copy(grabPoint);
            }
        }
    }
};

// IWSDK Spatial Audio System
IWSDK.SpatialAudioSystem = class {
    constructor() {
        this.audioSources = new Map();
        this.listener = null;
        this.context = null;
        console.log('IWSDK Spatial Audio System initialized');
    }

    initialize(camera) {
        try {
            this.context = new (window.AudioContext || window.webkitAudioContext)();
            this.listener = this.context.listener;
            
            // Set up listener to follow camera
            if (camera) {
                this.camera = camera;
            }
            
            return true;
        } catch (e) {
            console.error('Failed to initialize audio context:', e);
            return false;
        }
    }

    createAudioSource(audioElement, position = new THREE.Vector3(0, 0, 0)) {
        const sourceId = `audio_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
        
        // Create audio source
        const source = this.context.createMediaElementSource(audioElement);
        
        // Create 3D panner
        const panner = this.context.createPanner();
        panner.panningModel = 'HRTF';
        panner.distanceModel = 'inverse';
        panner.refDistance = 1;
        panner.maxDistance = 10000;
        panner.rolloffFactor = 1;
        panner.coneInnerAngle = 360;
        panner.coneOuterAngle = 0;
        panner.coneOuterGain = 0;
        
        // Set position
        panner.setPosition(position.x, position.y, position.z);
        
        // Connect nodes
        source.connect(panner);
        panner.connect(this.context.destination);
        
        const audioSource = {
            id: sourceId,
            element: audioElement,
            source: source,
            panner: panner,
            position: position
        };
        
        this.audioSources.set(sourceId, audioSource);
        return sourceId;
    }

    update(camera) {
        if (camera && this.listener) {
            // Update listener position based on camera
            this.listener.setPosition(camera.position.x, camera.position.y, camera.position.z);
            
            // In a real implementation, we'd also update listener orientation
            // based on camera rotation
        }
        
        // Update positions of all audio sources if needed
        for (const audioSource of this.audioSources.values()) {
            if (audioSource.position) {
                audioSource.panner.setPosition(
                    audioSource.position.x, 
                    audioSource.position.y, 
                    audioSource.position.z
                );
            }
        }
    }
};

// Initialize IWSDK when Three.js is available
document.addEventListener('DOMContentLoaded', () => {
    if (typeof THREE !== 'undefined') {
        window.IWSDK = window.IWSDK || {};
        
        // Create a global instance
        window.IWSDK.instance = new IWSDK.Core();
        
        console.log('IWSDK ready for use');
    } else {
        console.error('Three.js not loaded - IWSDK requires Three.js');
    }
});

console.log('IWSDK Core Module Loaded');