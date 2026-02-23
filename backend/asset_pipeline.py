# asset_pipeline.py
# 3D Asset Pipeline for Aetherstore Engine

import os
import uuid
import json
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetType(Enum):
    """Types of 3D assets supported by the pipeline"""
    MODEL_3D = "model_3d"
    TEXTURE = "texture"
    ANIMATION = "animation"
    SCAN = "scan"
    AVATAR = "avatar"
    ENVIRONMENT = "environment"

class AssetStatus(Enum):
    """Status of assets in the pipeline"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    OPTIMIZING = "optimizing"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"

class CompressionLevel(Enum):
    """Compression levels for 3D assets"""
    LOW = "low"      # Fast processing, larger files
    MEDIUM = "medium" # Balanced processing and size
    HIGH = "high"    # Slower processing, smaller files
    ULTRA = "ultra"  # Slowest processing, smallest files

class TextureFormat(Enum):
    """Supported texture formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    DDS = "dds"
    KTX2 = "ktx2"

class ModelFormat(Enum):
    """Supported 3D model formats"""
    GLB = "glb"
    GLTF = "gltf"
    FBX = "fbx"
    OBJ = "obj"
    USDZ = "usdz"

class AssetPipeline:
    """Main 3D Asset Pipeline for processing and optimizing 3D assets"""
    
    def __init__(self, base_storage_path: str = "assets", temp_path: str = "temp"):
        """
        Initialize the asset pipeline
        
        Args:
            base_storage_path: Base path for storing processed assets
            temp_path: Temporary path for processing files
        """
        self.base_storage_path = Path(base_storage_path)
        self.temp_path = Path(temp_path)
        
        # Create directories if they don't exist
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Supported formats
        self.supported_model_formats = [fmt.value for fmt in ModelFormat]
        self.supported_texture_formats = [fmt.value for fmt in TextureFormat]
        
        # Processing configuration
        self.default_compression = CompressionLevel.MEDIUM
        self.default_texture_quality = 80  # JPEG/WebP quality (1-100)
        self.max_polygon_count = 100000
        self.texture_resolution = "4k"  # 4k, 2k, 1k, 512, 256
        
        logger.info("Asset Pipeline initialized")
    
    def process_uploaded_asset(self, file_path: str, asset_type: AssetType, 
                              user_id: str, metadata: Dict = None) -> Dict:
        """
        Process an uploaded asset through the pipeline
        
        Args:
            file_path: Path to the uploaded file
            asset_type: Type of asset being processed
            user_id: ID of user who uploaded the asset
            metadata: Additional metadata for the asset
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Generate asset ID
            asset_id = str(uuid.uuid4())
            
            # Create asset record
            asset_record = {
                "id": asset_id,
                "user_id": user_id,
                "asset_type": asset_type.value,
                "original_file_path": file_path,
                "status": AssetStatus.UPLOADING.value,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "processing_log": []
            }
            
            # Update status
            asset_record["status"] = AssetStatus.PROCESSING.value
            asset_record["processing_log"].append({
                "timestamp": datetime.now().isoformat(),
                "status": AssetStatus.PROCESSING.value,
                "message": "Asset processing started"
            })
            
            # Process based on asset type
            if asset_type == AssetType.MODEL_3D:
                result = self._process_3d_model(file_path, asset_record)
            elif asset_type == AssetType.TEXTURE:
                result = self._process_texture(file_path, asset_record)
            elif asset_type == AssetType.SCAN:
                result = self._process_scan(file_path, asset_record)
            elif asset_type == AssetType.AVATAR:
                result = self._process_avatar(file_path, asset_record)
            else:
                result = self._process_generic_asset(file_path, asset_record)
            
            # Finalize processing
            result["status"] = AssetStatus.READY.value
            result["processing_log"].append({
                "timestamp": datetime.now().isoformat(),
                "status": AssetStatus.READY.value,
                "message": "Asset processing completed successfully"
            })
            
            logger.info(f"Asset {asset_id} processed successfully")
            return result
            
        except Exception as e:
            error_result = {
                "id": asset_id if 'asset_id' in locals() else "unknown",
                "status": AssetStatus.ERROR.value,
                "error": str(e),
                "processing_log": [{
                    "timestamp": datetime.now().isoformat(),
                    "status": AssetStatus.ERROR.value,
                    "message": f"Processing failed: {str(e)}"
                }]
            }
            logger.error(f"Asset processing failed: {str(e)}")
            return error_result
    
    def _process_3d_model(self, file_path: str, asset_record: Dict) -> Dict:
        """
        Process a 3D model file
        
        Args:
            file_path: Path to the 3D model file
            asset_record: Asset record dictionary
            
        Returns:
            Processed asset information
        """
        try:
            # Validate file format
            file_ext = Path(file_path).suffix.lower()[1:]  # Remove the dot
            if file_ext not in self.supported_model_formats:
                raise ValueError(f"Unsupported model format: {file_ext}")
            
            # Extract file information
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            
            # Create processing directory
            processing_dir = self.temp_path / f"processing_{asset_record['id']}"
            processing_dir.mkdir(exist_ok=True)
            
            # Copy file to processing directory
            temp_file_path = processing_dir / file_name
            shutil.copy2(file_path, temp_file_path)
            
            # Analyze model
            model_info = self._analyze_3d_model(str(temp_file_path))
            
            # Optimize model if needed
            if model_info["polygon_count"] > self.max_polygon_count:
                optimized_path = self._optimize_3d_model(
                    str(temp_file_path), 
                    self.default_compression
                )
                model_info["optimized"] = True
                model_info["original_polygon_count"] = model_info["polygon_count"]
                model_info["polygon_count"] = self._count_polygons(optimized_path)
            else:
                optimized_path = str(temp_file_path)
                model_info["optimized"] = False
            
            # Generate thumbnails
            thumbnail_paths = self._generate_model_thumbnails(optimized_path)
            
            # Move processed file to storage
            final_path = self._move_to_storage(
                optimized_path, 
                asset_record["user_id"], 
                asset_record["id"],
                f"model_{Path(optimized_path).stem}"
            )
            
            # Create asset result
            result = {
                **asset_record,
                "file_url": final_path,
                "file_name": Path(final_path).name,
                "file_size": os.path.getsize(final_path),
                "mime_type": self._get_mime_type(file_ext),
                "dimensions": model_info,
                "thumbnails": thumbnail_paths,
                "processing_steps": ["validation", "analysis", "optimization", "storage"]
            }
            
            # Clean up temporary files
            shutil.rmtree(processing_dir, ignore_errors=True)
            
            return result
            
        except Exception as e:
            raise Exception(f"3D model processing failed: {str(e)}")
    
    def _process_texture(self, file_path: str, asset_record: Dict) -> Dict:
        """
        Process a texture file
        
        Args:
            file_path: Path to the texture file
            asset_record: Asset record dictionary
            
        Returns:
            Processed asset information
        """
        try:
            # Validate file format
            file_ext = Path(file_path).suffix.lower()[1:]
            if file_ext not in self.supported_texture_formats:
                raise ValueError(f"Unsupported texture format: {file_ext}")
            
            # Extract file information
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            
            # Create processing directory
            processing_dir = self.temp_path / f"processing_{asset_record['id']}"
            processing_dir.mkdir(exist_ok=True)
            
            # Copy file to processing directory
            temp_file_path = processing_dir / file_name
            shutil.copy2(file_path, temp_file_path)
            
            # Optimize texture
            optimized_path = self._optimize_texture(
                str(temp_file_path),
                self.default_texture_quality,
                self.texture_resolution
            )
            
            # Generate thumbnails
            thumbnail_paths = self._generate_texture_thumbnails(optimized_path)
            
            # Move processed file to storage
            final_path = self._move_to_storage(
                optimized_path,
                asset_record["user_id"],
                asset_record["id"],
                f"texture_{Path(optimized_path).stem}"
            )
            
            # Get texture dimensions
            texture_info = self._analyze_texture(optimized_path)
            
            # Create asset result
            result = {
                **asset_record,
                "file_url": final_path,
                "file_name": Path(final_path).name,
                "file_size": os.path.getsize(final_path),
                "mime_type": self._get_mime_type(file_ext),
                "dimensions": texture_info,
                "thumbnails": thumbnail_paths,
                "processing_steps": ["validation", "optimization", "storage"]
            }
            
            # Clean up temporary files
            shutil.rmtree(processing_dir, ignore_errors=True)
            
            return result
            
        except Exception as e:
            raise Exception(f"Texture processing failed: {str(e)}")
    
    def _process_scan(self, file_path: str, asset_record: Dict) -> Dict:
        """
        Process a 3D scan file
        
        Args:
            file_path: Path to the scan file
            asset_record: Asset record dictionary
            
        Returns:
            Processed asset information
        """
        try:
            # Validate file format (allow various formats for scans)
            file_ext = Path(file_path).suffix.lower()[1:]
            
            # Extract file information
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            
            # Create processing directory
            processing_dir = self.temp_path / f"processing_{asset_record['id']}"
            processing_dir.mkdir(exist_ok=True)
            
            # Copy file to processing directory
            temp_file_path = processing_dir / file_name
            shutil.copy2(file_path, temp_file_path)
            
            # Process scan (this would involve more complex operations in a real implementation)
            processed_scan_path = self._process_3d_scan(str(temp_file_path))
            
            # Generate preview
            preview_path = self._generate_scan_preview(processed_scan_path)
            
            # Move processed file to storage
            final_path = self._move_to_storage(
                processed_scan_path,
                asset_record["user_id"],
                asset_record["id"],
                f"scan_{Path(processed_scan_path).stem}"
            )
            
            # Create asset result
            result = {
                **asset_record,
                "file_url": final_path,
                "file_name": Path(final_path).name,
                "file_size": os.path.getsize(final_path),
                "mime_type": self._get_mime_type(file_ext),
                "preview_url": preview_path,
                "processing_steps": ["validation", "processing", "preview_generation", "storage"]
            }
            
            # Clean up temporary files
            shutil.rmtree(processing_dir, ignore_errors=True)
            
            return result
            
        except Exception as e:
            raise Exception(f"Scan processing failed: {str(e)}")
    
    def _process_avatar(self, file_path: str, asset_record: Dict) -> Dict:
        """
        Process an avatar file
        
        Args:
            file_path: Path to the avatar file
            asset_record: Asset record dictionary
            
        Returns:
            Processed asset information
        """
        # Avatar processing would involve specific optimizations for human models
        # For now, we'll treat it similarly to 3D model processing
        return self._process_3d_model(file_path, asset_record)
    
    def _process_generic_asset(self, file_path: str, asset_record: Dict) -> Dict:
        """
        Process a generic asset file
        
        Args:
            file_path: Path to the asset file
            asset_record: Asset record dictionary
            
        Returns:
            Processed asset information
        """
        try:
            # Extract file information
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()[1:]
            
            # Move file to storage without processing
            final_path = self._move_to_storage(
                file_path,
                asset_record["user_id"],
                asset_record["id"],
                f"asset_{Path(file_path).stem}"
            )
            
            # Create asset result
            result = {
                **asset_record,
                "file_url": final_path,
                "file_name": Path(final_path).name,
                "file_size": os.path.getsize(final_path),
                "mime_type": self._get_mime_type(file_ext),
                "processing_steps": ["validation", "storage"]
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Generic asset processing failed: {str(e)}")
    
    def _analyze_3d_model(self, file_path: str) -> Dict:
        """
        Analyze a 3D model to extract metadata
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            Dictionary with model information
        """
        # In a real implementation, this would use 3D processing libraries
        # For now, we'll return mock data
        return {
            "polygon_count": 50000,
            "vertex_count": 25000,
            "texture_count": 3,
            "material_count": 2,
            "animation_clips": 0,
            "bounding_box": {
                "min": [-1.0, -1.0, -1.0],
                "max": [1.0, 1.0, 1.0]
            },
            "center": [0.0, 0.0, 0.0],
            "dimensions": {
                "width": 2.0,
                "height": 2.0,
                "depth": 2.0
            }
        }
    
    def _optimize_3d_model(self, file_path: str, compression_level: CompressionLevel) -> str:
        """
        Optimize a 3D model for web delivery
        
        Args:
            file_path: Path to the 3D model file
            compression_level: Level of compression to apply
            
        Returns:
            Path to the optimized model file
        """
        # In a real implementation, this would use tools like:
        # - Draco compression for geometry
        # - Texture compression
        # - Mesh decimation for polygon reduction
        # - Animation optimization
        
        # For now, we'll just return the original file path
        return file_path
    
    def _count_polygons(self, file_path: str) -> int:
        """
        Count polygons in a 3D model
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            Number of polygons
        """
        # In a real implementation, this would parse the model file
        # For now, we'll return a mock value
        return 50000
    
    def _generate_model_thumbnails(self, file_path: str) -> List[str]:
        """
        Generate thumbnails for a 3D model
        
        Args:
            file_path: Path to the 3D model file
            
        Returns:
            List of thumbnail file paths
        """
        # In a real implementation, this would render the model from different angles
        # For now, we'll return mock thumbnail paths
        return [
            f"{file_path}_thumb_0.jpg",
            f"{file_path}_thumb_45.jpg",
            f"{file_path}_thumb_90.jpg"
        ]
    
    def _optimize_texture(self, file_path: str, quality: int, resolution: str) -> str:
        """
        Optimize a texture for web delivery
        
        Args:
            file_path: Path to the texture file
            quality: Quality level (1-100 for JPEG/WebP)
            resolution: Target resolution (4k, 2k, 1k, etc.)
            
        Returns:
            Path to the optimized texture file
        """
        # In a real implementation, this would:
        # - Resize the texture to target resolution
        # - Convert to optimal format (WebP, DDS, KTX2)
        # - Apply compression based on quality setting
        
        # For now, we'll just return the original file path
        return file_path
    
    def _generate_texture_thumbnails(self, file_path: str) -> List[str]:
        """
        Generate thumbnails for a texture
        
        Args:
            file_path: Path to the texture file
            
        Returns:
            List of thumbnail file paths
        """
        # In a real implementation, this would generate smaller versions
        # For now, we'll return mock thumbnail paths
        return [
            f"{file_path}_thumb_small.jpg",
            f"{file_path}_thumb_medium.jpg"
        ]
    
    def _analyze_texture(self, file_path: str) -> Dict:
        """
        Analyze a texture to extract metadata
        
        Args:
            file_path: Path to the texture file
            
        Returns:
            Dictionary with texture information
        """
        # In a real implementation, this would extract texture properties
        # For now, we'll return mock data
        return {
            "width": 2048,
            "height": 2048,
            "channels": 4,
            "bit_depth": 8,
            "color_space": "sRGB",
            "compression": "JPEG"
        }
    
    def _process_3d_scan(self, file_path: str) -> str:
        """
        Process a 3D scan file
        
        Args:
            file_path: Path to the scan file
            
        Returns:
            Path to the processed scan file
        """
        # In a real implementation, this would:
        # - Clean up scan noise
        # - Fill holes in the mesh
        # - Optimize topology
        # - Apply proper UV mapping
        
        # For now, we'll just return the original file path
        return file_path
    
    def _generate_scan_preview(self, file_path: str) -> str:
        """
        Generate a preview image for a 3D scan
        
        Args:
            file_path: Path to the scan file
            
        Returns:
            Path to the preview image
        """
        # In a real implementation, this would render a preview image
        # For now, we'll return a mock preview path
        return f"{file_path}_preview.jpg"
    
    def _move_to_storage(self, file_path: str, user_id: str, asset_id: str, file_name: str) -> str:
        """
        Move a processed file to permanent storage
        
        Args:
            file_path: Path to the processed file
            user_id: ID of the user who owns the asset
            asset_id: ID of the asset
            file_name: Name for the stored file
            
        Returns:
            Path to the stored file
        """
        # Create user-specific storage directory
        user_storage_dir = self.base_storage_path / "users" / user_id
        user_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create final file path
        final_path = user_storage_dir / f"{asset_id}_{file_name}{Path(file_path).suffix}"
        
        # Move file to storage
        shutil.move(file_path, final_path)
        
        return str(final_path)
    
    def _get_mime_type(self, file_extension: str) -> str:
        """
        Get MIME type for a file extension
        
        Args:
            file_extension: File extension without dot
            
        Returns:
            MIME type string
        """
        mime_types = {
            "glb": "model/gltf-binary",
            "gltf": "model/gltf+json",
            "fbx": "application/octet-stream",
            "obj": "application/octet-stream",
            "usdz": "model/vnd.usdz+zip",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "dds": "image/vnd.ms-dds",
            "ktx2": "image/ktx2"
        }
        
        return mime_types.get(file_extension.lower(), "application/octet-stream")
    
    def get_asset_info(self, asset_id: str, user_id: str) -> Optional[Dict]:
        """
        Get information about a processed asset
        
        Args:
            asset_id: ID of the asset
            user_id: ID of the user who owns the asset
            
        Returns:
            Asset information or None if not found
        """
        try:
            # Construct asset path
            asset_path = self.base_storage_path / "users" / user_id / asset_id
            
            # Check if asset exists
            if not asset_path.exists():
                return None
            
            # Get file information
            stat = asset_path.stat()
            
            # Return asset information
            return {
                "id": asset_id,
                "user_id": user_id,
                "file_path": str(asset_path),
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting asset info: {str(e)}")
            return None
    
    def delete_asset(self, asset_id: str, user_id: str) -> bool:
        """
        Delete an asset from storage
        
        Args:
            asset_id: ID of the asset to delete
            user_id: ID of the user who owns the asset
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Construct asset path
            asset_path = self.base_storage_path / "users" / user_id / asset_id
            
            # Check if asset exists
            if not asset_path.exists():
                return False
            
            # Delete the asset
            asset_path.unlink()
            
            logger.info(f"Asset {asset_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting asset: {str(e)}")
            return False
    
    def list_user_assets(self, user_id: str) -> List[Dict]:
        """
        List all assets for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of asset information
        """
        try:
            # Construct user assets directory
            user_assets_dir = self.base_storage_path / "users" / user_id
            
            # Check if directory exists
            if not user_assets_dir.exists():
                return []
            
            # List all files in the directory
            assets = []
            for asset_file in user_assets_dir.iterdir():
                if asset_file.is_file():
                    stat = asset_file.stat()
                    assets.append({
                        "id": asset_file.name,
                        "user_id": user_id,
                        "file_path": str(asset_file),
                        "file_size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return assets
            
        except Exception as e:
            logger.error(f"Error listing user assets: {str(e)}")
            return []

# Global asset pipeline instance
asset_pipeline = AssetPipeline()

# Convenience functions
def process_asset(file_path: str, asset_type: AssetType, user_id: str, metadata: Dict = None) -> Dict:
    """Process an asset through the pipeline"""
    return asset_pipeline.process_uploaded_asset(file_path, asset_type, user_id, metadata)

def get_asset(asset_id: str, user_id: str) -> Optional[Dict]:
    """Get information about an asset"""
    return asset_pipeline.get_asset_info(asset_id, user_id)

def delete_asset(asset_id: str, user_id: str) -> bool:
    """Delete an asset"""
    return asset_pipeline.delete_asset(asset_id, user_id)

def list_assets(user_id: str) -> List[Dict]:
    """List all assets for a user"""
    return asset_pipeline.list_user_assets(user_id)

if __name__ == "__main__":
    print("Aetherstore Engine 3D Asset Pipeline")
    print("====================================")
    print("Asset pipeline initialized and ready for use.")
    print(f"Storage path: {asset_pipeline.base_storage_path}")
    print(f"Temp path: {asset_pipeline.temp_path}")