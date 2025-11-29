"""Clipboard service for Plugged.in SDK

This module provides both synchronous and asynchronous clipboard services
for persistent key-value and stack-based storage in AI workflows.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import (
    ClipboardDeleteRequest,
    ClipboardEncoding,
    ClipboardEntry,
    ClipboardGetFilters,
    ClipboardListResponse,
    ClipboardSource,
    ClipboardVisibility,
)

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


# -----------------------------------------------------------------------------
# Shared Helper Functions
# -----------------------------------------------------------------------------


def _normalize_encoding(
    encoding: Union[ClipboardEncoding, str]
) -> ClipboardEncoding:
    """Normalize encoding to ClipboardEncoding enum."""
    if isinstance(encoding, ClipboardEncoding):
        return encoding
    return ClipboardEncoding(encoding)


def _normalize_visibility(
    visibility: Union[ClipboardVisibility, str]
) -> ClipboardVisibility:
    """Normalize visibility to ClipboardVisibility enum."""
    if isinstance(visibility, ClipboardVisibility):
        return visibility
    return ClipboardVisibility(visibility)


def _build_clipboard_payload(
    value: str,
    name: Optional[str] = None,
    content_type: str = "text/plain",
    encoding: Union[ClipboardEncoding, str] = ClipboardEncoding.UTF8,
    visibility: Union[ClipboardVisibility, str] = ClipboardVisibility.PRIVATE,
    created_by_tool: Optional[str] = None,
    created_by_model: Optional[str] = None,
    ttl_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    """Build a clipboard request payload with common fields.

    Normalizes encoding and visibility enums in one place.
    """
    # Normalize enums here - callers don't need to
    normalized_encoding = _normalize_encoding(encoding)
    normalized_visibility = _normalize_visibility(visibility)

    payload: Dict[str, Any] = {
        "value": value,
        "contentType": content_type,
        "encoding": normalized_encoding.value,
        "visibility": normalized_visibility.value,
        "source": ClipboardSource.SDK.value,
    }

    if name:
        payload["name"] = name
    if created_by_tool:
        payload["createdByTool"] = created_by_tool
    if created_by_model:
        payload["createdByModel"] = created_by_model
    if ttl_seconds is not None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than 0 when provided")
        payload["ttlSeconds"] = ttl_seconds

    return payload


def _parse_list_response(data: Dict[str, Any]) -> List[ClipboardEntry]:
    """Parse list response and raise on failure."""
    if not data.get("success"):
        raise PluggedInError(data.get("error", "Failed to list clipboard entries"))
    return ClipboardListResponse(**data).entries


def _parse_entry_response(
    data: Dict[str, Any],
    error_msg: str = "Operation failed",
    raise_on_failure: bool = True,
) -> Optional[ClipboardEntry]:
    """Parse entry response with consistent error handling.

    Args:
        data: API response data
        error_msg: Error message to use if raising
        raise_on_failure: If True, raises PluggedInError on failure.
                         If False, returns None on failure.

    Returns:
        ClipboardEntry on success, None on failure (if not raising)

    Raises:
        PluggedInError: If raise_on_failure is True and operation failed
    """
    if not data.get("success"):
        if raise_on_failure:
            raise PluggedInError(data.get("error", error_msg))
        return None

    if "entry" in data and data["entry"]:
        return ClipboardEntry(**data["entry"])

    if raise_on_failure:
        raise PluggedInError(data.get("error", error_msg))
    return None


def _parse_delete_response(data: Dict[str, Any]) -> int:
    """Parse delete response and return deleted count.

    Returns:
        Number of deleted entries (0 if failed)
    """
    if not data.get("success"):
        return 0
    deleted = data.get("deleted", 0)
    return int(deleted) if deleted is not None else 0


def _build_get_params(filters: ClipboardGetFilters) -> Dict[str, str]:
    """Build query params from validated filters."""
    params: Dict[str, str] = {}
    if filters.name is not None:
        params["name"] = filters.name
    if filters.idx is not None:
        params["idx"] = str(filters.idx)
    return params


def _build_delete_payload(request: ClipboardDeleteRequest) -> Dict[str, Any]:
    """Build delete payload from validated request."""
    payload: Dict[str, Any] = {}
    if request.name is not None:
        payload["name"] = request.name
    if request.idx is not None:
        payload["idx"] = request.idx
    return payload


# -----------------------------------------------------------------------------
# Result Types
# -----------------------------------------------------------------------------


@dataclass
class ClearAllResult:
    """Result of clear_all operation with structured feedback.

    Attributes:
        deleted: Number of successfully deleted entries
        failed: Number of entries that failed to delete
        total: Total entries attempted (deleted + failed)
    """
    deleted: int
    failed: int

    @property
    def total(self) -> int:
        """Total entries attempted."""
        return self.deleted + self.failed

    @property
    def success(self) -> bool:
        """True if all entries were deleted."""
        return self.failed == 0


# -----------------------------------------------------------------------------
# Synchronous Clipboard Service
# -----------------------------------------------------------------------------


class ClipboardService:
    """Synchronous clipboard service for Plugged.in.

    Provides persistent key-value and stack-based storage for AI workflows.
    """

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def list(self) -> List[ClipboardEntry]:
        """List all clipboard entries.

        Returns:
            List of ClipboardEntry objects

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request("GET", "/api/clipboard")
        return _parse_list_response(response.json())

    def get(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> Optional[ClipboardEntry]:
        """Get a clipboard entry by name or index.

        Args:
            name: Entry name for key-value lookup
            idx: Entry index for stack-based lookup

        Returns:
            ClipboardEntry if found, None if not found

        Raises:
            ValueError: If neither name nor idx is provided
        """
        # Use Pydantic model for validation
        filters = ClipboardGetFilters(name=name, idx=idx)
        params = _build_get_params(filters)

        response = self.client.request("GET", "/api/clipboard", params=params)
        return _parse_entry_response(
            response.json(),
            error_msg="Failed to get clipboard entry",
            raise_on_failure=False,
        )

    def set(
        self,
        name: str,
        value: str,
        content_type: str = "text/plain",
        encoding: Union[ClipboardEncoding, str] = ClipboardEncoding.UTF8,
        visibility: Union[ClipboardVisibility, str] = ClipboardVisibility.PRIVATE,
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Set a named clipboard entry (upsert).

        Args:
            name: Entry name
            value: Value to store
            content_type: MIME type (default: text/plain)
            encoding: Content encoding (default: utf-8)
            visibility: Visibility level (default: private)
            created_by_tool: Tool name for attribution
            created_by_model: Model name for attribution
            ttl_seconds: Time-to-live in seconds

        Returns:
            The created/updated ClipboardEntry

        Raises:
            PluggedInError: If the API request fails
            ValueError: If ttl_seconds is <= 0
        """
        payload = _build_clipboard_payload(
            value=value,
            name=name,
            content_type=content_type,
            encoding=encoding,
            visibility=visibility,
            created_by_tool=created_by_tool,
            created_by_model=created_by_model,
            ttl_seconds=ttl_seconds,
        )

        response = self.client.request("POST", "/api/clipboard", json=payload)
        result = _parse_entry_response(
            response.json(),
            error_msg="Failed to set clipboard entry",
            raise_on_failure=True,
        )
        # result is guaranteed non-None when raise_on_failure=True
        assert result is not None
        return result

    def push(
        self,
        value: str,
        content_type: str = "text/plain",
        encoding: Union[ClipboardEncoding, str] = ClipboardEncoding.UTF8,
        visibility: Union[ClipboardVisibility, str] = ClipboardVisibility.PRIVATE,
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Push a value to the indexed clipboard (auto-increment index).

        Args:
            value: Value to store
            content_type: MIME type (default: text/plain)
            encoding: Content encoding (default: utf-8)
            visibility: Visibility level (default: private)
            created_by_tool: Tool name for attribution
            created_by_model: Model name for attribution
            ttl_seconds: Time-to-live in seconds

        Returns:
            The created ClipboardEntry with assigned index

        Raises:
            PluggedInError: If the API request fails
            ValueError: If ttl_seconds is <= 0
        """
        payload = _build_clipboard_payload(
            value=value,
            content_type=content_type,
            encoding=encoding,
            visibility=visibility,
            created_by_tool=created_by_tool,
            created_by_model=created_by_model,
            ttl_seconds=ttl_seconds,
        )

        response = self.client.request("POST", "/api/clipboard/push", json=payload)
        result = _parse_entry_response(
            response.json(),
            error_msg="Failed to push to clipboard",
            raise_on_failure=True,
        )
        assert result is not None
        return result

    def pop(self) -> Optional[ClipboardEntry]:
        """Pop the last indexed entry from clipboard (LIFO).

        Returns:
            The popped ClipboardEntry, or None if clipboard is empty
        """
        response = self.client.request("POST", "/api/clipboard/pop")
        return _parse_entry_response(
            response.json(),
            error_msg="Failed to pop from clipboard",
            raise_on_failure=False,
        )

    def delete(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> int:
        """Delete a clipboard entry by name or index.

        Args:
            name: Entry name to delete
            idx: Entry index to delete

        Returns:
            Number of deleted entries (0 or 1)

        Raises:
            ValueError: If neither name nor idx is provided
        """
        # Use Pydantic model for validation
        request = ClipboardDeleteRequest(name=name, idx=idx)
        payload = _build_delete_payload(request)

        response = self.client.request("DELETE", "/api/clipboard", json=payload)
        return _parse_delete_response(response.json())

    def clear_all(self) -> ClearAllResult:
        """Clear all clipboard entries using bulk delete API.

        Returns:
            ClearAllResult with deleted count and status

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request(
            "DELETE",
            "/api/clipboard",
            json={"clearAll": True}
        )
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to clear clipboard"))

        deleted = data.get("deleted", 0)
        return ClearAllResult(deleted=deleted, failed=0)


# -----------------------------------------------------------------------------
# Asynchronous Clipboard Service
# -----------------------------------------------------------------------------


class AsyncClipboardService:
    """Asynchronous clipboard service for Plugged.in.

    Provides persistent key-value and stack-based storage for AI workflows.
    """

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def list(self) -> List[ClipboardEntry]:
        """List all clipboard entries.

        Returns:
            List of ClipboardEntry objects

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request("GET", "/api/clipboard")
        return _parse_list_response(response.json())

    async def get(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> Optional[ClipboardEntry]:
        """Get a clipboard entry by name or index.

        Args:
            name: Entry name for key-value lookup
            idx: Entry index for stack-based lookup

        Returns:
            ClipboardEntry if found, None if not found

        Raises:
            ValueError: If neither name nor idx is provided
        """
        filters = ClipboardGetFilters(name=name, idx=idx)
        params = _build_get_params(filters)

        response = await self.client.request("GET", "/api/clipboard", params=params)
        return _parse_entry_response(
            response.json(),
            error_msg="Failed to get clipboard entry",
            raise_on_failure=False,
        )

    async def set(
        self,
        name: str,
        value: str,
        content_type: str = "text/plain",
        encoding: Union[ClipboardEncoding, str] = ClipboardEncoding.UTF8,
        visibility: Union[ClipboardVisibility, str] = ClipboardVisibility.PRIVATE,
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Set a named clipboard entry (upsert).

        Args:
            name: Entry name
            value: Value to store
            content_type: MIME type (default: text/plain)
            encoding: Content encoding (default: utf-8)
            visibility: Visibility level (default: private)
            created_by_tool: Tool name for attribution
            created_by_model: Model name for attribution
            ttl_seconds: Time-to-live in seconds

        Returns:
            The created/updated ClipboardEntry

        Raises:
            PluggedInError: If the API request fails
            ValueError: If ttl_seconds is <= 0
        """
        payload = _build_clipboard_payload(
            value=value,
            name=name,
            content_type=content_type,
            encoding=encoding,
            visibility=visibility,
            created_by_tool=created_by_tool,
            created_by_model=created_by_model,
            ttl_seconds=ttl_seconds,
        )

        response = await self.client.request("POST", "/api/clipboard", json=payload)
        result = _parse_entry_response(
            response.json(),
            error_msg="Failed to set clipboard entry",
            raise_on_failure=True,
        )
        assert result is not None
        return result

    async def push(
        self,
        value: str,
        content_type: str = "text/plain",
        encoding: Union[ClipboardEncoding, str] = ClipboardEncoding.UTF8,
        visibility: Union[ClipboardVisibility, str] = ClipboardVisibility.PRIVATE,
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Push a value to the indexed clipboard (auto-increment index).

        Args:
            value: Value to store
            content_type: MIME type (default: text/plain)
            encoding: Content encoding (default: utf-8)
            visibility: Visibility level (default: private)
            created_by_tool: Tool name for attribution
            created_by_model: Model name for attribution
            ttl_seconds: Time-to-live in seconds

        Returns:
            The created ClipboardEntry with assigned index

        Raises:
            PluggedInError: If the API request fails
            ValueError: If ttl_seconds is <= 0
        """
        payload = _build_clipboard_payload(
            value=value,
            content_type=content_type,
            encoding=encoding,
            visibility=visibility,
            created_by_tool=created_by_tool,
            created_by_model=created_by_model,
            ttl_seconds=ttl_seconds,
        )

        response = await self.client.request("POST", "/api/clipboard/push", json=payload)
        result = _parse_entry_response(
            response.json(),
            error_msg="Failed to push to clipboard",
            raise_on_failure=True,
        )
        assert result is not None
        return result

    async def pop(self) -> Optional[ClipboardEntry]:
        """Pop the last indexed entry from clipboard (LIFO).

        Returns:
            The popped ClipboardEntry, or None if clipboard is empty
        """
        response = await self.client.request("POST", "/api/clipboard/pop")
        return _parse_entry_response(
            response.json(),
            error_msg="Failed to pop from clipboard",
            raise_on_failure=False,
        )

    async def delete(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> int:
        """Delete a clipboard entry by name or index.

        Args:
            name: Entry name to delete
            idx: Entry index to delete

        Returns:
            Number of deleted entries (0 or 1)

        Raises:
            ValueError: If neither name nor idx is provided
        """
        request = ClipboardDeleteRequest(name=name, idx=idx)
        payload = _build_delete_payload(request)

        response = await self.client.request("DELETE", "/api/clipboard", json=payload)
        return _parse_delete_response(response.json())

    async def clear_all(self) -> ClearAllResult:
        """Clear all clipboard entries using bulk delete API.

        Returns:
            ClearAllResult with deleted count and status

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request(
            "DELETE",
            "/api/clipboard",
            json={"clearAll": True}
        )
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to clear clipboard"))

        deleted = data.get("deleted", 0)
        return ClearAllResult(deleted=deleted, failed=0)
