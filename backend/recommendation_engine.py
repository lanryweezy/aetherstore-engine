# Advanced Recommendation Engine for Aetherstore Engine
# Implements collaborative filtering, content-based filtering, and deep learning models

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import joblib
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime
import random
from shift15m_engine import Shift15MEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RecommendationResult:
    product_id: str
    score: float
    reason: str
    category: str
    brand_affinity: float
    style_compatibility: float

class CollaborativeFilteringEngine:
    """Collaborative filtering recommendation engine"""
    
    def __init__(self):
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.user_profiles = {}
        self.item_features = {}
        self.model = None
        self.is_trained = False
        
        logger.info("Collaborative Filtering Engine initialized")
    
    def build_user_item_matrix(self, interactions: List[Dict]) -> np.ndarray:
        """Build user-item interaction matrix"""
        # Extract unique users and items
        users = list(set([i['user_id'] for i in interactions]))
        items = list(set([i['product_id'] for i in interactions]))
        
        # Create mappings
        user_to_idx = {user: idx for idx, user in enumerate(users)}
        item_to_idx = {item: idx for idx, item in enumerate(items)}
        
        # Build matrix (rows = users, cols = items)
        matrix = np.zeros((len(users), len(items)))
        
        # Fill matrix with interaction weights
        for interaction in interactions:
            user_idx = user_to_idx[interaction['user_id']]
            item_idx = item_to_idx[interaction['product_id']]
            
            # Weight based on interaction type
            weight = 1.0  # Default
            if interaction['interaction_type'] == 'purchase':
                weight = 5.0
            elif interaction['interaction_type'] == 'try-on':
                weight = 3.0
            elif interaction['interaction_type'] == 'view':
                weight = 1.0
            
            matrix[user_idx, item_idx] = weight
        
        self.user_to_idx = user_to_idx
        self.item_to_idx = item_to_idx
        self.idx_to_user = {v: k for k, v in user_to_idx.items()}
        self.idx_to_item = {v: k for k, v in item_to_idx.items()}
        
        return matrix
    
    def train(self, interactions: List[Dict]):
        """Train the collaborative filtering model"""
        logger.info(f"Training collaborative filtering model with {len(interactions)} interactions")
        
        # Build user-item matrix
        self.user_item_matrix = self.build_user_item_matrix(interactions)
        
        # Compute item similarity matrix
        self.item_similarity_matrix = cosine_similarity(self.user_item_matrix.T)
        
        # Use SVD for dimensionality reduction (matrix factorization)
        n_factors = min(50, min(self.user_item_matrix.shape) - 1)
        if n_factors > 0:
            self.model = TruncatedSVD(n_components=n_factors, random_state=42)
            self.user_factors = self.model.fit_transform(self.user_item_matrix)
            self.item_factors = self.model.components_.T
        
        self.is_trained = True
        logger.info("Collaborative filtering model trained successfully")
    
    def get_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """Get recommendations for a specific user"""
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
        
        if user_id not in self.user_to_idx:
            # Cold start problem - return popular items
            return self.get_popular_items(n_recommendations)
        
        user_idx = self.user_to_idx[user_id]
        
        # Get user's interaction vector
        user_vector = self.user_item_matrix[user_idx]
        
        # Calculate scores for all items
        if hasattr(self, 'user_factors') and hasattr(self, 'item_factors'):
            # Use matrix factorization
            user_factor = self.user_factors[user_idx]
            scores = user_factor @ self.item_factors
        else:
            # Use item similarity approach
            user_interactions = self.user_item_matrix[user_idx]
            scores = user_interactions @ self.item_similarity_matrix
        
        # Mask items the user has already interacted with
        mask = user_vector > 0
        scores[mask] = -np.inf  # Set to negative infinity to exclude
        
        # Get top N recommendations
        top_item_indices = np.argsort(scores)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_item_indices:
            if scores[idx] > -np.inf:  # Check if it wasn't masked
                item_id = self.idx_to_item[idx]
                recommendations.append(
                    RecommendationResult(
                        product_id=item_id,
                        score=float(scores[idx]),
                        reason="Collaborative filtering based on similar users",
                        category="general",
                        brand_affinity=0.0,
                        style_compatibility=0.0
                    )
                )
        
        return recommendations
    
    def get_popular_items(self, n_items: int = 10) -> List[RecommendationResult]:
        """Return popular items for cold start problem"""
        if self.user_item_matrix is not None:
            item_popularity = np.sum(self.user_item_matrix, axis=0)
            top_item_indices = np.argsort(item_popularity)[::-1][:n_items]
            
            recommendations = []
            for idx in top_item_indices:
                item_id = self.idx_to_item[idx]
                recommendations.append(
                    RecommendationResult(
                        product_id=item_id,
                        score=float(item_popularity[idx]),
                        reason="Popular item based on overall interactions",
                        category="popular",
                        brand_affinity=0.0,
                        style_compatibility=0.0
                    )
                )
            return recommendations
        
        return []

