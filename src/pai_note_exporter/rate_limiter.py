"""Rate limiting utilities for API requests."""

import asyncio
import time
from collections import deque
from typing import Dict


class RateLimiter:
    """Token bucket rate limiter for API requests.

    Uses a token bucket algorithm to limit request rates while allowing
    bursts up to the specified limit.
    """

    def __init__(
        self,
        requests_per_second: float = 5.0,
        burst_limit: int = 15,
        name: str = "API"
    ):
        """Initialize the rate limiter.

        Args:
            requests_per_second: Average rate of requests allowed per second
            burst_limit: Maximum number of tokens (burst capacity)
            name: Name for logging/debugging purposes
        """
        self.requests_per_second = requests_per_second
        self.burst_limit = burst_limit
        self.name = name

        # Current token count
        self.tokens = burst_limit
        # Last time tokens were updated
        self.last_update = time.time()
        # Track recent request times for statistics
        self.request_times: deque[float] = deque(maxlen=1000)

    async def acquire(self) -> None:
        """Acquire permission to make a request.

        Will sleep if necessary to maintain the rate limit.
        """
        now = time.time()

        # Calculate tokens to add based on time passed
        time_passed = now - self.last_update
        tokens_to_add = time_passed * self.requests_per_second
        self.tokens = min(self.burst_limit, self.tokens + tokens_to_add)
        self.last_update = now

        # If we don't have enough tokens, wait
        if self.tokens < 1:
            wait_time = (1 - self.tokens) / self.requests_per_second
            await asyncio.sleep(wait_time)
            # After waiting, we'll have at least 1 token
            self.tokens = 1

        # Consume a token
        self.tokens -= 1
        self.request_times.append(now)

    def get_stats(self) -> Dict[str, float]:
        """Get rate limiting statistics.

        Returns:
            Dictionary with rate limiting statistics
        """
        now = time.time()

        # Calculate requests in the last minute
        one_minute_ago = now - 60
        recent_requests = sum(1 for t in self.request_times if t > one_minute_ago)

        # Calculate requests in the last 10 seconds
        ten_seconds_ago = now - 10
        very_recent_requests = sum(1 for t in self.request_times if t > ten_seconds_ago)

        return {
            "name": self.name,
            "requests_per_minute": recent_requests,
            "requests_per_10_seconds": very_recent_requests,
            "current_tokens": self.tokens,
            "burst_limit": self.burst_limit,
            "requests_per_second_limit": self.requests_per_second,
        }

    def __str__(self) -> str:
        """String representation of the rate limiter."""
        stats = self.get_stats()
        return (
            f"RateLimiter({self.name}): "
            f"{stats['requests_per_minute']:.1f} req/min, "
            f"{stats['current_tokens']:.1f}/{stats['burst_limit']} tokens"
        )
