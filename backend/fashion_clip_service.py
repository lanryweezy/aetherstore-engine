import logging
import os
import numpy as np

# Optional imports for AI research stack
try:
    import open_clip
    import torch
    from PIL import Image
    AI_STACK_AVAILABLE = True
except ImportError:
    AI_STACK_AVAILABLE = False

logger = logging.getLogger(__name__)
from config import settings

class FashionCLIPService:
    """
    Service for OpenFashionCLIP: Vision-and-Language Contrastive Learning 
    with Open-Source Fashion Data.
    """
    def __init__(self, model_path=None):
        self.initialized = False
        self.model_path = model_path or settings.MODEL_PATH_CLIP
        
        if AI_STACK_AVAILABLE:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            try:
                self.initialize()
            except Exception as e:
                logger.warning(f"Failed to initialize real FashionCLIP: {e}")
        else:
            logger.warning("AI research stack (open_clip/torch) not found. CLIP running in simulation mode.")

    def initialize(self):
        logger.info(f"Initializing FashionCLIP on {self.device}")
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-B/32')
        
        if os.path.exists(self.model_path):
            state_dict = torch.load(self.model_path, map_location=self.device)
            if isinstance(state_dict, dict) and 'CLIP' in state_dict:
                model.load_state_dict(state_dict['CLIP'])
            else:
                model.load_state_dict(state_dict)
        
        self.model = model.eval().requires_grad_(False).to(self.device)
        self.preprocess = preprocess
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.initialized = True

    def get_image_features(self, image_path):
        if not self.initialized: return np.random.rand(1, 512)
        try:
            img = Image.open(image_path).convert('RGB')
            img = self.preprocess(img).to(self.device)
            with torch.no_grad():
                image_features = self.model.encode_image(img.unsqueeze(0))
                image_features /= image_features.norm(dim=-1, keepdim=True)
            return image_features.cpu().numpy()
        except Exception: return np.random.rand(1, 512)

    def get_text_features(self, text_list):
        if not self.initialized: return np.random.rand(len(text_list), 512)
        try:
            prompt = "a photo of a"
            text_inputs = [f"{prompt} {t}" if not t.startswith("a photo of") else t for t in text_list]
            tokenized_text = self.tokenizer(text_inputs).to(self.device)
            with torch.no_grad():
                text_features = self.model.encode_text(tokenized_text)
                text_features /= text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy()
        except Exception: return np.random.rand(len(text_list), 512)

    def compute_similarity(self, image_path, text_list):
        img_features = self.get_image_features(image_path)
        text_features = self.get_text_features(text_list)
        logits = (100.0 * img_features @ text_features.T)
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)

# Global instance
fashion_clip_service = FashionCLIPService()
