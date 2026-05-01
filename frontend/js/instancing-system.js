/**
 * InstancingSystem
 * High-performance 3D rendering manager that dramatically reduces draw calls
 * for identical objects (like racks of identical shirts).
 */

class InstancingSystem {
    constructor(scene) {
        this.scene = scene;
        this.baseMeshes = new Map(); // Store the original loaded meshes
    }

    async addProduct(modelUrl, position, rotation, scaling) {
        let container = this.baseMeshes.get(modelUrl);

        if (!container) {
            // First time seeing this model, load it into an AssetContainer
            container = await BABYLON.SceneLoader.LoadAssetContainerAsync("", modelUrl, this.scene);

            // Disable physics on the template if it exists
            container.meshes.forEach(mesh => {
                if (mesh.physicsImpostor) {
                    mesh.physicsImpostor.dispose();
                    mesh.physicsImpostor = null;
                }
            });

            this.baseMeshes.set(modelUrl, container);
        }

        // Create a fast, lightweight instance hierarchy
        const instance = container.instantiateModelsToScene();
        const rootNode = instance.rootNodes[0];

        rootNode.position = position || new BABYLON.Vector3(0, 0, 0);

        if (rotation) {
            rootNode.rotation = rotation;
        }

        if (scaling) {
            rootNode.scaling = scaling;
        }

        // Return the root node of the instantiated hierarchy
        return rootNode;
    }

    clear() {
        this.baseMeshes.forEach(mesh => {
            mesh.dispose();
        });
        this.baseMeshes.clear();
    }
}

// Attach to global for integration
if (window.BABYLON) {
    window.InstancingSystem = InstancingSystem;
}
