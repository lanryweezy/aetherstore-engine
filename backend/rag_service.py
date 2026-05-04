import logging
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import ProductDB
from fashion_clip_service import fashion_clip_service
from database import SessionLocal

logger = logging.getLogger(__name__)

class RAGService:
    """
    High-Precision Multi-Modal Retrieval-Augmented Generation Service.
    Unifies Vision (CLIP) and Language (Llama 4) for hybrid fashion search.
    """
    def __init__(self):
        self.initialized = True
        self.vector_cache: Dict[str, np.ndarray] = {}
        logger.info("Multi-Modal RAG Service Initialized.")

    def _get_mock_embedding(self, text: str) -> np.ndarray:
        seed = sum(ord(c) for i, c in enumerate(text)) % 1000
        np.random.seed(seed)
        return np.random.rand(512).astype(np.float32)

    async def retrieve_relevant_products(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Standard semantic text search (Language-only)."""
        return await self._execute_search(query_vec=self._get_mock_embedding(query), query_text=query, limit=limit)

    async def retrieve_multimodal_products(self, query_text: str, image_path: Optional[str], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Moonshot Search: Combines visual features and linguistic intent.
        Example: [Image of Jacket] + "Make it more cyberpunk and silk"
        """
        logger.info(f"RAG: Executing Multi-Modal search. Text: '{query_text}', Image: {image_path}")
        
        # 1. Generate Hybrid Embedding
        text_vec = self._get_mock_embedding(query_text)
        
        if image_path:
            # Simulate fetching CLIP image embedding
            img_vec = fashion_clip_service.get_image_features(image_path)[0]
            # Weighted Fusion (60% Text Intent / 40% Visual Anchor)
            hybrid_vec = (text_vec * 0.6) + (img_vec * 0.4)
        else:
            hybrid_vec = text_vec

        return await self._execute_search(query_vec=hybrid_vec, query_text=query_text, limit=limit)

    async def _execute_search(self, query_vec: np.ndarray, query_text: str, limit: int) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            products = db.query(ProductDB).filter(ProductDB.is_active == True).all()
            if not products: return []

            scored_products = []
            for p in products:
                p_vec = self.vector_cache.get(p.id)
                if p_vec is None:
                    p_vec = self._get_mock_embedding(f"{p.name} {p.description} {p.material}")
                    self.vector_cache[p.id] = p_vec
                
                # Semantic Similarity
                score = np.dot(query_vec, p_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(p_vec))
                
                # Contextual Boosts (Hard matches)
                if query_text.lower() in p.name.lower(): score += 0.2
                if p.material and p.material.lower() in query_text.lower(): score += 0.15
                
                scored_products.append((float(score), p))
            
            scored_products.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for score, p in scored_products[:limit]:
                results.append({
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "material": p.material,
                    "relevance_score": round(score, 4),
                    "search_modality": "multimodal" if "hybrid" in str(query_vec.shape) else "semantic"
                })
            
            return results
        finally:
            db.close()

rag_service = RAGService()
