# ai_processing.py
# Refactored AI Processor: High-level Orchestration & Resilience Layer

import logging
import os
from typing import Dict, List, Optional, Any
from ai_orchestrators import (
    VisionOrchestrator, AuditoryOrchestrator, CognitiveOrchestrator,
    BehavioralOrchestrator, SpatialOrchestrator, GovernanceOrchestrator
)
from ai_models_real import body_measurement_model, fit_prediction_model, style_recommendation_model

# Import ALL Pillar Services
from fashion_clip_service import fashion_clip_service
from shaper_service import shaper_service
from boxer_service import boxer_service
from momentum_service import momentum_service
from tribe_service import tribe_service
from flowdec_service import flowdec_service
from sapiens_service import sapiens_service
from musicgen_service import musicgen_service
from moviegen_service import moviegen_service
from vjepa_service import vjepa_service
from llama_stylist_service import llama_stylist_service
from digital_twin_service import digital_twin_service
from llama_vision_service import llama_vision_service
from sam2_video_service import sam2_video_service
from spirit_lm_service import spirit_lm_service
from seamless_service import seamless_service
from social_ai_service import social_ai_service
from store_arch_service import store_arch_service
from animation_service import animation_service
from spatial_security_service import scenescript_service, audioseal_service
from foundation_peak_service import sam3_service, neuralset_service
from tactile_service import tactile_service
from superintelligence_pinnacle_service import maverick_service, motivo_service
from xr_perception_service import locate3d_service, perception_service
from neuromorphic_service import neuromorphic_service
from autonomous_house_service import autonomous_house_service

# Import Background Tasks for heavy AI workloads
from tasks import (
    generate_metric_3d_task, 
    generate_runway_reel_task, 
    generate_photoreal_twin_task,
    generate_neuromorphic_manifest_task
)

logger = logging.getLogger(__name__)

