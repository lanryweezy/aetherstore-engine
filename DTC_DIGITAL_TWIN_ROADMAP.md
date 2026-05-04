# Roadmap: Meta Digital Twin Catalog (DTC) Integration

## 📌 Overview
[Digital Twin Catalog (DTC)](https://github.com/facebookresearch/DigitalTwinCatalog) is a large-scale photorealistic 3D object digital twin dataset and toolset. It includes state-of-the-art baselines for **Large Reconstruction Models (LRM)**, **Neural Inverse Rendering (PBIR)**, and **Gaussian Splatting**.

## 🚀 Why DTC for AetherStore?

DTC represents the transition from "3D Models" to "Digital Twins":

*   **Photorealistic Mesh/Splats:** Supports both traditional meshes and modern Gaussian Splats for ultra-fast, photo-perfect rendering.
*   **Material Intelligence (PBIR):** Uses Neural-PBIR to solve for shape, reflectance (BRDF), and illumination. This means digital clothes will react to light exactly like their physical counterparts.
*   **Sparse-View Reconstruction:** Generates high-quality twins from just a few photos using feed-forward LRM models.
*   **Ground Truth Catalog:** Access to 2,000+ high-quality scanned objects to benchmark and refine our custom fashion reconstruction models.

## 📊 Reconstruction Evolution

| Feature | ShapeR (Phase 2) | DTC Integration (The Twin) |
| :--- | :--- | :--- |
| **Output Type** | Metric Mesh (.glb) | Photoreal Mesh + Gaussian Splats |
| **Material Support**| Textures only | **Physics-Based Materials (PBR)** |
| **Lighting** | Static | **Relightable (Inverse Rendering)** |
| **Performance** | Standard | **Splat-optimized (Instant load)** |

## 🛠 Potential Integration

### 1. The "Digital Twin" Engine (Backend)
Integrate **LRM** for instant sparse-view reconstruction. When a brand owner uploads 3-4 photos of a product, the engine "solves" the photoreal twin in seconds.

### 2. Neural Inverse Rendering
Use **Neural-PBIR** to extract the exact material properties of a garment. This ensures that the "swish" of a silk dress in the 3D viewer matches the "sheen" of the physical item.

### 3. Egocentric Boutique (AR)
Leverage **Gaussian Splatting** from AR glasses captures to create hyper-realistic virtual showrooms that feel indistinguishable from reality.

---
*Status: Identified as the "High-Fidelity Asset Pipeline" (Wave 18) for AetherStore.*
