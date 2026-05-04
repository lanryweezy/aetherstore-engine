import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from collections import deque
import numpy as np

logger = logging.getLogger("aetherstore.observability")

# Global metrics buffer for telemetry (Last 100 requests)
METRICS = deque(maxlen=100)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured logging and request performance tracking.
    Tracks latency and status for all API calls to the AI pillars.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000 # ms
            
            # Update global metrics
            METRICS.append(process_time)
            
            log_data = {
                "event": "request_completed",
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "latency_ms": round(process_time, 2),
                "client": client_host
            }
            
            if process_time > 1000:
                logger.warning(f"🐢 Slow Request: {json.dumps(log_data)}")
            else:
                logger.info(f"✅ Request: {json.dumps(log_data)}")
                
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            log_data = {
                "event": "request_failed",
                "method": method,
                "path": path,
                "error": str(e),
                "latency_ms": round(process_time, 2),
                "client": client_host
            }
            logger.error(f"❌ Failure: {json.dumps(log_data)}")
            raise e

def get_performance_stats():
    """Returns aggregated latency metrics for the telemetry engine"""
    if not METRICS:
        return {"avg_ms": 0, "p95_ms": 0, "load": "idle"}
    
    m_list = list(METRICS)
    return {
        "avg_ms": round(float(np.mean(m_list)), 2),
        "p95_ms": round(float(np.percentile(m_list, 95)), 2),
        "total_tracked": len(m_list),
        "load": "high" if np.mean(m_list) > 500 else "nominal"
    }
