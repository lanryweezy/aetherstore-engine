# Roadmap: Meta ShapeR Integration for High-Fidelity 3D Generation

## 📌 Overview
[ShapeR](https://github.com/facebookresearch/ShapeR) is a system for "Robust Conditional 3D Shape Generation from Casual Captures." It uses rectified flow transformers to turn image sequences into accurate, metric 3D meshes (.glb).

## 🚀 Why ShapeR for AetherStore?

ShapeR is the "missing link" for turning physical fashion into digital assets:
*   **Casual-to-Metric:** Brand owners can walk around a garment with a smartphone and generate a mesh that is accurately scaled to real-world dimensions.
*   **Text-Conditioned Refinement:** Uses captions to help the model understand fabric types and fine details that might be blurry in photos.
*   **Ready-to-Simulate:** Produces clean GLB files that can be imported directly into our Babylon.js/Three.js viewers.
*   **Scene Reconstruction:** Can reconstruct entire boutiques by applying the model to each detected object in a room capture.

## 📊 3D Technology Comparison

| Feature | SAM 3D (Object Masks) | ShapeR (Shape Generation) |
| :--- | :--- | :--- |
| **Primary Input** | Single Image / Video | Image Sequence + Camera Poses |
| **Output Type** | Segmentation / Point Cloud | **Metric 3D Mesh (.glb)** |
| **Accuracy** | Visual Shape only | Metric-accurate (Real dimensions) |
| **Use Case** | Fast background removal | **Creating Digital Twins for Sale** |

## 🛠 Potential Integration

### 1. The "Magic Importer" (Backend)
Replace our simulated 3D generation logic in `ai_processing.py` with the ShapeR inference pipeline.
1.  User uploads a 10-second video of a product.
2.  Backend runs ShapeR to "solve" the 3D shape.
3.  Resulting GLB is saved to `backend/uploads/` and becomes immediately buyable.

### 2. Metric Sizing Accuracy
Because ShapeR produces *metric* shapes, we can calculate the exact volume and surface area of a digital garment, leading to much more accurate **Fit Predictions**.

### 3. Texture Projection
Combine ShapeR's mesh generation with high-resolution texture projection from the input frames to create hyper-realistic 3D clothing.

---
*Status: Identified as the primary engine for "Phase 2: Real-World to 3D" asset creation.*
