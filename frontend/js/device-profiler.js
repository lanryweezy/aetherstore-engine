/**
 * Device Profiler for Aetherstore Engine
 * Estimates the user's hardware capabilities and automatically adjusts
 * 3D rendering settings to guarantee stability and high framerates.
 */

class DeviceProfiler {
    constructor(engine, scene) {
        this.engine = engine;
        this.scene = scene;
        this.tier = 'high'; // 'low', 'medium', 'high'
    }

    /**
     * Profile the device and apply optimal settings immediately
     */
    applyOptimalSettings() {
        this.profileDevice();
        this.applySettings();
    }

    profileDevice() {
        let score = 0;

        // 1. Check for Mobile
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        if (!isMobile) score += 2;

        // 2. Check Logical Cores (Rough proxy for CPU power)
        if (navigator.hardwareConcurrency) {
            if (navigator.hardwareConcurrency >= 8) score += 3;
            else if (navigator.hardwareConcurrency >= 4) score += 1;
        }

        // 3. Check Device Memory (if supported)
        if (navigator.deviceMemory) {
            if (navigator.deviceMemory >= 8) score += 3;
            else if (navigator.deviceMemory >= 4) score += 1;
        }

        // Determine Tier
        if (score <= 2) {
            this.tier = 'low'; // Likely a budget mobile device
        } else if (score <= 5) {
            this.tier = 'medium'; // Standard laptop or high-end phone
        } else {
            this.tier = 'high'; // Gaming PC or high-end workstation
        }

        console.log(`Device Profiler evaluated hardware tier as: ${this.tier.toUpperCase()} (Score: ${score})`);
    }

    applySettings() {
        switch(this.tier) {
            case 'low':
                // Lower resolution (render at 50% native resolution, upscale via CSS)
                this.engine.setHardwareScalingLevel(2.0);

                // Disable post-processes
                if (this.scene.postProcessRenderPipelineManager) {
                    this.scene.postProcessRenderPipelineManager.detachCamerasFromRenderPipeline("default", this.scene.activeCamera);
                }

                // Lower environment reflection quality
                this.scene.environmentTexture.lodGenerationScale = 0.5;
                break;

            case 'medium':
                // Render at 75% resolution
                this.engine.setHardwareScalingLevel(1.33);
                break;

            case 'high':
                // Render at full native resolution (100%)
                this.engine.setHardwareScalingLevel(1.0);
                break;
        }
    }
}

if (typeof window !== 'undefined') {
    window.DeviceProfiler = DeviceProfiler;
}
