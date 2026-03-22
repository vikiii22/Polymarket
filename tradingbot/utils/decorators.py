"""Decorator functions for common patterns like retry and timeout."""

import time
import functools
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_failure(
    max_retries: int = 3,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry a function on failure with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff: Backoff multiplier (2.0 means double wait time each retry)
        exceptions: Tuple of exception types to catch and retry
        
    Example:
        @retry_on_failure(max_retries=3, backoff=2)
        def fetch_data():
            # Code that might fail
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            wait_time = 1.0
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                        wait_time *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def timeout(seconds: float) -> Callable:
    """
    Decorator to add a timeout to a function (basic version without threading).
    
    Note: This is a placeholder. For production, use concurrent.futures or asyncio timeouts.
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # For now, just log. Full implementation requires threading/asyncio
            logger.debug(f"Executing {func.__name__} with {seconds}s timeout")
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_execution(level: int = logging.INFO) -> Callable:
    """
    Decorator to log function execution with timing.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            logger.log(level, f"Starting {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(level, f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Failed {func.__name__} after {elapsed:.2f}s: {e}")
                raise
        
        return wrapper
    return decorator
