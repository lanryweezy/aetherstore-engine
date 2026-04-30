import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    A simple Circuit Breaker implementation to prevent cascading failures.
    If an external service fails continuously, this will "open" the circuit
    and immediately reject further calls for a cool-down period.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit Breaker tripped! State set to OPEN after {self.failure_count} failures.")

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("Circuit Breaker recovered. State set to CLOSED.")
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if cool-down period has elapsed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False

        if self.state == "HALF_OPEN":
            # Only allow one test request through
            return True

        return False

    def __call__(self, func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise e

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not self.can_execute():
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise e

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

# Global instances for specific services
stripe_circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
email_circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=120)