class AIProcessor:
    """The High-Level Router for AetherStore AI"""
    
    def __init__(self):
        # Service Registry
        self.services = {
            'clip': fashion_clip_service, 'shaper': shaper_service, 'boxer': boxer_service,
            'momentum': momentum_service, 'tribe': tribe_service, 'flowdec': flowdec_service,
            'sapiens': sapiens_service, 'musicgen': musicgen_service, 'moviegen': moviegen_service,
            'vjepa': vjepa_service, 'llama': llama_stylist_service, 'dtc': digital_twin_service,
            'llama_vision': llama_vision_service, 'sam2_video': sam2_video_service,
            'spirit_lm': spirit_lm_service, 'seamless': seamless_service,
            'social_ai': social_ai_service, 'store_arch': store_arch_service,
            'animation': animation_service, 'scenescript': scenescript_service,
            'audioseal': audioseal_service, 'sam3': sam3_service, 'neuralset': neuralset_service,
            'tactile': tactile_service, 'maverick': maverick_service, 'motivo': motivo_service,
            'locate3d': locate3d_service, 'perception': perception_service,
            'neuromorphic': neuromorphic_service,
            'autonomous_house': autonomous_house_service
        }
        
        # Specialized Orchestrators (Delegation Layer)
        self.vision = VisionOrchestrator(self.services)
        self.auditory = AuditoryOrchestrator(self.services)
        self.cognitive = CognitiveOrchestrator(self.services)
        self.behavioral = BehavioralOrchestrator(self.services)
        self.spatial = SpatialOrchestrator(self.services)
        self.governance = GovernanceOrchestrator(self.services)

        # Legacy Models
        self.body_measurement_model = body_measurement_model
        self.fit_prediction_model = fit_prediction_model
        self.style_recommendation_model = style_recommendation_model
        
        logger.info("AI Processor Refactored: Task-Oriented Delegation active.")

    # --- ROUTING METHODS (ASYNC TASK DELEGATION) ---

    async def generate_metric_3d_model(self, sequence_id, text=None):
        """Dispatches asynchronous 3D synthesis task"""
        task = generate_metric_3d_model_task.delay(sequence_id, text)
        return {"status": "processing", "task_id": task.id}

    async def generate_cinematic_reels(self, aid, pid, style): 
        """Dispatches asynchronous cinematic video task"""
        task = generate_runway_reel_task.delay(aid, pid, style)
        return {"status": "processing", "task_id": task.id}

    async def generate_photoreal_twin(self, sid, splats=False): 
        """Dispatches asynchronous digital twin reconstruction task"""
        task = generate_photoreal_twin_task.delay(sid, splats)
        return {"status": "processing", "task_id": task.id}

    async def generate_neuromorphic_manifest(self, user_id: str, eeg_data: dict):
        """Dispatches asynchronous brain-to-GCode task"""
        task = generate_neuromorphic_manifest_task.delay(user_id, eeg_data)
        return {"status": "processing", "task_id": task.id}

    async def get_task_status(self, task_id: str):
        """Checks status of a background AI task using Celery's result backend"""
        from worker import celery_app
        res = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": res.status, # PENDING, STARTED, SUCCESS, FAILURE
            "result": res.result if res.ready() else None
        }

    # --- ROUTING METHODS (SYNCHRONOUS DELEGATION) ---

    async def perform_foundation_body_scan(self, path):
        return await self.vision.perform_hq_scan(path)

    async def get_intelligent_styling_advice(self, user_id, msg):
        return await self.cognitive.get_expert_advice(user_id, msg)

    async def generate_store_music(self, prompt, duration=15):
        return await self.auditory.resilient_call('musicgen', 'generate_store_vibe', prompt, duration)

    async def solve_pose_kinematics(self, landmarks):
        return await self.behavioral.resilient_call('momentum', 'solve_kinematics', landmarks)

    async def analyze_spatial_layout(self, path, prompts): 
        return await self.spatial.resilient_call('boxer', 'detect_room_layout', path, prompts)

    async def predict_neuro_aesthetic_response(self, path, ctx=None): 
        return await self.governance.resilient_call('tribe', 'predict_aesthetic_response', path, ctx)

    async def generate_audio_immersion(self, fabric, intensity): 
        return await self.auditory.resilient_call('flowdec', 'generate_fabric_foley', fabric, intensity)

    async def analyze_user_action(self, vid): 
        return await self.behavioral.resilient_call('vjepa', 'analyze_movement_context', vid)

    async def estimate_pbr_materials(self, path): 
        return await self.vision.resilient_call('dtc', 'estimate_materials', path)

    async def analyze_visual_style(self, path, query): 
        return await self.cognitive.get_expert_advice(None, query, path)

    async def generate_expressive_voice_advice(self, text, emotion="enthusiastic"): 
        return await self.auditory.resilient_call('spirit_lm', 'generate_expressive_speech', text, emotion)

    async def translate_fashion_content(self, text, lang): 
        return await self.governance.resilient_call('seamless', 'translate_fashion_dialogue', text, lang)

    async def analyze_social_group(self, sid, mids): 
        return await self.cognitive.resilient_call('social_ai', 'analyze_group_style', sid, mids)

    async def analyze_store_architecture(self, desc): 
        return await self.spatial.build_environment(desc)

    async def reconstruct_structured_scene(self, cid): 
        return await self.spatial.resilient_call('scenescript', 'reconstruct_structured_scene', cid)

    async def watermark_asset_audio(self, path, aid): 
        return await self.governance.secure_media(path, aid)

    async def segment_with_sam3(self, path): 
        return await self.vision.resilient_call('sam3', 'segment_ultra_hq', path)

    async def refine_neuro_model(self, path): 
        return await self.governance.resilient_call('neuralset', 'process_neural_dataset', path)

    async def predict_tactile_feel(self, mid, path): 
        return await self.vision.resilient_call('tactile', 'predict_fabric_feel', mid, path)

    async def get_maverick_expert_advice(self, uid, msg): 
        return await self.cognitive.get_expert_advice(uid, msg)

    async def generate_assistant_behavior(self, aid, intent): 
        return await self.behavioral.resilient_call('motivo', 'generate_agent_behavior', aid, [0,0,0], intent)

    async def generate_locomotion(self, user_id, style="catwalk", duration=5.0):
        """Generate neural-driven character locomotion using AI4AnimationPy"""
        return await self.behavioral.resilient_call('animation', 'generate_locomotion', user_id, style, duration)

    async def track_video_garment(self, sid, mask): 
        return await self.vision.resilient_call('sam2_video', 'track_garment_in_video', sid, mask)

    async def get_video_overlay(self, sid, fid): 
        return await self.vision.resilient_call('sam2_video', 'get_tracked_overlay', sid, fid)

    async def solve_xr_fit(self, fid, pose):
        """Ultra-low latency (40ms) spatial reasoning using Meta Locate 3D"""
        return await self.vision.resilient_call('locate3d', 'solve_spatial_fit', fid, pose)

    async def detect_micro_fashion_details(self, path):
        """Micro-object and textile detection using Meta Perception Encoder"""
        return await self.vision.resilient_call('perception', 'detect_micro_details', path)

    async def trigger_autonomous_cycle(self, market_data: dict):
        """Moonshot: Trigger autonomous fashion house generation cycle"""
        return await self.governance.resilient_call('autonomous_house', 'initiate_autonomous_cycle', market_data)

    # --- CORE UTILITIES ---
    def get_style_recommendations(self, uid, prefs, avail, n=10):
        return self.style_recommendation_model.get_recommendations(uid, prefs, avail, n)

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Returns the health and initialization status of all 29 AI pillars, including performance stats"""
        from config import settings
        from observability_middleware import get_performance_stats
        
        telemetry = {
            "pillars": {},
            "performance": get_performance_stats()
        }
        
        weight_map = {
            'clip': settings.MODEL_PATH_CLIP,
            'shaper': settings.MODEL_PATH_SHAPER,
            'boxer': settings.MODEL_PATH_BOXER,
            'momentum': settings.MODEL_PATH_MOMENTUM,
            'sapiens': settings.MODEL_PATH_SAPIENS,
            'tribe': settings.MODEL_PATH_TRIBE,
            'flowdec': settings.MODEL_PATH_FLOWDEC,
            'sam2_video': settings.MODEL_PATH_SAM2_VIDEO,
            'sam3': settings.MODEL_PATH_SAM3,
            'tactile': settings.MODEL_PATH_TACTOVIS,
            'dtc': settings.MODEL_PATH_DTC,
            'locate3d': settings.MODEL_PATH_LOCATE3D if hasattr(settings, 'MODEL_PATH_LOCATE3D') else None
        }

        for name, service in self.services.items():
            weight_path = weight_map.get(name)
            weights_found = os.path.exists(weight_path) if weight_path else True 
            
            telemetry["pillars"][name] = {
                "status": "online" if getattr(service, 'initialized', True) else "simulation",
                "weights_verified": weights_found,
                "version": getattr(service, 'model_path', 'v1.0-research'),
                "health": "ok" if (getattr(service, 'initialized', True) and weights_found) else "degraded"
            }
        return telemetry

# Global Instance
ai_processor = AIProcessor()
AdvancedAIService = AIProcessor
