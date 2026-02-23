# asset_management.py
# 3D Asset Management System for Aetherstore Engine

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import uuid

# Import our asset processing components
from asset_pipeline import AssetPipeline, AssetType, AssetStatus
from asset_optimizer import AssetOptimizer, AssetReport
from 3d_processing import ModelProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetManagementSystem:
    """Comprehensive 3D Asset Management System"""
    
    def __init__(self, storage_path: str = "assets", temp_path: str = "temp"):
        """
        Initialize the asset management system
        
        Args:
            storage_path: Base path for storing processed assets
            temp_path: Temporary path for processing files
        """
        self.storage_path = Path(storage_path)
        self.temp_path = Path(temp_path)
        
        # Create directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize processing components
        self.asset_pipeline = AssetPipeline(str(self.storage_path), str(self.temp_path))
        self.asset_optimizer = AssetOptimizer()
        self.model_processor = ModelProcessor()
        
        # Asset database (in a real implementation, this would be a proper database)
        self.assets_db = {}
        self.processing_queue = {}
        
        logger.info("Asset Management System initialized")
    
    def upload_asset(self, file_path: str, user_id: str, 
                    asset_type: AssetType, metadata: Dict = None) -> str:
        """
        Upload and register a new asset
        
        Args:
            file_path: Path to the asset file
            user_id: ID of user uploading the asset
            asset_type: Type of asset being uploaded
            metadata: Additional metadata
            
        Returns:
            Asset ID of the registered asset
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Asset file not found: {file_path}")
            
            # Generate asset ID
            asset_id = str(uuid.uuid4())
            
            # Create asset record
            asset_record = {
                "id": asset_id,
                "user_id": user_id,
                "asset_type": asset_type.value,
                "original_file_path": file_path,
                "upload_timestamp": datetime.now().isoformat(),
                "status": AssetStatus.UPLOADING.value,
                "metadata": metadata or {},
                "processing_log": []
            }
            
            # Store asset record
            self.assets_db[asset_id] = asset_record
            
            logger.info(f"Asset {asset_id} registered for user {user_id}")
            return asset_id
            
        except Exception as e:
            logger.error(f"Asset upload failed: {str(e)}")
            raise
    
    def process_asset(self, asset_id: str, optimization_settings: Optional[Dict] = None) -> bool:
        """
        Process an uploaded asset through the pipeline
        
        Args:
            asset_id: ID of asset to process
            optimization_settings: Settings for asset optimization
            
        Returns:
            True if processing started successfully, False otherwise
        """
        try:
            # Retrieve asset record
            if asset_id not in self.assets_db:
                raise ValueError(f"Asset not found: {asset_id}")
            
            asset_record = self.assets_db[asset_id]
            
            # Update status
            asset_record["status"] = AssetStatus.PROCESSING.value
            asset_record["processing_log"].append({
                "timestamp": datetime.now().isoformat(),
                "status": AssetStatus.PROCESSING.value,
                "message": "Asset processing started"
            })
            
            # Add to processing queue
            self.processing_queue[asset_id] = {
                "asset_record": asset_record,
                "settings": optimization_settings,
                "start_time": datetime.now()
            }
            
            logger.info(f"Asset {asset_id} added to processing queue")
            return True
            
        except Exception as e:
            logger.error(f"Asset processing initiation failed: {str(e)}")
            return False
    
    def execute_processing_queue(self) -> Dict[str, AssetReport]:
        """
        Execute all queued asset processing jobs
        
        Returns:
            Dictionary mapping asset IDs to processing reports
        """
        results = {}
        
        # Process each queued asset
        for asset_id, processing_job in list(self.processing_queue.items()):
            try:
                asset_record = processing_job["asset_record"]
                settings = processing_job["settings"]
                start_time = processing_job["start_time"]
                
                # Process asset through pipeline
                processed_asset = self.asset_pipeline.process_uploaded_asset(
                    asset_record["original_file_path"],
                    AssetType(asset_record["asset_type"]),
                    asset_record["user_id"],
                    asset_record["metadata"]
                )
                
                # If pipeline succeeded, optimize the asset
                if processed_asset["status"] == AssetStatus.READY.value:
                    # Optimize the processed asset
                    optimization_report = self.asset_optimizer.optimize_asset(
                        processed_asset["file_url"],
                        self._get_optimized_path(asset_id),
                        AssetType(asset_record["asset_type"]),
                        settings
                    )
                    
                    # Update asset record with optimization results
                    asset_record.update({
                        "optimized_file_url": self._get_optimized_path(asset_id),
                        "optimization_report": optimization_report.__dict__,
                        "status": AssetStatus.READY.value,
                        "processing_completed": datetime.now().isoformat(),
                        "processing_duration": (datetime.now() - start_time).total_seconds()
                    })
                    
                    results[asset_id] = optimization_report
                    
                    # Update processing log
                    asset_record["processing_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": AssetStatus.READY.value,
                        "message": "Asset processing and optimization completed successfully"
                    })
                
                else:
                    # Pipeline failed
                    asset_record["status"] = processed_asset.get("status", AssetStatus.ERROR.value)
                    asset_record["error"] = processed_asset.get("error", "Unknown error")
                    asset_record["processing_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": AssetStatus.ERROR.value,
                        "message": f"Asset processing failed: {processed_asset.get('error', 'Unknown error')}"
                    })
                    
                    results[asset_id] = processed_asset.get("error", "Processing failed")
                
                # Remove from queue
                del self.processing_queue[asset_id]
                
            except Exception as e:
                logger.error(f"Asset processing failed for {asset_id}: {str(e)}")
                
                # Update asset record with error
                if asset_id in self.assets_db:
                    asset_record = self.assets_db[asset_id]
                    asset_record["status"] = AssetStatus.ERROR.value
                    asset_record["error"] = str(e)
                    asset_record["processing_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "status": AssetStatus.ERROR.value,
                        "message": f"Processing error: {str(e)}"
                    })
                
                # Remove from queue
                if asset_id in self.processing_queue:
                    del self.processing_queue[asset_id]
                
                results[asset_id] = f"Processing error: {str(e)}"
        
        logger.info(f"Processing queue execution completed. {len(results)} assets processed.")
        return results
    
    def get_asset_info(self, asset_id: str, user_id: str) -> Optional[Dict]:
        """
        Get information about a specific asset
        
        Args:
            asset_id: ID of the asset
            user_id: ID of the user (for permission check)
            
        Returns:
            Asset information or None if not found/authorized
        """
        try:
            if asset_id not in self.assets_db:
                return None
            
            asset_record = self.assets_db[asset_id]
            
            # Check user authorization
            if asset_record["user_id"] != user_id:
                # In a real implementation, we'd also check for admin access
                return None
            
            return asset_record
            
        except Exception as e:
            logger.error(f"Error retrieving asset info for {asset_id}: {str(e)}")
            return None
    
    def list_user_assets(self, user_id: str, asset_type: Optional[AssetType] = None) -> List[Dict]:
        """
        List all assets for a specific user
        
        Args:
            user_id: ID of the user
            asset_type: Optional filter by asset type
            
        Returns:
            List of asset information
        """
        try:
            user_assets = []
            
            for asset_id, asset_record in self.assets_db.items():
                # Filter by user
                if asset_record["user_id"] != user_id:
                    continue
                
                # Filter by asset type if specified
                if asset_type and asset_record["asset_type"] != asset_type.value:
                    continue
                
                user_assets.append(asset_record)
            
            logger.info(f"Retrieved {len(user_assets)} assets for user {user_id}")
            return user_assets
            
        except Exception as e:
            logger.error(f"Error listing user assets: {str(e)}")
            return []
    
    def delete_asset(self, asset_id: str, user_id: str) -> bool:
        """
        Delete an asset
        
        Args:
            asset_id: ID of the asset to delete
            user_id: ID of the user (for permission check)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if asset_id not in self.assets_db:
                logger.warning(f"Attempt to delete non-existent asset {asset_id}")
                return False
            
            asset_record = self.assets_db[asset_id]
            
            # Check user authorization
            if asset_record["user_id"] != user_id:
                logger.warning(f"Unauthorized attempt to delete asset {asset_id} by user {user_id}")
                return False
            
            # Remove from processing queue if present
            if asset_id in self.processing_queue:
                del self.processing_queue[asset_id]
            
            # Delete asset files
            file_paths = [
                asset_record.get("original_file_path"),
                asset_record.get("optimized_file_url"),
                asset_record.get("file_url")
            ]
            
            for file_path in file_paths:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.debug(f"Deleted asset file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete asset file {file_path}: {str(e)}")
            
            # Remove from database
            del self.assets_db[asset_id]
            
            logger.info(f"Asset {asset_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting asset {asset_id}: {str(e)}")
            return False
    
    def get_processing_status(self, asset_id: str) -> Optional[Dict]:
        """
        Get the current processing status of an asset
        
        Args:
            asset_id: ID of the asset
            
        Returns:
            Processing status or None if asset not found
        """
        try:
            # Check if asset exists
            if asset_id not in self.assets_db:
                return None
            
            asset_record = self.assets_db[asset_id]
            
            # Check if in processing queue
            if asset_id in self.processing_queue:
                queue_entry = self.processing_queue[asset_id]
                queue_time = queue_entry["start_time"]
                wait_time = (datetime.now() - queue_time).total_seconds()
                
                return {
                    "status": "queued",
                    "asset_id": asset_id,
                    "wait_time_seconds": wait_time,
                    "queue_position": list(self.processing_queue.keys()).index(asset_id) + 1
                }
            
            # Return current status
            return {
                "status": asset_record["status"],
                "asset_id": asset_id,
                "processing_log": asset_record.get("processing_log", []),
                "error": asset_record.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error getting processing status for {asset_id}: {str(e)}")
            return None
    
    def get_system_stats(self) -> Dict:
        """
        Get system statistics
        
        Returns:
            Dictionary with system statistics
        """
        try:
            total_assets = len(self.assets_db)
            processing_assets = len(self.processing_queue)
            completed_assets = sum(1 for asset in self.assets_db.values() 
                                 if asset["status"] == AssetStatus.READY.value)
            error_assets = sum(1 for asset in self.assets_db.values() 
                             if asset["status"] == AssetStatus.ERROR.value)
            
            # Calculate total storage usage
            total_storage_mb = 0
            for asset_record in self.assets_db.values():
                file_paths = [
                    asset_record.get("original_file_path"),
                    asset_record.get("optimized_file_url"),
                    asset_record.get("file_url")
                ]
                
                for file_path in file_paths:
                    if file_path and os.path.exists(file_path):
                        try:
                            total_storage_mb += os.path.getsize(file_path) / (1024 * 1024)
                        except:
                            pass
            
            stats = {
                "total_assets": total_assets,
                "processing_queue_size": processing_assets,
                "completed_assets": completed_assets,
                "error_assets": error_assets,
                "total_storage_mb": round(total_storage_mb, 2),
                "supported_asset_types": [t.value for t in AssetType],
                "system_uptime": datetime.now().isoformat()
            }
            
            logger.debug("System statistics retrieved")
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving system statistics: {str(e)}")
            return {}
    
    def _get_optimized_path(self, asset_id: str) -> str:
        """
        Generate path for optimized asset file
        
        Args:
            asset_id: ID of the asset
            
        Returns:
            Path for optimized asset file
        """
        return str(self.storage_path / "optimized" / f"{asset_id}_optimized.glb")
    
    def cleanup_temp_files(self) -> int:
        """
        Clean up temporary files
        
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            
            # Clean up temp directory
            if self.temp_path.exists():
                for temp_file in self.temp_path.glob("*"):
                    try:
                        if temp_file.is_file():
                            temp_file.unlink()
                        elif temp_file.is_dir():
                            import shutil
                            shutil.rmtree(temp_file)
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file {temp_file}: {str(e)}")
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {str(e)}")
            return 0

# Global asset management system instance
asset_management_system = AssetManagementSystem()

# Convenience functions
def register_asset(file_path: str, user_id: str, 
                  asset_type: AssetType, metadata: Dict = None) -> str:
    """Register a new asset"""
    return asset_management_system.upload_asset(file_path, user_id, asset_type, metadata)

def process_registered_asset(asset_id: str, 
                           optimization_settings: Optional[Dict] = None) -> bool:
    """Process a registered asset"""
    return asset_management_system.process_asset(asset_id, optimization_settings)

def get_asset_information(asset_id: str, user_id: str) -> Optional[Dict]:
    """Get information about a specific asset"""
    return asset_management_system.get_asset_info(asset_id, user_id)

def list_user_asset_collection(user_id: str, 
                              asset_type: Optional[AssetType] = None) -> List[Dict]:
    """List all assets for a user"""
    return asset_management_system.list_user_assets(user_id, asset_type)

def remove_asset(asset_id: str, user_id: str) -> bool:
    """Delete an asset"""
    return asset_management_system.delete_asset(asset_id, user_id)

def get_asset_processing_status(asset_id: str) -> Optional[Dict]:
    """Get processing status of an asset"""
    return asset_management_system.get_processing_status(asset_id)

def execute_asset_processing_queue() -> Dict[str, AssetReport]:
    """Execute all queued processing jobs"""
    return asset_management_system.execute_processing_queue()

def get_asset_system_statistics() -> Dict:
    """Get system statistics"""
    return asset_management_system.get_system_stats()

if __name__ == "__main__":
    print("Aetherstore Engine 3D Asset Management System")
    print("=============================================")
    print("Asset management system initialized and ready for use.")
    print(f"Storage path: {asset_management_system.storage_path}")
    print(f"Temp path: {asset_management_system.temp_path}")