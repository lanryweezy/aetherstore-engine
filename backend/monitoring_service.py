# monitoring_service.py
# Comprehensive monitoring and observability service

import logging
import time
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from collections import defaultdict
import traceback
from starlette.requests import Request
from starlette.responses import Response

# Try to import monitoring libraries (optional)
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Prometheus metrics (if available)
if PROMETHEUS_AVAILABLE:
    http_requests_total = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration',
        ['method', 'endpoint']
    )
    
    active_connections = Gauge(
        'active_connections',
        'Number of active connections'
    )
    
    database_query_duration = Histogram(
        'database_query_duration_seconds',
        'Database query duration'
    )
    
    payment_processing_duration = Histogram(
        'payment_processing_duration_seconds',
        'Payment processing duration',
        ['provider']
    )
    
    order_creation_total = Counter(
        'order_creation_total',
        'Total orders created',
        ['status']
    )

class MonitoringService:
    """Comprehensive monitoring and observability service"""
    
    def __init__(self):
        self.sentry_dsn = None
        self.environment = "development"
        self.enable_sentry = False
        self.enable_prometheus = False
        
        # In-memory metrics (fallback if Prometheus not available)
        self.metrics = {
            "requests": defaultdict(int),
            "errors": defaultdict(int),
            "response_times": defaultdict(list),
            "active_connections": 0
        }
        
        logger.info("Monitoring Service initialized")
    
    def initialize_sentry(self, dsn: str, environment: str = "production"):
        """Initialize Sentry for error tracking"""
        if not SENTRY_AVAILABLE:
            logger.warning("Sentry SDK not available. Install with: pip install sentry-sdk")
            return False
        
        try:
            sentry_sdk.init(
                dsn=dsn,
                environment=environment,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,  # 10% of transactions
                profiles_sample_rate=0.1,
            )
            self.sentry_dsn = dsn
            self.environment = environment
            self.enable_sentry = True
            logger.info("Sentry initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {str(e)}")
            return False
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture an exception for error tracking"""
        if self.enable_sentry and SENTRY_AVAILABLE:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_exception(exception)
        else:
            # Log to file/system
            logger.error(f"Exception: {str(exception)}", exc_info=True)
            if context:
                logger.error(f"Context: {context}")
    
    def capture_message(self, message: str, level: str = "info"):
        """Capture a message for logging"""
        if self.enable_sentry and SENTRY_AVAILABLE:
            sentry_sdk.capture_message(message, level=level)
        else:
            getattr(logger, level.lower(), logger.info)(message)
    
    def track_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics"""
        if PROMETHEUS_AVAILABLE:
            http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
            http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        else:
            # Fallback to in-memory metrics
            self.metrics["requests"][f"{method} {endpoint} {status_code}"] += 1
            self.metrics["response_times"][endpoint].append(duration)
            
            # Keep only last 1000 response times per endpoint
            if len(self.metrics["response_times"][endpoint]) > 1000:
                self.metrics["response_times"][endpoint] = self.metrics["response_times"][endpoint][-1000:]
    
    def track_error(self, error_type: str, endpoint: Optional[str] = None):
        """Track error occurrence"""
        if PROMETHEUS_AVAILABLE:
            # Prometheus handles this via status codes in track_request
            pass
        else:
            key = f"{error_type}"
            if endpoint:
                key += f" {endpoint}"
            self.metrics["errors"][key] += 1
    
    def track_database_query(self, query_type: str, duration: float):
        """Track database query performance"""
        if PROMETHEUS_AVAILABLE:
            database_query_duration.observe(duration)
        else:
            logger.debug(f"Database query: {query_type} took {duration:.3f}s")
    
    def track_payment(self, provider: str, duration: float, success: bool):
        """Track payment processing"""
        if PROMETHEUS_AVAILABLE:
            payment_processing_duration.labels(provider=provider).observe(duration)
        else:
            logger.info(f"Payment {provider}: {'success' if success else 'failed'} in {duration:.3f}s")
    
    def track_order(self, status: str):
        """Track order creation"""
        if PROMETHEUS_AVAILABLE:
            order_creation_total.labels(status=status).inc()
        else:
            self.metrics["requests"][f"order_{status}"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "requests": dict(self.metrics["requests"]),
            "errors": dict(self.metrics["errors"]),
            "active_connections": self.metrics["active_connections"]
        }
        
        # Calculate average response times
        avg_response_times = {}
        for endpoint, times in self.metrics["response_times"].items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        metrics["avg_response_times"] = avg_response_times
        
        return metrics
    
    def get_prometheus_metrics(self) -> Optional[str]:
        """Get Prometheus metrics in text format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest().decode('utf-8')
        return None

# Global monitoring service
monitoring_service = MonitoringService()

# Middleware for request tracking
async def monitoring_middleware(request: Request, call_next):
    """Middleware to track requests"""
    start_time = time.time()
    
    # Track active connections
    monitoring_service.metrics["active_connections"] += 1
    if PROMETHEUS_AVAILABLE:
        active_connections.inc()
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track request
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        monitoring_service.track_request(method, endpoint, status_code, duration)
        
        # Add custom headers
        response.headers["X-Response-Time"] = f"{duration:.3f}"
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        monitoring_service.capture_exception(e, {
            "endpoint": request.url.path,
            "method": request.method,
            "duration": duration
        })
        monitoring_service.track_error(type(e).__name__, request.url.path)
        raise
    finally:
        monitoring_service.metrics["active_connections"] -= 1
        if PROMETHEUS_AVAILABLE:
            active_connections.dec()

# Decorator for tracking function performance
def track_performance(func_name: Optional[str] = None):
    """Decorator to track function performance"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitoring_service.capture_exception(e, {
                    "function": name,
                    "duration": duration
                })
                raise
        
        return wrapper
    return decorator

