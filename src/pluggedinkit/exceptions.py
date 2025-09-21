"""Exception classes for Plugged.in SDK"""

from typing import Any, Optional


class PluggedInError(Exception):
    """Base exception for Plugged.in SDK"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class AuthenticationError(PluggedInError):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(PluggedInError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(PluggedInError):
    """Raised when a resource is not found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(PluggedInError):
    """Raised when request validation fails"""

    def __init__(self, message: str, errors: Optional[Any] = None):
        super().__init__(message, status_code=400, details=errors)