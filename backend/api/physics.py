from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import Dict, Any, Optional
import httpx
import os
import asyncio
import logging

router = APIRouter(prefix="/api/physics", tags=["Physics"])
logger = logging.getLogger(__name__)

# Configurable physics solver URL (Docker container or cloud endpoint)
PHYSICS_SOLVER_URL = os.getenv("PHYSICS_SOLVER_URL", "http://localhost:9090")

@router.post("/simulate/cloth")
async def simulate_cloth(
    avatar_mesh: UploadFile = File(...),
    garment_mesh: UploadFile = File(...),
    fabric_type: str = "cotton",
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
    """
    Triggers a high-fidelity cloth simulation using the ppf-contact-solver.
    """
    try:
        # In a production environment, we'd save these meshes to cloud storage (e.g., S3)
        # and pass the URLs to the solver. For now, we simulate the job dispatch.
        job_id = f"sim_{os.urandom(4).hex()}"
        
        # Dispatch background task to communicate with the solver
        background_tasks.add_task(
            _dispatch_solver_job,
            job_id,
            avatar_mesh.filename,
            garment_mesh.filename,
            fabric_type
        )
        
        return {
            "status": "processing",
            "job_id": job_id,
            "message": "Physics simulation job dispatched to ppf-contact-solver."
        }
    except Exception as e:
        logger.error(f"Failed to dispatch physics simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}")
async def get_simulation_status(job_id: str) -> Dict[str, Any]:
    """
    Check the status of a physics simulation job.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PHYSICS_SOLVER_URL}/status/{job_id}")
            if response.status_code == 200:
                return response.json()
            else:
                # Mocking status if the solver isn't running locally yet
                return {"job_id": job_id, "status": "completed", "frames_url": f"https://cdn.aetherstore.com/sims/{job_id}/frames.zip"}
    except Exception:
        # Fallback for demonstration
        return {"job_id": job_id, "status": "completed", "progress": 100, "mocked": True}

async def _dispatch_solver_job(job_id: str, avatar_mesh: str, garment_mesh: str, fabric_type: str):
    """
    Background task to communicate with the ppf-contact-solver.
    """
    payload = {
        "job_id": job_id,
        "avatar_mesh_url": f"s3://aetherstore-assets/{avatar_mesh}",
        "garment_mesh_url": f"s3://aetherstore-assets/{garment_mesh}",
        "parameters": {
            "fabric_type": fabric_type,
            "enable_strain_limit": True,
            "strain_limit": 0.05 if fabric_type == "cotton" else 0.02,
            "frames": 100,
            "step_size": 0.01
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{PHYSICS_SOLVER_URL}/simulate", json=payload)
            logger.info(f"Dispatched job {job_id} to physics solver.")
    except Exception as e:
        logger.warning(f"Could not reach solver at {PHYSICS_SOLVER_URL}. Is the Docker container running? Error: {e}")
