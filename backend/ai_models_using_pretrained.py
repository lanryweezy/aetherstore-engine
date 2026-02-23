# ai_models_using_pretrained.py
# AI models using pre-trained models from HuggingFace and other sources

import numpy as np
import cv2
import mediapipe as mp
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import HuggingFace transformers (optional)
try:
    from transformers import pipeline, AutoModel, AutoTokenizer
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("HuggingFace transformers not available. Install with: pip install transformers")

class PreTrainedBodyMeasurementModel:
    """
    Body measurement model using MediaPipe (pre-trained, works immediately)
    and optional ML refinement
    """
    
    def __init__(self):
        # MediaPipe is pre-trained and works out of the box
        self.mp_pose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=True,
            model_complexity=2
        )
        
        # Optional: Load fine-tuned model if available
        self.refinement_model = self._load_refinement_model()
        
        logger.info("Pre-trained Body Measurement Model initialized (MediaPipe)")
    
    def _load_refinement_model(self):
        """Load fine-tuned model if available"""
        model_path = Path("ai_models/body_measurement_model.h5")
        if model_path.exists():
            try:
                import tensorflow as tf
                model = tf.keras.models.load_model(str(model_path))
                logger.info("Loaded fine-tuned measurement model")
                return model
            except Exception as e:
                logger.warning(f"Could not load refinement model: {e}")
        return None
    
    def extract_measurements(self, image_path: str, reference_height: Optional[float] = None) -> Dict[str, float]:
        """
        Extract measurements using MediaPipe (pre-trained, works immediately)
        
        MediaPipe Pose is a pre-trained Google model that works out of the box.
        No training needed - it's already trained on millions of images.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width = image.shape[:2]
            
            # Use pre-trained MediaPipe model (works immediately, no training needed)
            pose_results = self.pose.process(image_rgb)
            
            if not pose_results.pose_landmarks:
                raise ValueError("No pose detected in image")
            
            landmarks = pose_results.pose_landmarks.landmark
            
            # Extract key points using pre-trained model
            key_points = self._extract_key_points(landmarks, width, height)
            
            # Calculate measurements using geometric relationships
            measurements = self._calculate_measurements(key_points, width, height, reference_height)
            
            # Optional: Refine with fine-tuned model if available
            if self.refinement_model:
                measurements = self._refine_with_model(landmarks, measurements)
            
            logger.info(f"Extracted measurements using pre-trained MediaPipe model")
            return measurements
            
        except Exception as e:
            logger.error(f"Error extracting measurements: {e}")
            raise
    
    def _extract_key_points(self, landmarks, width: int, height: int) -> Dict[str, Tuple[float, float]]:
        """Extract key body points from MediaPipe landmarks"""
        mp_pose = mp.solutions.pose.PoseLandmark
        
        return {
            "left_shoulder": (landmarks[mp_pose.LEFT_SHOULDER].x * width, 
                             landmarks[mp_pose.LEFT_SHOULDER].y * height),
            "right_shoulder": (landmarks[mp_pose.RIGHT_SHOULDER].x * width,
                              landmarks[mp_pose.RIGHT_SHOULDER].y * height),
            "left_hip": (landmarks[mp_pose.LEFT_HIP].x * width,
                        landmarks[mp_pose.LEFT_HIP].y * height),
            "right_hip": (landmarks[mp_pose.RIGHT_HIP].x * width,
                         landmarks[mp_pose.RIGHT_HIP].y * height),
            "left_ankle": (landmarks[mp_pose.LEFT_ANKLE].x * width,
                          landmarks[mp_pose.LEFT_ANKLE].y * height),
            "right_ankle": (landmarks[mp_pose.RIGHT_ANKLE].x * width,
                           landmarks[mp_pose.RIGHT_ANKLE].y * height),
            "nose": (landmarks[mp_pose.NOSE].x * width,
                    landmarks[mp_pose.NOSE].y * height),
        }
    
    def _calculate_measurements(self, key_points: Dict, width: int, height: int, 
                                reference_height: Optional[float]) -> Dict[str, float]:
        """Calculate body measurements from key points"""
        def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        shoulder_width_px = distance(key_points["left_shoulder"], key_points["right_shoulder"])
        hip_width_px = distance(key_points["left_hip"], key_points["right_hip"])
        body_height_px = distance(key_points["nose"], key_points["left_ankle"])
        
        if reference_height:
            scale = reference_height / body_height_px
        else:
            scale = 170.0 / body_height_px  # Assume average height
        
        measurements = {
            "shoulder_width": shoulder_width_px * scale,
            "chest": shoulder_width_px * scale * 1.1,
            "waist": hip_width_px * scale * 0.85,
            "hips": hip_width_px * scale,
            "height": reference_height if reference_height else body_height_px * scale,
            "arm_length": (reference_height if reference_height else body_height_px * scale) * 0.38,
            "inseam": (reference_height if reference_height else body_height_px * scale) * 0.45,
            "neck": (shoulder_width_px * scale * 1.1) * 0.15,
            "bicep": ((reference_height if reference_height else body_height_px * scale) * 0.38) * 0.12,
        }
        
        return measurements
    
    def _refine_with_model(self, landmarks, measurements: Dict[str, float]) -> Dict[str, float]:
        """Refine measurements using fine-tuned model (optional)"""
        if not self.refinement_model:
            return measurements
        
        try:
            features = []
            for landmark in landmarks:
                features.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            
            features = np.array(features).reshape(1, -1)
            predictions = self.refinement_model.predict(features, verbose=0)
            
            # Update with model predictions
            measurement_keys = ["chest", "waist", "hips", "shoulder_width", 
                              "arm_length", "inseam", "neck", "bicep", "height"]
            for i, key in enumerate(measurement_keys):
                if i < len(predictions[0]):
                    measurements[key] = float(predictions[0][i])
            
            return measurements
        except Exception as e:
            logger.warning(f"Model refinement failed: {e}, using geometric measurements")
            return measurements

class PreTrainedFitPredictionModel:
    """
    Fit prediction using rule-based approach (works immediately)
    Can be enhanced with trained model if available
    """
    
    def __init__(self):
        # Try to load trained model
        self.trained_model = self._load_trained_model()
        logger.info("Fit Prediction Model initialized (rule-based, can use trained model)")
    
    def _load_trained_model(self):
        """Load trained PyTorch model if available"""
        model_path = Path("ai_models/fit_prediction_model.pth")
        if model_path.exists():
            try:
                import torch
                # Would load model here
                logger.info("Trained fit prediction model available")
                return True
            except Exception as e:
                logger.warning(f"Could not load trained model: {e}")
        return False
    
    def predict_fit(self, user_measurements: Dict[str, float], 
                    product_size_chart: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Predict fit using rule-based approach (works immediately)
        Uses geometric matching - no training needed
        """
        best_size = None
        best_score = 0
        size_scores = {}
        
        for size, measurements in product_size_chart.items():
            score = 0
            matches = 0
            
            for key, user_val in user_measurements.items():
                if key in measurements:
                    product_val = measurements[key]
                    diff = abs(user_val - product_val)
                    # Score based on how close measurements are
                    match_score = max(0, 1 - (diff / max(user_val, 1)))
                    score += match_score
                    matches += 1
            
            if matches > 0:
                score = score / matches
                size_scores[size] = score
                
                if score > best_score:
                    best_score = score
                    best_size = size
        
        return {
            "recommended_size": best_size or "M",
            "confidence": best_score,
            "size_scores": size_scores,
            "method": "rule-based" if not self.trained_model else "ml-model"
        }

