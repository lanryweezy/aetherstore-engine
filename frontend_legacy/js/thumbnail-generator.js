/**
 * thumbnail-generator.js
 * Generates 3D thumbnails instantly on the client side using Babylon.js
 * This offloads heavy rendering from the backend, costing zero server CPU.
 */

class ClientThumbnailGenerator {
    constructor() {
        // Create an offscreen canvas for rendering
        this.canvas = document.createElement('canvas');
        this.canvas.width = 512;
        this.canvas.height = 512;
        this.canvas.style.display = 'none';
        document.body.appendChild(this.canvas);

        this.engine = new BABYLON.Engine(this.canvas, true, { preserveDrawingBuffer: true, stencil: true });
    }

    /**
     * Generate thumbnails from a File object before uploading
     * @param {File} file - The 3D model file (.glb, .gltf, .obj)
     * @returns {Promise<Object>} Object containing data URLs for front, side, top, iso
     */
    async generateFromUpload(file) {
        return new Promise((resolve, reject) => {
            const scene = new BABYLON.Scene(this.engine);
            scene.clearColor = new BABYLON.Color4(0.96, 0.96, 0.96, 1); // Light gray background

            // Add lighting
            const hemisphericLight = new BABYLON.HemisphericLight("hemiLight", new BABYLON.Vector3(0, 1, 0), scene);
            hemisphericLight.intensity = 0.7;
            const dirLight = new BABYLON.DirectionalLight("dirLight", new BABYLON.Vector3(-1, -2, -1), scene);
            dirLight.intensity = 0.8;

            // Setup camera
            const camera = new BABYLON.ArcRotateCamera("camera", 0, 0, 10, BABYLON.Vector3.Zero(), scene);

            // Read file into memory
            const reader = new FileReader();
            reader.onload = async (e) => {
                const data = e.target.result;
                // Determine extension
                const extension = "." + file.name.split('.').pop().toLowerCase();

                try {
                    // Load the model into the scene
                    const result = await BABYLON.SceneLoader.ImportMeshAsync("", data, "", scene, null, extension);
                    const rootNode = result.meshes[0];

                    // Normalize the model size and center it
                    rootNode.normalizeToUnitCube();
                    const boundingInfo = rootNode.getHierarchyBoundingVectors();
                    const center = boundingInfo.max.add(boundingInfo.min).scale(0.5);
                    rootNode.position = center.scale(-1);

                    // Re-calculate after centering
                    camera.setTarget(BABYLON.Vector3.Zero());
                    camera.radius = 2.5; // Back up slightly from the unit cube

                    const thumbnails = {};

                    // The camera angles (alpha = rotation around Y, beta = rotation around X)
                    const views = {
                        "front": { alpha: Math.PI / 2, beta: Math.PI / 2 },
                        "side": { alpha: Math.PI, beta: Math.PI / 2 },
                        "top": { alpha: Math.PI / 2, beta: 0 },
                        "iso": { alpha: Math.PI / 4, beta: Math.PI / 3 }
                    };

                    // Render each view and save the canvas as a base64 image
                    for (const [viewName, angles] of Object.entries(views)) {
                        camera.alpha = angles.alpha;
                        camera.beta = angles.beta;

                        scene.render();

                        thumbnails[viewName] = this.canvas.toDataURL("image/png");
                    }

                    // Cleanup
                    scene.dispose();
                    resolve(thumbnails);

                } catch (err) {
                    scene.dispose();
                    reject(err);
                }
            };

            reader.onerror = (err) => reject(err);
            // Babylon SceneLoader needs data: URIs or ArrayBuffers depending on format.
            // We use readAsDataURL which handles .glb and .gltf robustly with Babylon.
            reader.readAsDataURL(file);
        });
    }

    dispose() {
        this.engine.dispose();
        if (this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

// Export as a global for use in other scripts
window.ClientThumbnailGenerator = ClientThumbnailGenerator;
