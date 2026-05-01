import os
import logging
from celery import shared_task
from asset_processor_3d import optimize_3d_model, OptimizationLevel
from database import SessionLocal
from crud import update_product

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=2)
def process_3d_model_task(self, product_id: str, raw_path: str, optimized_path: str):
    """
    Celery background task to optimize a 3D model and update the database.
    This runs in a completely separate process from the FastAPI web server.
    """
    logger.info(f"Starting async optimization task for product {product_id}")

    try:
        # Decimate mesh and compress textures automatically
        result = optimize_3d_model(raw_path, optimized_path, OptimizationLevel.MEDIUM)

        if result.success:
            final_path = optimized_path
            try:
                os.remove(raw_path) # Clean up raw file to save space
            except OSError:
                pass
        else:
            final_path = raw_path # Fallback to raw if optimization fails
            logger.warning(f"3D Optimization failed for {product_id}: {result.error_message}")

    except Exception as e:
        final_path = raw_path
        logger.error(f"Critical error in 3D pipeline for {product_id}: {str(e)}")
        # We can retry on critical failures
        raise self.retry(exc=e, countdown=10)

    # Create a fresh database session for the background task
    db = SessionLocal()
    try:
        update_product(db, product_id, {"model_3d_url": final_path})
        db.commit()
        logger.info(f"Successfully optimized and updated product {product_id}")
        return {"status": "success", "product_id": product_id, "final_path": final_path}
    except Exception as e:
        logger.error(f"Failed to update database for product {product_id} after optimization: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=5)
    finally:
        db.close()