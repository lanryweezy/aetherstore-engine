class MiniMap {
    constructor() {
        this.mapElement = null;
        this.playerMarker = null;
        this.cameraRig = null;
        this.storeScale = 0.1; // Scale factor for the mini-map
        this.init();
    }

    init() {
        console.log('Initializing Mini-Map...');

        // Create map container
        this.mapElement = document.createElement('div');
        this.mapElement.id = 'mini-map';
        this.mapElement.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 150px;
            height: 150px;
            background-color: rgba(0, 0, 0, 0.7);
            border: 2px solid #4a90e2;
            border-radius: 50%;
            z-index: 1000;
            overflow: hidden;
            box-shadow: 0 0 15px rgba(74, 144, 226, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
        `;

        // Create player marker
        this.playerMarker = document.createElement('div');
        this.playerMarker.id = 'mini-map-player';
        this.playerMarker.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #ff3366;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 8px #ff3366;
            transition: all 0.1s ease-out;
        `;

        // Direction indicator
        const directionIndicator = document.createElement('div');
        directionIndicator.style.cssText = `
            position: absolute;
            top: -5px;
            left: 3px;
            width: 4px;
            height: 8px;
            background-color: #ffffff;
            border-radius: 2px;
        `;
        this.playerMarker.appendChild(directionIndicator);

        this.mapElement.appendChild(this.playerMarker);
        document.body.appendChild(this.mapElement);

        // Find camera rig after a short delay to ensure A-Frame/Babylon is loaded
        setTimeout(() => {
            this.cameraRig = document.getElementById('camera-rig') ||
                             document.querySelector('[camera]') ||
                             document.querySelector('.camera');

            if (this.cameraRig) {
                this.startTracking();
            } else {
                console.warn('MiniMap: Could not find camera element to track.');
                // For demo without A-Frame rig
                this.startMockTracking();
            }
        }, 1000);
    }

    startTracking() {
        // Update loop
        const updatePosition = () => {
            if (!this.cameraRig) return;

            let pos = { x: 0, z: 0 };
            let rot = 0;

            // Handle A-Frame
            if (this.cameraRig.getAttribute && this.cameraRig.getAttribute('position')) {
                const position = this.cameraRig.getAttribute('position');
                const rotation = this.cameraRig.getAttribute('rotation');
                pos.x = position.x;
                pos.z = position.z;
                rot = rotation ? rotation.y : 0;
            }
            // Handle raw Three.js / Babylon.js if exposed
            else if (this.cameraRig.position) {
                pos.x = this.cameraRig.position.x;
                pos.z = this.cameraRig.position.z;
                // Simplified rotation for raw objects
                if (this.cameraRig.rotation) rot = this.cameraRig.rotation.y * (180/Math.PI);
            }

            this.updateMarker(pos.x, pos.z, rot);
            requestAnimationFrame(updatePosition);
        };

        updatePosition();
    }

    startMockTracking() {
        // Just for demo purposes if no 3D scene is active
        document.addEventListener('keydown', (e) => {
            let currentLeft = parseFloat(this.playerMarker.style.left || '50');
            let currentTop = parseFloat(this.playerMarker.style.top || '50');

            const speed = 2;
            switch(e.key.toLowerCase()) {
                case 'w': currentTop -= speed; break;
                case 's': currentTop += speed; break;
                case 'a': currentLeft -= speed; break;
                case 'd': currentLeft += speed; break;
            }

            // Keep within bounds
            currentLeft = Math.max(10, Math.min(90, currentLeft));
            currentTop = Math.max(10, Math.min(90, currentTop));

            this.playerMarker.style.left = `${currentLeft}%`;
            this.playerMarker.style.top = `${currentTop}%`;
        });

        // Initial center
        this.playerMarker.style.left = '50%';
        this.playerMarker.style.top = '50%';
    }

    updateMarker(x, z, rotationY) {
        // Center of the map is 50%, 50%
        // Map 3D world coordinates to 2D map coordinates
        // Assuming map width/height represents approx 100 units in 3D space

        const mapX = 50 + (x * this.storeScale * 10);
        const mapY = 50 + (z * this.storeScale * 10); // Z maps to Y in 2D top-down

        // Constrain to map bounds (roughly 10% to 90% to stay inside the circle)
        const constrainedX = Math.max(10, Math.min(90, mapX));
        const constrainedY = Math.max(10, Math.min(90, mapY));

        this.playerMarker.style.left = `${constrainedX}%`;
        this.playerMarker.style.top = `${constrainedY}%`;

        // Rotate marker to match camera facing direction
        this.playerMarker.style.transform = `translate(-50%, -50%) rotate(${-rotationY}deg)`;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're likely in a 3D store view, not on admin dashboard
    if (!window.location.href.includes('/admin/')) {
        window.miniMap = new MiniMap();
    }
});
