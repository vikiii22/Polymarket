"""Custom exceptions for API operations."""


class ApiConnectionError(Exception):
    """Raised when unable to connect to the Polymarket API."""
    pass


class InvalidTokenIdError(ValueError):
    """Raised when a token ID is invalid or not found."""
    pass


class OrderPlacementError(Exception):
    """Raised when an order placement fails."""
    pass


class InsufficientBalanceError(Exception):
    """Raised when attempting to place order with insufficient balance."""
    pass


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass
