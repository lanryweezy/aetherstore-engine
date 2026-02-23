# asset_optimizer.py
# Asset Optimization Service for Aetherstore Engine

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import shutil

# Import our 3D processing service
from 3d_processing import ModelProcessor, OptimizationLevel, ProcessingResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetType(Enum):
    """Types of digital assets"""
    MODEL_3D = "model_3d"
    TEXTURE = "texture"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"

class CompressionFormat(Enum):
    """Supported compression formats"""
    GLB = "glb"          # GL Transmission Format (binary)
    DRACO = "draco"      # Google's Draco compression
    KTX2 = "ktx2"        # Khronos Texture 2
    WEBP = "webp"        # WebP image format
    MP4 = "mp4"          # H.264 video
    OPUS = "opus"        # Opus audio
    ZIP = "zip"          # Generic compression

@dataclass
class OptimizationSettings:
    """Settings for asset optimization"""
    target_format: str
    compression_level: str  # low, medium, high, ultra
    quality: int  # 1-100 for lossy formats
    max_resolution: Tuple[int, int]  # max width, height
    enable_mipmaps: bool
    optimize_for_web: bool
    preserve_original: bool

@dataclass
class AssetReport:
    """Report of asset optimization results"""
    asset_id: str
    original_size: int
    optimized_size: int
    compression_ratio: float
    processing_time: float
    savings_mb: float
    optimization_settings: OptimizationSettings
    processing_steps: List[str]
    warnings: List[str]
    errors: List[str]

