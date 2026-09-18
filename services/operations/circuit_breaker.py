"""Circuit Breakers, Rate Limiters & Resilience Controls Service."""

import time
import math
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class CircuitBreaker:
    """Stateful circuit breaker implementation (CLOSED, OPEN, HALF_OPEN)."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 10.0,
        half_open_success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.half_open_success_threshold = half_open_success_threshold

        self.state = "CLOSED"
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        self.last_failure_time = None

    def allow_request(self) -> bool:
        """Determine whether incoming request is allowed through circuit."""
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_state_change >= self.recovery_timeout_seconds:
                self.state = "HALF_OPEN"
                self.success_count = 0
                self.last_state_change = now
                return True
            return False

        return True

    def record_success(self) -> None:
        """Record successful invocation."""
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self.state = "CLOSED"
                self.failure_count = 0
                self.last_state_change = time.time()
        elif self.state == "CLOSED":
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed invocation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state in ["CLOSED", "HALF_OPEN"]:
            if self.failure_count >= self.failure_threshold or self.state == "HALF_OPEN":
                self.state = "OPEN"
                self.last_state_change = time.time()

    def get_status(self) -> Dict[str, Any]:
        """Return circuit breaker status dictionary."""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout_seconds,
            "last_state_change": datetime.fromtimestamp(self.last_state_change, timezone.utc).isoformat(),
        }


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(self, capacity: int = 100, refill_rate_per_sec: float = 10.0):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def consume(self, tokens_needed: int = 1) -> bool:
        """Attempt to consume tokens."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False


class CircuitBreakerAndResilienceService:
    """Service providing unified circuit breaker registry, rate limiting, and backpressure controls."""

    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._rate_limiters: Dict[str, TokenBucketRateLimiter] = {}

    def get_or_create_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 10.0,
    ) -> CircuitBreaker:
        """Get or initialize a circuit breaker instance by name."""
        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout_seconds=recovery_timeout_seconds,
            )
        return self._circuit_breakers[name]

    def check_circuit(self, name: str) -> bool:
        """Check if circuit allows request execution."""
        cb = self.get_or_create_circuit_breaker(name)
        return cb.allow_request()

    def record_circuit_outcome(self, name: str, success: bool) -> Dict[str, Any]:
        """Record success or failure on circuit breaker."""
        cb = self.get_or_create_circuit_breaker(name)
        if success:
            cb.record_success()
        else:
            cb.record_failure()
        return cb.get_status()

    def check_rate_limit(
        self,
        key: str,
        capacity: int = 100,
        refill_rate_per_sec: float = 10.0,
    ) -> bool:
        """Check and consume rate limit token."""
        if key not in self._rate_limiters:
            self._rate_limiters[key] = TokenBucketRateLimiter(capacity, refill_rate_per_sec)
        return self._rate_limiters[key].consume()

    def calculate_backoff_delay(
        self,
        attempt: int,
        base_delay_ms: float = 100.0,
        max_delay_ms: float = 5000.0,
        jitter: bool = True,
    ) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        exponential = base_delay_ms * (2 ** (attempt - 1))
        delay = min(max_delay_ms, exponential)
        if jitter:
            delay = delay * random.uniform(0.8, 1.2)
        return round(delay, 2)

    def evaluate_backpressure(
        self,
        current_queue_depth: int,
        max_capacity: int = 1000,
        high_watermark_pct: float = 80.0,
    ) -> Dict[str, Any]:
        """Evaluate backpressure queue status and determine load shedding decision."""
        utilization_pct = (current_queue_depth / max_capacity) * 100.0 if max_capacity > 0 else 100.0
        should_shed_load = utilization_pct >= high_watermark_pct

        return {
            "current_queue_depth": current_queue_depth,
            "max_capacity": max_capacity,
            "utilization_pct": round(utilization_pct, 2),
            "high_watermark_pct": high_watermark_pct,
            "should_shed_load": should_shed_load,
            "action": "SHED_TRAFFIC" if should_shed_load else "PROCESS_NORMAL",
        }

    def list_circuit_breakers() -> List[Dict[str, Any]]:
        """List status of all registered circuit breakers."""
        return [cb.get_status() for cb in self._circuit_breakers.values()]
