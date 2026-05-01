/**
 * AutoLODSystem
 * Automatically generates Levels of Detail (LOD) for complex 3D meshes to ensure
 * high frame rates (60+ FPS) when rendering large, crowded virtual stores.
 */

class AutoLODSystem {
    constructor(scene) {
        this.scene = scene;
        this.optimizationActive = false;
    }

    /**
     * Applies automatic LOD generation to a newly loaded mesh hierarchy.
     * @param {BABYLON.Mesh} rootMesh - The root node/mesh of the loaded product.
     */
    applyAutoLOD(rootMesh) {
        // Iterate through all child meshes in the hierarchy
        const meshes = rootMesh.getChildMeshes ? rootMesh.getChildMeshes() : [rootMesh];

        meshes.forEach(mesh => {
            // Only apply LOD to reasonably complex meshes (e.g. > 2000 vertices)
            if (mesh.getTotalVertices() > 2000) {
                this.generateLODLevels(mesh);
            }
        });
    }

    /**
     * Generates decimated versions of the mesh for different viewing distances.
     * @param {BABYLON.Mesh} mesh - The target mesh.
     */
    generateLODLevels(mesh) {
        // We use Quadratic Error Decimation which is built into Babylon.js
        console.log(`Generating LODs for: ${mesh.name} (${mesh.getTotalVertices()} vertices)`);

        try {
            // Apply simplification configurations in a single array
            mesh.simplify(
                [
                    { quality: 0.5, distance: 15, optimizeMesh: true },
                    { quality: 0.2, distance: 30, optimizeMesh: true }
                ],
                false,
                BABYLON.SimplificationType.QUADRATIC,
                (mesh, lodIndex) => {
                    console.log(`LOD ${lodIndex} generated for ${mesh.name}`);
                }
            );

            // Level 3: Completely cull (hide) the object when it is very far away (e.g., > 100 units)
            mesh.addLODLevel(100, null);

        } catch (err) {
            console.warn(`Failed to auto-generate LODs for ${mesh.name}:`, err);
        }
    }

    /**
     * Alternatively, this enables the Scene Optimizer, which dynamically degrades
     * visual quality (shadows, particles, texture resolution, then LODs) if the FPS drops below a target.
     */
    enableDynamicSceneOptimizer(targetFPS = 60) {
        if (this.optimizationActive) return;

        console.log(`Enabling Dynamic Scene Optimizer (Target: ${targetFPS} FPS)`);

        const options = BABYLON.SceneOptimizerOptions.HighDegradationAllowed(targetFPS);
        this.optimizer = new BABYLON.SceneOptimizer(this.scene, options);

        this.optimizer.start();
        this.optimizationActive = true;

        this.optimizer.onNewOptimizationAppliedObservable.add((optim) => {
            console.log(`FPS drop detected. Applied optimization: ${optim.getDescription()}`);
        });

        this.optimizer.onSuccessObservable.add(() => {
            console.log(`Scene optimization stabilized at target FPS.`);
        });
    }
}

// Attach to global for integration
if (typeof window !== 'undefined' && window.BABYLON) {
    window.AutoLODSystem = AutoLODSystem;
}
