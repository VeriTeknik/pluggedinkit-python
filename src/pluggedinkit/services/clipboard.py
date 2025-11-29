"""Clipboard service for Plugged.in SDK"""

from typing import TYPE_CHECKING, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import (
    ClipboardDeleteRequest,
    ClipboardDeleteResponse,
    ClipboardEntry,
    ClipboardGetFilters,
    ClipboardListResponse,
    ClipboardPushRequest,
    ClipboardResponse,
    ClipboardSetRequest,
)

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class ClipboardService:
    """Synchronous clipboard service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def list(self) -> List[ClipboardEntry]:
        """List all clipboard entries"""
        response = self.client.request("GET", "/api/clipboard")
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to list clipboard entries"))

        list_response = ClipboardListResponse(**data)
        return list_response.entries

    def get(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> Optional[ClipboardEntry]:
        """Get a clipboard entry by name or index"""
        if name is None and idx is None:
            raise ValueError("Either 'name' or 'idx' must be provided")

        params = {}
        if name is not None:
            params["name"] = name
        if idx is not None:
            params["idx"] = str(idx)

        response = self.client.request("GET", "/api/clipboard", params=params)
        data = response.json()

        if not data.get("success"):
            return None

        if "entry" in data and data["entry"]:
            return ClipboardEntry(**data["entry"])
        return None

    def set(
        self,
        name: str,
        value: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
        visibility: str = "private",
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Set a named clipboard entry (upsert)"""
        payload = {
            "name": name,
            "value": value,
            "contentType": content_type,
            "encoding": encoding,
            "visibility": visibility,
            "source": "sdk",  # Hardcoded: SDK always uses 'sdk' source
        }

        if created_by_tool:
            payload["createdByTool"] = created_by_tool
        if created_by_model:
            payload["createdByModel"] = created_by_model
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be greater than 0 when provided")
            payload["ttlSeconds"] = ttl_seconds

        response = self.client.request("POST", "/api/clipboard", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to set clipboard entry"))

        return ClipboardEntry(**data["entry"])

    def push(
        self,
        value: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
        visibility: str = "private",
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Push a value to the indexed clipboard (auto-increment index)"""
        payload = {
            "value": value,
            "contentType": content_type,
            "encoding": encoding,
            "visibility": visibility,
            "source": "sdk",  # Hardcoded: SDK always uses 'sdk' source
        }

        if created_by_tool:
            payload["createdByTool"] = created_by_tool
        if created_by_model:
            payload["createdByModel"] = created_by_model
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be greater than 0 when provided")
            payload["ttlSeconds"] = ttl_seconds

        response = self.client.request("POST", "/api/clipboard/push", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to push to clipboard"))

        return ClipboardEntry(**data["entry"])

    def pop(self) -> Optional[ClipboardEntry]:
        """Pop the last indexed entry from clipboard"""
        response = self.client.request("POST", "/api/clipboard/pop")
        data = response.json()

        if not data.get("success") or not data.get("entry"):
            return None

        return ClipboardEntry(**data["entry"])

    def delete(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> bool:
        """Delete a clipboard entry by name or index"""
        if name is None and idx is None:
            raise ValueError("Either 'name' or 'idx' must be provided")

        payload = {}
        if name is not None:
            payload["name"] = name
        if idx is not None:
            payload["idx"] = idx

        response = self.client.request("DELETE", "/api/clipboard", json=payload)
        data = response.json()

        return data.get("success", False) and data.get("deleted", False)

    def clear_all(self) -> int:
        """Clear all clipboard entries. Returns count of deleted entries."""
        entries = self.list()
        deleted = 0

        for entry in entries:
            try:
                success = False
                if entry.name:
                    success = self.delete(name=entry.name)
                elif entry.idx is not None:
                    success = self.delete(idx=entry.idx)
                if success:
                    deleted += 1
            except PluggedInError:
                pass

        return deleted


class AsyncClipboardService:
    """Asynchronous clipboard service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def list(self) -> List[ClipboardEntry]:
        """List all clipboard entries"""
        response = await self.client.request("GET", "/api/clipboard")
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to list clipboard entries"))

        list_response = ClipboardListResponse(**data)
        return list_response.entries

    async def get(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> Optional[ClipboardEntry]:
        """Get a clipboard entry by name or index"""
        if name is None and idx is None:
            raise ValueError("Either 'name' or 'idx' must be provided")

        params = {}
        if name is not None:
            params["name"] = name
        if idx is not None:
            params["idx"] = str(idx)

        response = await self.client.request("GET", "/api/clipboard", params=params)
        data = response.json()

        if not data.get("success"):
            return None

        if "entry" in data and data["entry"]:
            return ClipboardEntry(**data["entry"])
        return None

    async def set(
        self,
        name: str,
        value: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
        visibility: str = "private",
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Set a named clipboard entry (upsert)"""
        payload = {
            "name": name,
            "value": value,
            "contentType": content_type,
            "encoding": encoding,
            "visibility": visibility,
            "source": "sdk",  # Hardcoded: SDK always uses 'sdk' source
        }

        if created_by_tool:
            payload["createdByTool"] = created_by_tool
        if created_by_model:
            payload["createdByModel"] = created_by_model
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be greater than 0 when provided")
            payload["ttlSeconds"] = ttl_seconds

        response = await self.client.request("POST", "/api/clipboard", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to set clipboard entry"))

        return ClipboardEntry(**data["entry"])

    async def push(
        self,
        value: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
        visibility: str = "private",
        created_by_tool: Optional[str] = None,
        created_by_model: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> ClipboardEntry:
        """Push a value to the indexed clipboard (auto-increment index)"""
        payload = {
            "value": value,
            "contentType": content_type,
            "encoding": encoding,
            "visibility": visibility,
            "source": "sdk",  # Hardcoded: SDK always uses 'sdk' source
        }

        if created_by_tool:
            payload["createdByTool"] = created_by_tool
        if created_by_model:
            payload["createdByModel"] = created_by_model
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be greater than 0 when provided")
            payload["ttlSeconds"] = ttl_seconds

        response = await self.client.request("POST", "/api/clipboard/push", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to push to clipboard"))

        return ClipboardEntry(**data["entry"])

    async def pop(self) -> Optional[ClipboardEntry]:
        """Pop the last indexed entry from clipboard"""
        response = await self.client.request("POST", "/api/clipboard/pop")
        data = response.json()

        if not data.get("success") or not data.get("entry"):
            return None

        return ClipboardEntry(**data["entry"])

    async def delete(
        self,
        name: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> bool:
        """Delete a clipboard entry by name or index"""
        if name is None and idx is None:
            raise ValueError("Either 'name' or 'idx' must be provided")

        payload = {}
        if name is not None:
            payload["name"] = name
        if idx is not None:
            payload["idx"] = idx

        response = await self.client.request("DELETE", "/api/clipboard", json=payload)
        data = response.json()

        return data.get("success", False) and data.get("deleted", False)

    async def clear_all(self) -> int:
        """Clear all clipboard entries. Returns count of deleted entries."""
        entries = await self.list()
        deleted = 0

        for entry in entries:
            try:
                success = False
                if entry.name:
                    success = await self.delete(name=entry.name)
                elif entry.idx is not None:
                    success = await self.delete(idx=entry.idx)
                if success:
                    deleted += 1
            except PluggedInError:
                pass

        return deleted