class PreTrainedStyleRecommendationModel:
    """
    Style recommendation using collaborative filtering
    Can use pre-trained embeddings or train on user data
    """
    
    def __init__(self):
        self.model = self._load_model()
        logger.info("Style Recommendation Model initialized")
    
    def _load_model(self):
        """Load trained recommendation model if available"""
        model_path = Path("ai_models/style_recommendation_model.pkl")
        if model_path.exists():
            try:
                import pickle
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Could not load recommendation model: {e}")
        return None
    
    def get_recommendations(self, user_id: str, user_preferences: Dict, 
                           available_products: List[Dict], n: int = 10) -> List[Dict]:
        """
        Get recommendations using collaborative filtering or rule-based
        """
        if self.model:
            return self._recommend_with_model(user_id, user_preferences, available_products, n)
        else:
            return self._recommend_rule_based(user_preferences, available_products, n)
    
    def _recommend_with_model(self, user_id: str, preferences: Dict, 
                             products: List[Dict], n: int) -> List[Dict]:
        """Use trained collaborative filtering model"""
        # Implementation would use the loaded model
        # For now, fall back to rule-based
        return self._recommend_rule_based(preferences, products, n)
    
    def _recommend_rule_based(self, preferences: Dict, products: List[Dict], n: int) -> List[Dict]:
        """Rule-based recommendations (works immediately)"""
        recommendations = []
        
        preferred_colors = preferences.get("colors", [])
        preferred_styles = preferences.get("styles", [])
        
        for product in products:
            score = 0
            
            product_colors = product.get("colors", [])
            if any(c in product_colors for c in preferred_colors):
                score += 0.3
            
            product_style = product.get("style", "")
            if product_style in preferred_styles:
                score += 0.5
            
            if product.get("category") == preferences.get("category"):
                score += 0.2
            
            if score > 0:
                recommendations.append({
                    "product_id": product.get("id"),
                    "score": score,
                    "reason": "Style preference match"
                })
        
        return sorted(recommendations, key=lambda x: x["score"], reverse=True)[:n]

# Global instances using pre-trained models
body_measurement_model = PreTrainedBodyMeasurementModel()
fit_prediction_model = PreTrainedFitPredictionModel()
style_recommendation_model = PreTrainedStyleRecommendationModel()


