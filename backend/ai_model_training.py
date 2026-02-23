# ai_model_training.py
# Training scripts for AI models used in Aetherstore Engine

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import os

logger = logging.getLogger(__name__)

class BodyMeasurementModelTrainer:
    """Train a model to predict body measurements from MediaPipe landmarks"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_dir = Path("ai_models")
        self.model_dir.mkdir(exist_ok=True)
    
    def create_model(self, input_dim: int = 132) -> keras.Model:
        """Create neural network model for measurement prediction"""
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dense(9, activation='linear')  # 9 measurements: chest, waist, hips, etc.
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_data(self, data_file: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from CSV file
        
        Expected CSV format:
        - Columns: landmark_x_0, landmark_y_0, ..., landmark_z_32, chest, waist, hips, ...
        - Rows: Each row is a training sample
        """
        df = pd.read_csv(data_file)
        
        # Separate features (landmarks) and targets (measurements)
        landmark_cols = [col for col in df.columns if col.startswith('landmark_')]
        measurement_cols = ['chest', 'waist', 'hips', 'shoulder_width', 
                           'arm_length', 'inseam', 'neck', 'bicep', 'height']
        
        X = df[landmark_cols].values
        y = df[measurement_cols].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def train(self, data_file: str, epochs: int = 100, batch_size: int = 32, 
              validation_split: float = 0.2):
        """Train the measurement prediction model"""
        logger.info(f"Loading training data from {data_file}")
        X, y = self.prepare_data(data_file)
        
        logger.info(f"Training on {len(X)} samples")
        
        # Create model
        self.model = self.create_model(input_dim=X.shape[1])
        
        # Train
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                keras.callbacks.ModelCheckpoint(
                    str(self.model_dir / "body_measurement_model_checkpoint.h5"),
                    save_best_only=True
                )
            ]
        )
        
        # Save final model
        model_path = self.model_dir / "body_measurement_model.h5"
        self.model.save(str(model_path))
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        scaler_path = self.model_dir / "body_measurement_scaler.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        return history
    
    def generate_sample_data(self, output_file: str, n_samples: int = 1000):
        """Generate sample training data for testing"""
        logger.info(f"Generating {n_samples} sample training records")
        
        # Generate synthetic MediaPipe landmarks (33 landmarks * 4 values = 132 features)
        n_features = 132
        data = []
        
        for i in range(n_samples):
            # Generate random landmarks (normalized 0-1)
            landmarks = np.random.rand(n_features)
            
            # Generate realistic measurements based on landmarks
            # This is simplified - real data would come from actual body scans
            chest = 80 + np.random.normal(0, 10)
            waist = 70 + np.random.normal(0, 10)
            hips = 90 + np.random.normal(0, 10)
            shoulder_width = 40 + np.random.normal(0, 5)
            arm_length = 60 + np.random.normal(0, 5)
            inseam = 75 + np.random.normal(0, 5)
            neck = 35 + np.random.normal(0, 3)
            bicep = 30 + np.random.normal(0, 3)
            height = 170 + np.random.normal(0, 10)
            
            row = list(landmarks) + [chest, waist, hips, shoulder_width, 
                                    arm_length, inseam, neck, bicep, height]
            data.append(row)
        
        # Create DataFrame
        landmark_cols = [f'landmark_{i}' for i in range(n_features)]
        measurement_cols = ['chest', 'waist', 'hips', 'shoulder_width', 
                           'arm_length', 'inseam', 'neck', 'bicep', 'height']
        df = pd.DataFrame(data, columns=landmark_cols + measurement_cols)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Sample data saved to {output_file}")
        return output_file