class AssetOptimizer:
    """Service for optimizing digital assets for web delivery"""
    
    def __init__(self):
        """Initialize the asset optimizer"""
        self.model_processor = ModelProcessor()
        self.supported_extensions = {
            ".glb": AssetType.MODEL_3D,
            ".gltf": AssetType.MODEL_3D,
            ".fbx": AssetType.MODEL_3D,
            ".obj": AssetType.MODEL_3D,
            ".ply": AssetType.MODEL_3D,
            ".stl": AssetType.MODEL_3D,
            ".jpg": AssetType.IMAGE,
            ".jpeg": AssetType.IMAGE,
            ".png": AssetType.IMAGE,
            ".webp": AssetType.IMAGE,
            ".gif": AssetType.IMAGE,
            ".bmp": AssetType.IMAGE,
            ".tga": AssetType.IMAGE,
            ".mp4": AssetType.VIDEO,
            ".webm": AssetType.VIDEO,
            ".mov": AssetType.VIDEO,
            ".avi": AssetType.VIDEO,
            ".mp3": AssetType.AUDIO,
            ".wav": AssetType.AUDIO,
            ".ogg": AssetType.AUDIO,
            ".flac": AssetType.AUDIO,
            ".pdf": AssetType.DOCUMENT,
            ".doc": AssetType.DOCUMENT,
            ".docx": AssetType.DOCUMENT,
            ".txt": AssetType.DOCUMENT,
            ".json": AssetType.DOCUMENT,
            ".xml": AssetType.DOCUMENT
        }
        
        # Default optimization settings
        self.default_settings = {
            AssetType.MODEL_3D: OptimizationSettings(
                target_format="glb",
                compression_level="medium",
                quality=80,
                max_resolution=(2048, 2048),
                enable_mipmaps=True,
                optimize_for_web=True,
                preserve_original=True
            ),
            AssetType.IMAGE: OptimizationSettings(
                target_format="webp",
                compression_level="medium",
                quality=80,
                max_resolution=(2048, 2048),
                enable_mipmaps=False,
                optimize_for_web=True,
                preserve_original=True
            ),
            AssetType.VIDEO: OptimizationSettings(
                target_format="mp4",
                compression_level="medium",
                quality=70,
                max_resolution=(1920, 1080),
                enable_mipmaps=False,
                optimize_for_web=True,
                preserve_original=True
            ),
            AssetType.AUDIO: OptimizationSettings(
                target_format="opus",
                compression_level="medium",
                quality=60,
                max_resolution=(0, 0),  # Not applicable for audio
                enable_mipmaps=False,
                optimize_for_web=True,
                preserve_original=True
            )
        }
        
        logger.info("Asset Optimizer initialized")
    
    def get_asset_type(self, file_path: str) -> AssetType:
        """
        Determine the type of an asset based on its file extension
        
        Args:
            file_path: Path to the asset file
            
        Returns:
            Asset type
        """
        file_ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(file_ext, AssetType.OTHER)
    
    def optimize_asset(self, input_file: str, output_file: str, 
                      asset_type: Optional[AssetType] = None,
                      settings: Optional[OptimizationSettings] = None) -> AssetReport:
        """
        Optimize a digital asset for web delivery
        
        Args:
            input_file: Path to input asset
            output_file: Path for optimized output asset
            asset_type: Type of asset (auto-detected if not provided)
            settings: Optimization settings (defaults used if not provided)
            
        Returns:
            Asset optimization report
        """
        import time
        start_time = time.time()
        
        # Determine asset type if not provided
        if asset_type is None:
            asset_type = self.get_asset_type(input_file)
        
        # Use default settings if none provided
        if settings is None:
            settings = self.default_settings.get(asset_type, self.default_settings[AssetType.OTHER])
        
        # Get original file size
        original_size = os.path.getsize(input_file)
        
        # Initialize report data
        processing_steps = []
        warnings = []
        errors = []
        
        try:
            # Validate input file
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            processing_steps.append("validation")
            
            # Optimize based on asset type
            if asset_type == AssetType.MODEL_3D:
                result = self._optimize_3d_model(input_file, output_file, settings)
                processing_steps.extend(result.processing_steps)
                if not result.success:
                    errors.append(result.error_message or "3D model optimization failed")
            elif asset_type == AssetType.IMAGE:
                success = self._optimize_image(input_file, output_file, settings)
                processing_steps.append("image_optimization")
                if not success:
                    errors.append("Image optimization failed")
            elif asset_type == AssetType.VIDEO:
                success = self._optimize_video(input_file, output_file, settings)
                processing_steps.append("video_optimization")
                if not success:
                    errors.append("Video optimization failed")
            elif asset_type == AssetType.AUDIO:
                success = self._optimize_audio(input_file, output_file, settings)
                processing_steps.append("audio_optimization")
                if not success:
                    errors.append("Audio optimization failed")
            else:
                # For other asset types, just copy the file
                shutil.copy2(input_file, output_file)
                processing_steps.append("file_copy")
                warnings.append(f"No optimization available for {asset_type.value} assets")
            
            # Get optimized file size
            if os.path.exists(output_file):
                optimized_size = os.path.getsize(output_file)
                compression_ratio = optimized_size / original_size if original_size > 0 else 1.0
                savings_mb = (original_size - optimized_size) / (1024 * 1024)
            else:
                optimized_size = original_size
                compression_ratio = 1.0
                savings_mb = 0.0
            
            # Create asset report
            report = AssetReport(
                asset_id=self._generate_asset_id(input_file),
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                processing_time=time.time() - start_time,
                savings_mb=savings_mb,
                optimization_settings=settings,
                processing_steps=processing_steps,
                warnings=warnings,
                errors=errors
            )
            
            if not errors:
                logger.info(f"Asset optimization completed: {input_file} -> {output_file}")
            else:
                logger.warning(f"Asset optimization completed with errors: {input_file} -> {output_file}")
            
            return report
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = str(e)
            errors.append(f"Unexpected error: {error_msg}")
            
            # Try to copy original file as fallback
            try:
                if os.path.exists(input_file) and not os.path.exists(output_file):
                    shutil.copy2(input_file, output_file)
                    warnings.append("Original file copied as fallback")
            except Exception as copy_error:
                errors.append(f"Fallback copy failed: {str(copy_error)}")
            
            # Create error report
            report = AssetReport(
                asset_id=self._generate_asset_id(input_file),
                original_size=original_size if 'original_size' in locals() else 0,
                optimized_size=original_size if 'original_size' in locals() else 0,
                compression_ratio=1.0,
                processing_time=time.time() - start_time,
                savings_mb=0.0,
                optimization_settings=settings,
                processing_steps=processing_steps,
                warnings=warnings,
                errors=errors
            )
            
            logger.error(f"Asset optimization failed: {input_file} - {error_msg}")
            return report
    
    def _optimize_3d_model(self, input_file: str, output_file: str, 
                           settings: OptimizationSettings) -> ProcessingResult:
        """
        Optimize a 3D model using our 3D processing service
        
        Args:
            input_file: Path to input 3D model
            output_file: Path for optimized output model
            settings: Optimization settings
            
        Returns:
            Processing result
        """
        try:
            # Map compression level to optimization level
            level_map = {
                "low": OptimizationLevel.LOW,
                "medium": OptimizationLevel.MEDIUM,
                "high": OptimizationLevel.HIGH,
                "ultra": OptimizationLevel.ULTRA
            }
            
            optimization_level = level_map.get(settings.compression_level, OptimizationLevel.MEDIUM)
            
            # Use our 3D model processor
            result = self.model_processor.optimize_model(
                input_file, 
                output_file, 
                optimization_level
            )
            
            return result
            
        except Exception as e:
            logger.error(f"3D model optimization failed: {str(e)}")
            # Return error result
            return ProcessingResult(
                success=False,
                input_file=input_file,
                output_file=output_file,
                metadata=None,
                processing_steps=[],
                processing_time=0.0,
                error_message=str(e)
            )
    
    def _optimize_image(self, input_file: str, output_file: str, 
                        settings: OptimizationSettings) -> bool:
        """
        Optimize an image file
        
        Args:
            input_file: Path to input image
            output_file: Path for optimized output image
            settings: Optimization settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert quality setting to percentage
            quality = settings.quality
            
            # Parse resolution setting
            try:
                max_width, max_height = settings.max_resolution
            except:
                max_width, max_height = 2048, 2048
            
            # Use our 3D processor's texture processing (it handles images too)
            from 3d_processing import process_3d_texture
            success = process_3d_texture(
                input_file, 
                output_file, 
                quality=quality,
                resolution=f"{max_width}x{max_height}"
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            return False
    
    def _optimize_video(self, input_file: str, output_file: str, 
                        settings: OptimizationSettings) -> bool:
        """
        Optimize a video file (placeholder implementation)
        
        Args:
            input_file: Path to input video
            output_file: Path for optimized output video
            settings: Optimization settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would use FFmpeg or similar
            # For now, we'll just copy the file
            shutil.copy2(input_file, output_file)
            logger.warning("Video optimization not implemented - file copied as-is")
            return True
            
        except Exception as e:
            logger.error(f"Video optimization failed: {str(e)}")
            return False
    
    def _optimize_audio(self, input_file: str, output_file: str, 
                        settings: OptimizationSettings) -> bool:
        """
        Optimize an audio file (placeholder implementation)
        
        Args:
            input_file: Path to input audio
            output_file: Path for optimized output audio
            settings: Optimization settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, this would use audio processing libraries
            # For now, we'll just copy the file
            shutil.copy2(input_file, output_file)
            logger.warning("Audio optimization not implemented - file copied as-is")
            return True
            
        except Exception as e:
            logger.error(f"Audio optimization failed: {str(e)}")
            return False
    
    def batch_optimize(self, assets: List[Dict[str, str]], 
                      output_directory: str,
                      asset_types: Optional[List[AssetType]] = None,
                      settings: Optional[Dict[AssetType, OptimizationSettings]] = None) -> List[AssetReport]:
        """
        Optimize multiple assets in batch
        
        Args:
            assets: List of asset dictionaries with 'input_file' and 'output_file' keys
            output_directory: Directory for optimized assets
            asset_types: Types of assets to optimize (all if None)
            settings: Settings for each asset type (defaults used if None)
            
        Returns:
            List of optimization reports
        """
        reports = []
        
        for asset in assets:
            try:
                input_file = asset.get("input_file")
                output_file = asset.get("output_file") or os.path.join(
                    output_directory, 
                    os.path.basename(input_file)
                )
                
                # Determine asset type
                asset_type = self.get_asset_type(input_file)
                
                # Skip if not in specified types
                if asset_types and asset_type not in asset_types:
                    continue
                
                # Get settings for this asset type
                asset_settings = None
                if settings:
                    asset_settings = settings.get(asset_type)
                
                # Optimize the asset
                report = self.optimize_asset(input_file, output_file, asset_type, asset_settings)
                reports.append(report)
                
            except Exception as e:
                logger.error(f"Batch optimization failed for {asset}: {str(e)}")
                # Add error report
                reports.append(AssetReport(
                    asset_id=self._generate_asset_id(asset.get("input_file", "unknown")),
                    original_size=0,
                    optimized_size=0,
                    compression_ratio=1.0,
                    processing_time=0.0,
                    savings_mb=0.0,
                    optimization_settings=asset_settings or OptimizationSettings(
                        target_format="", compression_level="", quality=0,
                        max_resolution=(0,0), enable_mipmaps=False,
                        optimize_for_web=False, preserve_original=False
                    ),
                    processing_steps=[],
                    warnings=[],
                    errors=[str(e)]
                ))
        
        logger.info(f"Batch optimization completed for {len(reports)} assets")
        return reports
    
    def _generate_asset_id(self, file_path: str) -> str:
        """
        Generate a unique ID for an asset based on its file path
        
        Args:
            file_path: Path to the asset file
            
        Returns:
            Unique asset ID
        """
        # Create a hash of the file path and modification time
        try:
            mtime = os.path.getmtime(file_path)
            file_info = f"{file_path}:{mtime}".encode('utf-8')
            return hashlib.md5(file_info).hexdigest()
        except:
            # Fallback to random UUID if file info unavailable
            import uuid
            return str(uuid.uuid4())
    
    def get_optimization_savings(self, reports: List[AssetReport]) -> Dict[str, float]:
        """
        Calculate total savings from asset optimization
        
        Args:
            reports: List of asset optimization reports
            
        Returns:
            Dictionary with savings statistics
        """
        total_original = sum(report.original_size for report in reports)
        total_optimized = sum(report.optimized_size for report in reports)
        total_savings = sum(report.savings_mb for report in reports)
        
        if total_original > 0:
            compression_ratio = total_optimized / total_original
        else:
            compression_ratio = 1.0
        
        return {
            "total_original_mb": total_original / (1024 * 1024),
            "total_optimized_mb": total_optimized / (1024 * 1024),
            "total_savings_mb": total_savings,
            "average_compression_ratio": compression_ratio,
            "processed_assets": len(reports)
        }

# Global asset optimizer instance
asset_optimizer = AssetOptimizer()

# Convenience functions
def optimize_single_asset(input_file: str, output_file: str, 
                         asset_type: Optional[AssetType] = None,
                         settings: Optional[OptimizationSettings] = None) -> AssetReport:
    """Optimize a single asset"""
    return asset_optimizer.optimize_asset(input_file, output_file, asset_type, settings)

def optimize_batch(assets: List[Dict[str, str]], 
                  output_directory: str,
                  asset_types: Optional[List[AssetType]] = None,
                  settings: Optional[Dict[AssetType, OptimizationSettings]] = None) -> List[AssetReport]:
    """Optimize multiple assets in batch"""
    return asset_optimizer.batch_optimize(assets, output_directory, asset_types, settings)

def get_asset_savings_statistics(reports: List[AssetReport]) -> Dict[str, float]:
    """Calculate total savings from optimization"""
    return asset_optimizer.get_optimization_savings(reports)

if __name__ == "__main__":
    print("Aetherstore Engine Asset Optimizer")
    print("===================================")
    print("Asset optimizer initialized and ready for use.")