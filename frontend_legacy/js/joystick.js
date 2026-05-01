class VirtualJoystick {
    constructor(cameraRigId = 'camera-rig') {
        this.cameraRig = document.getElementById(cameraRigId) || document.querySelector('[camera]') || document.querySelector('.camera');

        this.joystickContainer = null;
        this.joystickKnob = null;

        this.active = false;
        this.center = { x: 0, y: 0 };
        this.current = { x: 0, y: 0 };
        this.maxRadius = 50;
        this.moveSpeed = 0.15;

        // Only initialize on mobile devices
        if (this.isMobile()) {
            this.init();
        }
    }

    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
    }

    init() {
        console.log('Initializing Virtual Joystick...');

        // Create container
        this.joystickContainer = document.createElement('div');
        this.joystickContainer.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 100px;
            height: 100px;
            background-color: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            z-index: 1000;
            display: flex;
            justify-content: center;
            align-items: center;
            touch-action: none;
            user-select: none;
        `;

        // Create knob
        this.joystickKnob = document.createElement('div');
        this.joystickKnob.style.cssText = `
            width: 40px;
            height: 40px;
            background-color: rgba(78, 205, 196, 0.8);
            border-radius: 50%;
            position: absolute;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            transition: transform 0.1s ease-out;
            pointer-events: none;
        `;

        this.joystickContainer.appendChild(this.joystickKnob);
        document.body.appendChild(this.joystickContainer);

        this.setupEvents();
        this.startUpdateLoop();
    }

    setupEvents() {
        this.joystickContainer.addEventListener('touchstart', this.handleStart.bind(this), {passive: false});
        this.joystickContainer.addEventListener('touchmove', this.handleMove.bind(this), {passive: false});
        this.joystickContainer.addEventListener('touchend', this.handleEnd.bind(this));

        // Mouse fallback for testing
        this.joystickContainer.addEventListener('mousedown', (e) => {
            this.active = true;
            this.handleStart({ touches: [{ clientX: e.clientX, clientY: e.clientY }] });
        });
        document.addEventListener('mousemove', (e) => {
            if (!this.active) return;
            this.handleMove({ touches: [{ clientX: e.clientX, clientY: e.clientY }] });
        });
        document.addEventListener('mouseup', () => {
            if (this.active) this.handleEnd();
        });
    }

    handleStart(e) {
        if (e.preventDefault) e.preventDefault();
        this.active = true;

        const rect = this.joystickContainer.getBoundingClientRect();
        this.center = {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2
        };

        this.updateKnob(e.touches[0].clientX, e.touches[0].clientY);
    }

    handleMove(e) {
        if (!this.active) return;
        if (e.preventDefault) e.preventDefault();

        this.updateKnob(e.touches[0].clientX, e.touches[0].clientY);
    }

    handleEnd() {
        this.active = false;
        this.current = { x: 0, y: 0 };
        this.joystickKnob.style.transform = `translate(0px, 0px)`;
    }

    updateKnob(clientX, clientY) {
        let deltaX = clientX - this.center.x;
        let deltaY = clientY - this.center.y;

        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

        if (distance > this.maxRadius) {
            const ratio = this.maxRadius / distance;
            deltaX *= ratio;
            deltaY *= ratio;
        }

        this.current = {
            x: deltaX / this.maxRadius, // Normalize -1 to 1
            y: deltaY / this.maxRadius
        };

        this.joystickKnob.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
    }

    startUpdateLoop() {
        const update = () => {
            if (this.active && this.cameraRig && (this.current.x !== 0 || this.current.y !== 0)) {
                // Determine rotation/direction based on A-Frame or Babylon/Three
                let moveX = this.current.x * this.moveSpeed;
                let moveZ = this.current.y * this.moveSpeed;

                if (this.cameraRig.getAttribute && this.cameraRig.getAttribute('position')) {
                    // A-Frame
                    const pos = this.cameraRig.getAttribute('position');
                    // Simplified rotation assumption, ideally factor in camera's Y rotation
                    pos.x += moveX;
                    pos.z += moveZ;
                    this.cameraRig.setAttribute('position', pos);
                } else if (this.cameraRig.position) {
                    // Raw 3D Engine
                    this.cameraRig.position.x += moveX;
                    this.cameraRig.position.z += moveZ;
                }
            }

            requestAnimationFrame(update);
        };

        update();
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    // We only want this in the main store view
    if (!window.location.href.includes('/admin/')) {
        setTimeout(() => {
            window.virtualJoystick = new VirtualJoystick();
        }, 1000);
    }
});
