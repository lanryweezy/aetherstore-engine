# Roadmap: Meta Momentum Integration for AetherStore

## 📌 Overview
[Momentum](https://github.com/facebookresearch/momentum) is a library from Meta Research providing foundational algorithms for human kinematic motion and numerical optimization solvers. Integrating Momentum will transform AetherStore from a static measurement tool into a **High-Fidelity Virtual Mirror**.

## 🚀 Why Momentum?

While our current stack (MediaPipe + SAM 3D) is excellent for static measurements and segmentation, Momentum offers:
*   **Bio-Mechanical Realism:** Prevents "unnatural" poses by applying human skeletal constraints.
*   **Inverse Kinematics (IK):** Allows users to move an avatar's limb (e.g., "raise arm") while the rest of the body adapts naturally.
*   **Precision Optimization:** Fits a parameterized human model to RGB/RGBD data for ultra-accurate sizing.

## 📊 Comparison: Current vs. Momentum Upgrade

| Feature | Current (MediaPipe/SAM) | Momentum Upgrade |
| :--- | :--- | :--- |
| **Tracking** | 2D/3D Landmarks (Skeleton only) | Full Kinematic Solve (Joints + Limits) |
| **Accuracy** | Heuristic-based (Estimates) | Optimization-based (Global fit) |
| **Animation** | Static or rigid transforms | Dynamic IK (Fluid motion) |
| **AR Mirror** | Basic overlay | Real-time motion-synced avatar |

## 🛠 Integration Strategy

### Phase 1: Environment Setup
*   Install `pymomentum` (Conda-forge or build from source).
*   Initialize the `CharacterSolver` in the backend.

### Phase 2: Enhanced AI Processing
*   Modify `backend/ai_processing.py` to use Momentum as the primary pose optimizer.
*   Feed MediaPipe landmarks into Momentum's solver for a "stabilized" skeletal result.

### Phase 3: Live AR Mirror (Frontend)
*   Stream webcam frames to the backend.
*   Momentum solves the pose and returns joint rotations.
*   The 3D Scene (Babylon.js/Three.js) applies these rotations to the user's avatar in real-time.

## 📈 Future Potential: "The Dynamic Fitting Room"
With Momentum, we can move from "Will this fit?" to "How does this move?"
*   **Drape Simulation:** Simulate how fabric stretches and folds as the user "walks" or "dances" in their digital clothes.
*   **Motion Analytics:** Analyze range-of-motion constraints for sportswear and technical apparel.

---
*Status: Identified as a future "Wave 11" improvement. Not currently active.*