class FitPredictionModelTrainer:
    """Train a model to predict best fit size"""
    
    def __init__(self):
        self.model = None
        self.model_dir = Path("ai_models")
        self.model_dir.mkdir(exist_ok=True)
    
    def create_model(self, input_dim: int = 15) -> nn.Module:
        """Create PyTorch model for fit prediction"""
        class FitPredictionNet(nn.Module):
            def __init__(self, input_dim, num_sizes=5):
                super().__init__()
                self.fc1 = nn.Linear(input_dim, 128)
                self.fc2 = nn.Linear(128, 64)
                self.fc3 = nn.Linear(64, 32)
                self.fc4 = nn.Linear(32, num_sizes)
                self.relu = nn.ReLU()
                self.dropout = nn.Dropout(0.3)
            
            def forward(self, x):
                x = self.relu(self.fc1(x))
                x = self.dropout(x)
                x = self.relu(self.fc2(x))
                x = self.dropout(x)
                x = self.relu(self.fc3(x))
                x = self.fc4(x)
                return torch.softmax(x, dim=1)
        
        return FitPredictionNet(input_dim)
    
    def prepare_data(self, data_file: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Prepare training data
        
        Expected CSV format:
        - Features: user_chest, user_waist, user_hips, product_S_chest, product_S_waist, ...
        - Target: best_size (encoded as one-hot)
        """
        df = pd.read_csv(data_file)
        
        # Separate features and target
        feature_cols = [col for col in df.columns if col != 'best_size']
        X = df[feature_cols].values.astype(np.float32)
        
        # Encode sizes (S=0, M=1, L=2, XL=3, XXL=4)
        size_map = {'S': 0, 'M': 1, 'L': 2, 'XL': 3, 'XXL': 4}
        y = df['best_size'].map(size_map).values
        
        # Convert to tensors
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)
        
        return X_tensor, y_tensor
    
    def train(self, data_file: str, epochs: int = 100, batch_size: int = 32,
              learning_rate: float = 0.001):
        """Train the fit prediction model"""
        logger.info(f"Loading training data from {data_file}")
        X, y = self.prepare_data(data_file)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Create model
        self.model = self.create_model(input_dim=X.shape[1])
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        best_val_loss = float('inf')
        for epoch in range(epochs):
            # Training
            self.model.train()
            optimizer.zero_grad()
            outputs = self.model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = criterion(val_outputs, y_val)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                model_path = self.model_dir / "fit_prediction_model.pth"
                torch.save(self.model.state_dict(), str(model_path))
        
        logger.info(f"Training complete. Best model saved to {model_path}")
        return self.model

class StyleRecommendationTrainer:
    """Train collaborative filtering model for style recommendations"""
    
    def __init__(self):
        self.model = None
        self.model_dir = Path("ai_models")
        self.model_dir.mkdir(exist_ok=True)
    
    def train(self, interactions_file: str):
        """
        Train collaborative filtering model
        
        Expected CSV format:
        - user_id, product_id, rating (1-5), timestamp
        """
        from sklearn.decomposition import NMF
        from scipy.sparse import csr_matrix
        
        logger.info(f"Loading interactions from {interactions_file}")
        df = pd.read_csv(interactions_file)
        
        # Create user-item matrix
        user_ids = df['user_id'].unique()
        product_ids = df['product_id'].unique()
        
        user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
        product_to_idx = {pid: i for i, pid in enumerate(product_ids)}
        
        # Build sparse matrix
        rows = [user_to_idx[uid] for uid in df['user_id']]
        cols = [product_to_idx[pid] for pid in df['product_id']]
        values = df['rating'].values
        
        matrix = csr_matrix((values, (rows, cols)), shape=(len(user_ids), len(product_ids)))
        
        # Train NMF model
        logger.info("Training NMF model...")
        model = NMF(n_components=50, random_state=42, max_iter=1000)
        W = model.fit_transform(matrix)
        H = model.components_
        
        # Save model
        model_path = self.model_dir / "style_recommendation_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'W': W,
                'H': H,
                'user_to_idx': user_to_idx,
                'product_to_idx': product_to_idx,
                'user_ids': user_ids,
                'product_ids': product_ids
            }, f)
        
        logger.info(f"Model saved to {model_path}")
        return model

def train_all_models():
    """Train all AI models"""
    logger.info("Starting model training...")
    
    # Create sample data if it doesn't exist
    data_dir = Path("training_data")
    data_dir.mkdir(exist_ok=True)
    
    # Train body measurement model
    measurement_data = data_dir / "body_measurements.csv"
    if not measurement_data.exists():
        logger.info("Generating sample measurement data...")
        trainer = BodyMeasurementModelTrainer()
        trainer.generate_sample_data(str(measurement_data), n_samples=1000)
    
    trainer = BodyMeasurementModelTrainer()
    trainer.train(str(measurement_data), epochs=50)
    
    # Train fit prediction model
    fit_data = data_dir / "fit_predictions.csv"
    if not fit_data.exists():
        logger.warning(f"Fit prediction data not found: {fit_data}")
        logger.info("Skipping fit prediction training. Add data to train.")
    
    # Train style recommendation
    interactions_data = data_dir / "user_interactions.csv"
    if not interactions_data.exists():
        logger.warning(f"Interactions data not found: {interactions_data}")
        logger.info("Skipping recommendation training. Add data to train.")
    
    logger.info("Model training complete!")

if __name__ == "__main__":
    train_all_models()