class ContentBasedFilteringEngine:
    """Content-based recommendation engine based on item features"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.item_features_matrix = None
        self.items = {}
        self.is_trained = False
        
        logger.info("Content-Based Filtering Engine initialized")
    
    def extract_features(self, items: List[Dict]) -> np.ndarray:
        """Extract features from item descriptions and attributes"""
        # Create text representation for each item
        item_texts = []
        for item in items:
            text = f"{item.get('name', '')} {item.get('description', '')} {item.get('category', '')} {item.get('brand', '')}"
            # Add color, material, and style information
            attributes = item.get('attributes', {})
            text += f" {attributes.get('color', '')} {attributes.get('material', '')} {attributes.get('style', '')}"
            item_texts.append(text)
        
        # Vectorize text features
        features = self.tfidf_vectorizer.fit_transform(item_texts)
        return features
    
    def train(self, items: List[Dict]):
        """Train the content-based filtering model"""
        logger.info(f"Training content-based filtering model with {len(items)} items")
        
        self.items = {item['id']: item for item in items}
        self.item_features_matrix = self.extract_features(items)
        
        self.is_trained = True
        logger.info("Content-based filtering model trained successfully")
    
    def get_similar_items(self, item_id: str, n_items: int = 10) -> List[RecommendationResult]:
        """Get items similar to a given item"""
        if not self.is_trained or item_id not in self.items:
            return []
        
        item_idx = list(self.items.keys()).index(item_id)
        item_vector = self.item_features_matrix[item_idx]
        
        # Calculate similarity with all items
        similarities = cosine_similarity(item_vector, self.item_features_matrix).flatten()
        
        # Get top N similar items (excluding the original item)
        similar_indices = np.argsort(similarities)[::-1][1:n_items+1]
        
        recommendations = []
        for idx in similar_indices:
            similar_item_id = list(self.items.keys())[idx]
            recommendations.append(
                RecommendationResult(
                    product_id=similar_item_id,
                    score=float(similarities[idx]),
                    reason="Content similarity based on attributes and description",
                    category=self.items[similar_item_id].get('category', 'general'),
                    brand_affinity=0.0,
                    style_compatibility=0.0
                )
            )
        
        return recommendations
    
    def get_recommendations(self, user_profile: Dict, n_recommendations: int = 10) -> List[RecommendationResult]:
        """Get recommendations based on user profile"""
        if not self.is_trained:
            return []
        
        # Create user preference vector based on profile
        user_preferences = self._create_user_profile_vector(user_profile)
        
        # Calculate similarity with all items
        similarities = cosine_similarity([user_preferences], self.item_features_matrix).flatten()
        
        # Get top N recommendations
        top_item_indices = np.argsort(similarities)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_item_indices:
            item_id = list(self.items.keys())[idx]
            recommendations.append(
                RecommendationResult(
                    product_id=item_id,
                    score=float(similarities[idx]),
                    reason="Content match based on user preferences",
                    category=self.items[item_id].get('category', 'general'),
                    brand_affinity=user_profile.get('brand_affinity', 0.0),
                    style_compatibility=user_profile.get('style_compatibility', 0.0)
                )
            )
        
        return recommendations
    
    def _create_user_profile_vector(self, user_profile: Dict) -> np.ndarray:
        """Create a vector representing user preferences"""
        # This is a simplified approach - in reality, you'd want to 
        # generate vector representations based on user preferences
        user_text = f"{user_profile.get('preferred_colors', '')} {user_profile.get('preferred_brands', '')} {user_profile.get('style_preferences', '')}"
        
        # Transform user profile to same feature space as items
        user_vector = self.tfidf_vectorizer.transform([user_text])
        return user_vector.toarray()[0]

class DeepLearningRecommendationEngine:
    """Deep learning-based recommendation engine"""
    
    def __init__(self):
        self.user_embeddings = None
        self.item_embeddings = None
        self.user_features = {}
        self.item_features = {}
        self.is_trained = False
        
        logger.info("Deep Learning Recommendation Engine initialized")
    
    def train(self, interactions: List[Dict], users: List[Dict], items: List[Dict]):
        """Train the deep learning model (simulated)"""
        logger.info(f"Training deep learning model with {len(interactions)} interactions")
        
        # In a real implementation, this would use neural collaborative filtering
        # or other deep learning approaches
        
        # Simulate training by creating random embeddings
        n_users = len(set([i['user_id'] for i in interactions]))
        n_items = len(set([i['product_id'] for i in interactions]))
        embedding_dim = 50
        
        # Create random embeddings (in real implementation, these would be learned)
        self.user_embeddings = np.random.normal(0, 0.1, (n_users, embedding_dim))
        self.item_embeddings = np.random.normal(0, 0.1, (n_items, embedding_dim))
        
        # Store user and item features
        self.user_features = {u['id']: u for u in users}
        self.item_features = {i['id']: i for i in items}
        
        self.is_trained = True
        logger.info("Deep learning model trained successfully")
    
    def get_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """Get recommendations using deep learning approach"""
        if not self.is_trained:
            return []
        
        # Find user embedding (simplified lookup)
        user_idx = hash(user_id) % len(self.user_embeddings)
        user_embedding = self.user_embeddings[user_idx]
        
        # Calculate similarity scores
        scores = user_embedding @ self.item_embeddings.T
        
        # Get top N recommendations
        top_item_indices = np.argsort(scores)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_item_indices:
            # In a real implementation, we'd map indices back to item IDs properly
            # For simulation, we'll use the item ID from features
            item_ids = list(self.item_features.keys())
            if idx < len(item_ids):
                item_id = item_ids[idx]
                recommendations.append(
                    RecommendationResult(
                        product_id=item_id,
                        score=float(scores[idx]),
                        reason="Deep learning model prediction",
                        category=self.item_features[item_id].get('category', 'general'),
                        brand_affinity=0.0,
                        style_compatibility=0.0
                    )
                )
        
        return recommendations

class HybridRecommendationEngine:
    """Main recommendation engine that combines multiple approaches"""
    
    def __init__(self):
        self.collaborative_filter = CollaborativeFilteringEngine()
        self.content_filter = ContentBasedFilteringEngine()
        self.deep_learning = DeepLearningRecommendationEngine()
        self.shift_engine = Shift15MEngine()
        self.user_profiles = {}
        
        logger.info("Hybrid Recommendation Engine initialized with SHIFT15M Intelligence")
    
    async def train(self, interactions: List[Dict], users: List[Dict], items: List[Dict]):
        """Train all recommendation models"""
        logger.info("Training hybrid recommendation models...")
        
        # Train collaborative filtering
        if interactions:
            self.collaborative_filter.train(interactions)
            # Use historical vs current interactions for shift analysis
            mid = len(interactions) // 2
            self.shift_engine.calculate_distribution_shift(interactions[mid:], interactions[:mid])
        
        # Train content-based filtering
        if items:
            self.content_filter.train(items)
        
        # Train deep learning model
        if interactions and users and items:
            self.deep_learning.train(interactions, users, items)
        
        # Store user profiles
        self.user_profiles = {u['id']: u for u in users}
        
        logger.info("All recommendation models trained successfully")
    
    async def get_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """Get hybrid recommendations for a user with distribution shift awareness"""
        all_recommendations = []
        
        # Get recommendations from each engine
        cf_recs = self.collaborative_filter.get_recommendations(user_id, n_recommendations)
        cb_recs = await self._get_content_based_recommendations(user_id, n_recommendations)
        dl_recs = self.deep_learning.get_recommendations(user_id, n_recommendations)
        
        # Combine and rank recommendations
        all_recommendations.extend(cf_recs)
        all_recommendations.extend(cb_recs)
        all_recommendations.extend(dl_recs)
        
        # Remove duplicates while preserving scores and applying shift weights
        unique_recs = {}
        for rec in all_recommendations:
            # Apply SHIFT15M weights to favor trending categories
            final_score = self.shift_engine.apply_shift_weights(rec.product_id, rec.score, rec.category)
            
            if rec.product_id not in unique_recs:
                unique_recs[rec.product_id] = RecommendationResult(
                    product_id=rec.product_id,
                    score=final_score,
                    reason=rec.reason,
                    category=rec.category,
                    brand_affinity=rec.brand_affinity,
                    style_compatibility=rec.style_compatibility
                )
            else:
                # Combine scores with weights
                existing = unique_recs[rec.product_id]
                combined_score = (existing.score * 0.6) + (final_score * 0.4)
                unique_recs[rec.product_id] = RecommendationResult(
                    product_id=rec.product_id,
                    score=combined_score,
                    reason=f"{existing.reason} + {rec.reason}",
                    category=rec.category,
                    brand_affinity=rec.brand_affinity,
                    style_compatibility=rec.style_compatibility
                )
        
        # Sort by score and return top N
        sorted_recs = sorted(unique_recs.values(), key=lambda x: x.score, reverse=True)
        return sorted_recs[:n_recommendations]
    
    async def _get_content_based_recommendations(self, user_id: str, n_recommendations: int) -> List[RecommendationResult]:
        """Get content-based recommendations for a user"""
        user_profile = self.user_profiles.get(user_id, {})
        if user_profile:
            return self.content_filter.get_recommendations(user_profile, n_recommendations)
        else:
            # If no user profile, use popular items approach
            return self.collaborative_filter.get_popular_items(n_recommendations)
    
    async def get_similar_items(self, item_id: str, n_items: int = 10) -> List[RecommendationResult]:
        """Get items similar to a given item"""
        return self.content_filter.get_similar_items(item_id, n_items)
    
    async def retrain_user_model(self, user_id: str, new_interactions: List[Dict]):
        """Retrain model for a specific user with new interactions"""
        # In a real implementation, this would update the user's profile
        logger.info(f"Retraining model for user {user_id} with {len(new_interactions)} new interactions")
        
        # Update user profile in memory
        for interaction in new_interactions:
            if interaction['user_id'] == user_id:
                # Add to user profile or update preferences
                user_profile = self.user_profiles.get(user_id, {})
                user_profile['last_interaction'] = datetime.now().isoformat()
                # Update category preferences based on interaction
                if 'categories_interacted' not in user_profile:
                    user_profile['categories_interacted'] = []
                user_profile['categories_interacted'].append(interaction.get('category', 'unknown'))
                
                self.user_profiles[user_id] = user_profile

# Example usage
async def main():
    # Example data for testing
    interactions = [
        {'user_id': 'user1', 'product_id': 'prod1', 'interaction_type': 'view', 'timestamp': '2023-01-01'},
        {'user_id': 'user1', 'product_id': 'prod2', 'interaction_type': 'try-on', 'timestamp': '2023-01-02'},
        {'user_id': 'user1', 'product_id': 'prod3', 'interaction_type': 'purchase', 'timestamp': '2023-01-03'},
        {'user_id': 'user2', 'product_id': 'prod1', 'interaction_type': 'view', 'timestamp': '2023-01-01'},
        {'user_id': 'user2', 'product_id': 'prod3', 'interaction_type': 'try-on', 'timestamp': '2023-01-02'},
        {'user_id': 'user3', 'product_id': 'prod2', 'interaction_type': 'purchase', 'timestamp': '2023-01-01'},
    ]
    
    users = [
        {'id': 'user1', 'preferred_colors': 'blue,black', 'preferred_brands': 'brand1,brand2', 'style_preferences': 'casual,elegant'},
        {'id': 'user2', 'preferred_colors': 'red,white', 'preferred_brands': 'brand2,brand3', 'style_preferences': 'trendy,sporty'},
        {'id': 'user3', 'preferred_colors': 'black,gray', 'preferred_brands': 'brand1,brand3', 'style_preferences': 'classic,professional'},
    ]
    
    items = [
        {'id': 'prod1', 'name': 'Blue Casual Shirt', 'description': 'Comfortable casual shirt', 'category': 'tops', 'brand': 'brand1',
         'attributes': {'color': 'blue', 'material': 'cotton', 'style': 'casual'}},
        {'id': 'prod2', 'name': 'Red Sports Jacket', 'description': 'Sporty jacket', 'category': 'outerwear', 'brand': 'brand2',
         'attributes': {'color': 'red', 'material': 'polyester', 'style': 'sporty'}},
        {'id': 'prod3', 'name': 'Black Evening Gown', 'description': 'Elegant evening gown', 'category': 'dresses', 'brand': 'brand3',
         'attributes': {'color': 'black', 'material': 'silk', 'style': 'elegant'}},
    ]
    
    # Initialize and train the hybrid engine
    engine = HybridRecommendationEngine()
    await engine.train(interactions, users, items)
    
    # Get recommendations for a user
    recommendations = await engine.get_recommendations('user1', 5)
    print(f"Recommendations for user1:")
    for rec in recommendations:
        print(f"  {rec.product_id}: {rec.score:.3f} - {rec.reason}")
    
    print("\nSimilar items to prod1:")
    similar_items = await engine.get_similar_items('prod1', 3)
    for item in similar_items:
        print(f"  {item.product_id}: {item.score:.3f} - {item.reason}")

if __name__ == "__main__":
    asyncio.run(main())