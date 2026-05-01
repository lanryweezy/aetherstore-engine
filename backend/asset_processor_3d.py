# 3d_processing.py
# 3D Model Processing Service for Aetherstore Engine

import os
import json
import numpy as np
import trimesh
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import trimesh
import PIL.Image as Image
from blender_processor import blender_processor
from gltf_processor import gltf_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessingStep(Enum):
    """Steps in the 3D processing pipeline"""
    VALIDATION = "validation"
    DECOMPRESSION = "decompression"
    CLEANING = "cleaning"
    OPTIMIZATION = "optimization"
    COMPRESSION = "compression"
    TEXTURE_PROCESSING = "texture_processing"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    METADATA_EXTRACTION = "metadata_extraction"

class OptimizationLevel(Enum):
    """Levels of optimization for 3D models"""
    LOW = "low"      # Minimal optimization
    MEDIUM = "medium" # Balanced optimization
    HIGH = "high"    # Aggressive optimization
    ULTRA = "ultra"  # Maximum optimization

@dataclass
class ModelMetadata:
    """Metadata extracted from a 3D model"""
    vertex_count: int
    face_count: int
    triangle_count: int
    bounding_box: Dict[str, List[float]]
    center: List[float]
    dimensions: Dict[str, float]
    texture_count: int
    material_count: int
    animation_clips: int
    file_size: int
    processing_time: float

@dataclass
class ProcessingResult:
    """Result of 3D model processing"""
    success: bool
    input_file: str
    output_file: str
    metadata: ModelMetadata
    processing_steps: List[ProcessingStep]
    processing_time: float
    error_message: Optional[str] = None
    warnings: List[str] = None

