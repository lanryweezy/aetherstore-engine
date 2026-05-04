# Roadmap: Meta Boxer Integration for Spatial AR

## 📌 Overview
[Boxer](https://github.com/facebookresearch/boxer) is a system for "Robust Lifting of Open-World 2D Bounding Boxes to 3D." It specializes in turning 2D detections (from images) into 3D Oriented Bounding Boxes (OBBs) within a physical environment.

## 🚀 Why Boxer for AetherStore?

While **SAM 3D** (our current tool) is great for reconstructing the *shape* of a product, **Boxer** is optimized for **Spatial Awareness** in the real world:
*   **Room Anchoring:** Detect a physical mirror or wardrobe in a user's room and automatically anchor the "Virtual Mirror" UI there.
*   **Inventory Mapping:** Walk through a physical boutique with a camera and automatically map every product's 3D position in the room.
*   **Open-World Detection:** Use text prompts (via OWL-ViT) to find any fashion-related object in a scene.

## 📊 Feature Comparison

| Feature | SAM 3D (Current) | Boxer (Spatial Upgrade) |
| :--- | :--- | :--- |
| **Output** | High-fidelity Point Cloud / Mesh | Oriented 3D Bounding Boxes (OBB) |
| **Focus** | Object Geometry & Masking | Global Scene Fusion & Positioning |
| **Strength** | Creating a 3D digital twin of an item | Mapping where items are in a 3D room |
| **Detection** | Mask-based | Text-promptable (Open-Vocabulary) |

## 🛠 Potential Integration

### 1. Spatial Boutiques (AR)
Use Boxer to detect "clothing racks" or "mannequins" in a physical space. AetherStore can then "replace" or "augment" these physical anchors with digital stock.

### 2. Intelligent AR Mirror Placement
Instead of the user manually placing the virtual mirror, the AI uses Boxer to find a "wall" or "vertical surface" near a "person" and suggests the optimal 3D placement.

### 3. Mixed Reality Inventory
Lifting 2D detections to 3D boxes allows the engine to calculate exactly how much physical space a "digital wardrobe" would take up in a user's real room.

---
*Status: Identified as a future "Spatial Intelligence" improvement for AR/MR platforms.*