class ModelProcessor:
    """Service for processing and optimizing 3D models"""
    
    def __init__(self):
        """Initialize the model processor"""
        self.supported_formats = [".glb", ".gltf", ".obj", ".fbx", ".ply", ".stl"]
        self.optimization_levels = {
            OptimizationLevel.LOW: {"decimation_ratio": 0.9, "texture_quality": 90},
            OptimizationLevel.MEDIUM: {"decimation_ratio": 0.7, "texture_quality": 70},
            OptimizationLevel.HIGH: {"decimation_ratio": 0.5, "texture_quality": 50},
            OptimizationLevel.ULTRA: {"decimation_ratio": 0.3, "texture_quality": 30}
        }
        
        logger.info("Model Processor initialized")
    
    def validate_model(self, file_path: str) -> bool:
        """
        Validate that a file is a valid 3D model
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                logger.warning(f"Unsupported file format: {file_ext}")
                return False
            
            # Check file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Try to load the model to verify it's valid
            mesh = trimesh.load(file_path, force='mesh')
            if mesh is None:
                logger.error(f"Could not load mesh from {file_path}")
                return False
            
            logger.info(f"Model validation passed for {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed for {file_path}: {str(e)}")
            return False
    
    def extract_metadata(self, file_path: str) -> ModelMetadata:
        """
        Extract metadata from a 3D model
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            Model metadata
        """
        try:
            # Load the model
            mesh = trimesh.load(file_path, force='mesh')
            
            # Get basic mesh information
            vertex_count = len(mesh.vertices)
            face_count = len(mesh.faces)
            triangle_count = face_count  # Simplified assumption
            
            # Calculate bounding box and dimensions
            bounds = mesh.bounds
            bbox = {
                "min": bounds[0].tolist(),
                "max": bounds[1].tolist()
            }
            
            center = ((bounds[0] + bounds[1]) / 2).tolist()
            dimensions = {
                "width": float(bounds[1][0] - bounds[0][0]),
                "height": float(bounds[1][1] - bounds[0][1]),
                "depth": float(bounds[1][2] - bounds[0][2])
            }
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create metadata object
            metadata = ModelMetadata(
                vertex_count=vertex_count,
                face_count=face_count,
                triangle_count=triangle_count,
                bounding_box=bbox,
                center=center,
                dimensions=dimensions,
                texture_count=0,  # Would be extracted from materials
                material_count=0,  # Would be extracted from mesh
                animation_clips=0,  # Would be extracted from model
                file_size=file_size,
                processing_time=0.0
            )
            
            logger.info(f"Extracted metadata for {file_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed for {file_path}: {str(e)}")
            raise
    
    def optimize_model(self, input_file: str, output_file: str, 
                       optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM) -> ProcessingResult:
        """
        Optimize a 3D model for web delivery
        
        Args:
            input_file: Path to input 3D model
            output_file: Path for optimized output model
            optimization_level: Level of optimization to apply
            
        Returns:
            Processing result
        """
        import time
        start_time = time.time()
        
        try:
            # Validate input file
            if not self.validate_model(input_file):
                return ProcessingResult(
                    success=False,
                    input_file=input_file,
                    output_file=output_file,
                    metadata=None,
                    processing_steps=[ProcessingStep.VALIDATION],
                    processing_time=time.time() - start_time,
                    error_message="Invalid input model"
                )
            
            completed_steps = [ProcessingStep.VALIDATION]
            params = self.optimization_levels[optimization_level]
            
            use_fallback = True
            if gltf_processor.is_available():
                logger.info("Using gltf-transform for optimization")
                # This is extremely fast and handles PBR materials seamlessly
                success = gltf_processor.optimize_model(input_file, output_file)
                if success:
                    completed_steps.extend([
                        ProcessingStep.DECOMPRESSION,
                        ProcessingStep.CLEANING,
                        ProcessingStep.OPTIMIZATION,
                        ProcessingStep.COMPRESSION
                    ])
                    use_fallback = False
                else:
                    logger.warning("gltf-transform optimization failed. Falling back.")

            if use_fallback and blender_processor.is_blender_available():
                logger.info("Using Blender for optimization")
                # Optimize using Blender
                success = blender_processor.optimize_model(input_file, output_file, params["decimation_ratio"])
                if success:
                    completed_steps.extend([
                        ProcessingStep.DECOMPRESSION,
                        ProcessingStep.CLEANING,
                        ProcessingStep.OPTIMIZATION,
                        ProcessingStep.COMPRESSION
                    ])
                    use_fallback = False
                else:
                    logger.warning("Blender optimization failed. Falling back to Trimesh.")

            if use_fallback:
                logger.info("Using Trimesh for optimization")
                # Load the model
                mesh = trimesh.load(input_file, force='mesh')
                completed_steps.append(ProcessingStep.DECOMPRESSION)

                # Clean the mesh
                mesh = self._clean_mesh(mesh)
                completed_steps.append(ProcessingStep.CLEANING)

                # Optimize the mesh
                mesh = self._optimize_mesh(mesh, params["decimation_ratio"])
                completed_steps.append(ProcessingStep.OPTIMIZATION)

                # Process textures
                # This would involve texture compression and optimization
                completed_steps.append(ProcessingStep.TEXTURE_PROCESSING)

                # Save optimized model
                mesh.export(output_file)
                completed_steps.append(ProcessingStep.COMPRESSION)
            
            # Extract metadata
            metadata = self.extract_metadata(output_file)
            metadata.processing_time = time.time() - start_time
            completed_steps.append(ProcessingStep.METADATA_EXTRACTION)
            
            # Skip Backend Thumbnail generation as it will be handled by the frontend
            logger.info(f"Skipping backend thumbnail generation for {input_file} - now handled by frontend")
            
            result = ProcessingResult(
                success=True,
                input_file=input_file,
                output_file=output_file,
                metadata=metadata,
                processing_steps=completed_steps,
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Model optimization completed for {input_file}")
            return result
            
        except Exception as e:
            logger.error(f"Model optimization failed for {input_file}: {str(e)}")
            return ProcessingResult(
                success=False,
                input_file=input_file,
                output_file=output_file,
                metadata=None,
                processing_steps=completed_steps,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _clean_mesh(self, mesh) -> trimesh.Trimesh:
        """
        Clean a mesh by removing artifacts and fixing issues
        
        Args:
            mesh: Trimesh object to clean
            
        Returns:
            Cleaned mesh
        """
        try:
            # Remove duplicate vertices
            mesh.remove_duplicate_vertices()
            
            # Remove degenerate faces
            mesh.remove_degenerate_faces()
            
            # Fix winding and normals
            mesh.fix_normals()
            
            # Remove disconnected components (keep largest)
            if hasattr(mesh, 'split'):
                components = mesh.split()
                if len(components) > 1:
                    # Keep the largest component
                    largest_component = max(components, key=lambda m: len(m.vertices))
                    mesh = largest_component
            
            logger.debug("Mesh cleaning completed")
            return mesh
            
        except Exception as e:
            logger.warning(f"Mesh cleaning failed: {str(e)}")
            return mesh  # Return original mesh if cleaning fails
    
    def _optimize_mesh(self, mesh, decimation_ratio: float) -> trimesh.Trimesh:
        """
        Optimize a mesh by reducing polygon count
        
        Args:
            mesh: Trimesh object to optimize
            decimation_ratio: Ratio of faces to keep (0.0-1.0)
            
        Returns:
            Optimized mesh
        """
        try:
            original_face_count = len(mesh.faces)
            target_face_count = int(original_face_count * decimation_ratio)
            
            if target_face_count < original_face_count:
                # Simplify the mesh
                simplified_mesh = mesh.simplify_quadratic_decimation(target_face_count)
                logger.debug(f"Mesh simplified from {original_face_count} to {len(simplified_mesh.faces)} faces")
                return simplified_mesh
            else:
                logger.debug("No mesh simplification needed")
                return mesh
                
        except Exception as e:
            logger.warning(f"Mesh optimization failed: {str(e)}")
            return mesh  # Return original mesh if optimization fails
    
    def _generate_thumbnails(self, model_file: str) -> List[str]:
        """
        Generate thumbnails for a 3D model.
        Uses Blender if available, otherwise falls back to trimesh wireframes.
        """
        try:
            base_name = Path(model_file).stem
            thumb_dir = Path(model_file).parent / "thumbnails"
            thumb_dir.mkdir(exist_ok=True)
            thumbnails = []

            views = ["front", "side", "top", "iso"]

            if blender_processor.is_blender_available():
                logger.info(f"Using Blender to render thumbnails for {model_file}")
                success = blender_processor.render_thumbnails(model_file, str(thumb_dir))
                if success:
                    for view_name in views:
                        thumb_path = thumb_dir / f"{base_name}_{view_name}.png"
                        if thumb_path.exists():
                            thumbnails.append(str(thumb_path))
                    logger.info(f"Generated {len(thumbnails)} rendered thumbnails for {model_file}")
                    return thumbnails
                else:
                    logger.warning("Blender thumbnail rendering failed. Falling back to wireframes.")

            logger.info(f"Using Trimesh to generate wireframe thumbnails for {model_file}")
            from PIL import ImageDraw
            mesh = trimesh.load(model_file, force='mesh')

            # Rotation angles for different views
            views_rotations = {
                "front": [0, 0, 0],
                "side": [0, np.pi/2, 0],
                "top": [np.pi/2, 0, 0],
                "iso": [np.pi/4, np.pi/4, 0]
            }

            for view_name, rotation in views_rotations.items():
                thumb_path = thumb_dir / f"{base_name}_{view_name}.png"

                # Create canvas
                img = Image.new('RGB', (512, 512), color=(245, 245, 245))
                draw = ImageDraw.Draw(img)

                # Copy and rotate mesh for projection
                temp_mesh = mesh.copy()
                if any(rotation):
                    transform = trimesh.transformations.euler_matrix(*rotation)
                    temp_mesh.apply_transform(transform)

                # Project vertices to 2D (XY plane)
                vertices_2d = temp_mesh.vertices[:, :2]
                
                # Normalize to fit 512x512 with padding
                v_min, v_max = vertices_2d.min(axis=0), vertices_2d.max(axis=0)
                scale = 400 / max(v_max - v_min)
                offset = (v_max + v_min) / 2

                points = (vertices_2d - offset) * scale + 256

                # Draw wireframe (sampled edges for performance)
                edges = temp_mesh.edges_unique
                sample_rate = max(1, len(edges) // 2000) # Draw up to 2000 edges
                for edge in edges[::sample_rate]:
                    p1, p2 = points[edge[0]], points[edge[1]]
                    draw.line([p1[0], p1[1], p2[0], p2[1]], fill=(100, 100, 100), width=1)

                img.save(thumb_path, 'PNG')
                thumbnails.append(str(thumb_path))
            
            logger.info(f"Generated {len(thumbnails)} wireframe thumbnails for {model_file}")
            return thumbnails
            
        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {str(e)}. Falling back to basic placeholder.")
            return self._generate_basic_placeholders(model_file)

    def _generate_basic_placeholders(self, model_file: str) -> List[str]:
        """Fallback method for simple placeholders"""
        thumbnails = []
        base_name = Path(model_file).stem
        thumb_dir = Path(model_file).parent / "thumbnails"
        thumb_dir.mkdir(exist_ok=True)
        for view in ["front", "side", "top"]:
            thumb_path = thumb_dir / f"{base_name}_{view}.jpg"
            img = Image.new('RGB', (256, 256), color=(73, 109, 137))
            img.save(thumb_path)
            thumbnails.append(str(thumb_path))
        return thumbnails
    
    def process_texture(self, input_file: str, output_file: str, 
                       quality: int = 80, resolution: str = "1024x1024") -> bool:
        """
        Process and optimize a texture image
        
        Args:
            input_file: Path to input texture
            output_file: Path for processed texture
            quality: JPEG/WebP quality (1-100)
            resolution: Target resolution (e.g., "1024x1024")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input file
            if not os.path.exists(input_file):
                logger.error(f"Texture file not found: {input_file}")
                return False
            
            # Load texture
            img = Image.open(input_file)
            
            # Parse resolution
            try:
                width, height = map(int, resolution.lower().replace('x', ' ').split())
            except:
                width, height = 1024, 1024  # Default resolution
            
            # Resize image
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save with compression
            if output_file.lower().endswith('.webp'):
                img.save(output_file, 'WEBP', quality=quality)
            else:
                img.save(output_file, 'JPEG', quality=quality)
            
            logger.info(f"Texture processed: {input_file} -> {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Texture processing failed: {str(e)}")
            return False
    
    def analyze_model_complexity(self, file_path: str) -> Dict:
        """
        Analyze the complexity of a 3D model
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            Complexity analysis
        """
        try:
            # Load the model
            mesh = trimesh.load(file_path, force='mesh')
            
            # Get basic metrics
            vertex_count = len(mesh.vertices)
            face_count = len(mesh.faces)
            
            # Calculate surface area
            surface_area = mesh.area
            
            # Calculate volume (if watertight)
            volume = mesh.volume if mesh.is_watertight else 0
            
            # Estimate complexity score (0-100)
            complexity_score = min(100, (vertex_count / 10000) + (face_count / 5000))
            
            # Determine recommended optimization level
            if complexity_score < 30:
                recommended_level = OptimizationLevel.LOW
            elif complexity_score < 60:
                recommended_level = OptimizationLevel.MEDIUM
            elif complexity_score < 80:
                recommended_level = OptimizationLevel.HIGH
            else:
                recommended_level = OptimizationLevel.ULTRA
            
            analysis = {
                "vertex_count": vertex_count,
                "face_count": face_count,
                "surface_area": surface_area,
                "volume": volume,
                "complexity_score": round(complexity_score, 2),
                "recommended_optimization_level": recommended_level.value,
                "estimated_webgl_performance": self._estimate_webgl_performance(vertex_count, face_count)
            }
            
            logger.info(f"Complexity analysis completed for {file_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Complexity analysis failed for {file_path}: {str(e)}")
            raise
    
    def _estimate_webgl_performance(self, vertex_count: int, face_count: int) -> str:
        """
        Estimate WebGL performance based on model complexity
        
        Args:
            vertex_count: Number of vertices
            face_count: Number of faces
            
        Returns:
            Performance estimate
        """
        total_complexity = vertex_count + face_count
        
        if total_complexity < 50000:
            return "excellent"
        elif total_complexity < 100000:
            return "good"
        elif total_complexity < 200000:
            return "fair"
        else:
            return "poor"

# Global model processor instance
model_processor = ModelProcessor()

# Convenience functions
def validate_3d_model(file_path: str) -> bool:
    """Validate a 3D model file"""
    return model_processor.validate_model(file_path)

def optimize_3d_model(input_file: str, output_file: str, 
                     optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM) -> ProcessingResult:
    """Optimize a 3D model"""
    return model_processor.optimize_model(input_file, output_file, optimization_level)

def process_3d_texture(input_file: str, output_file: str, quality: int = 80, 
                      resolution: str = "1024x1024") -> bool:
    """Process a 3D texture"""
    return model_processor.process_texture(input_file, output_file, quality, resolution)

def analyze_model_complexity(file_path: str) -> Dict:
    """Analyze model complexity"""
    return model_processor.analyze_model_complexity(file_path)

if __name__ == "__main__":
    print("Aetherstore Engine 3D Model Processor")
    print("====================================")
    print("Model processor initialized and ready for use.")