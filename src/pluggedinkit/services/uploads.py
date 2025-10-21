"""Upload service for Plugged.in SDK"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import DocumentWithContent, UploadMetadata, UploadResponse

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class UploadService:
    """Synchronous upload service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def upload_file(
        self,
        file: Union[BinaryIO, bytes, Path],
        metadata: Dict[str, Any],
        on_progress: Optional[Any] = None,
    ) -> UploadResponse:
        """Binary uploads are no longer exposed via the public API."""
        raise PluggedInError(
            "Binary file uploads are no longer supported via the API. "
            "Please use the Plugged.in web interface or forthcoming upload workflow."
        )

    def upload_document(
        self,
        content: str,
        metadata: UploadMetadata,
    ) -> DocumentWithContent:
        """Upload an AI generated document."""
        payload = {
            "title": metadata.title,
            "content": content,
            "description": metadata.description,
            "tags": metadata.tags,
            "category": metadata.category,
            "format": metadata.format or "md",
            "metadata": metadata.metadata,
        }

        response = self.client.request("POST", "/api/documents/ai", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload document"))

        document_id = data.get("documentId")
        if not document_id:
            raise PluggedInError("Server did not return a document id")

        document_response = self.client.request(
            "GET",
            f"/api/documents/{document_id}",
            params={"includeContent": "true"},
        )
        document_data = document_response.json()
        return DocumentWithContent(**document_data)

    def upload_batch(
        self,
        files: List[Dict[str, Any]],
        on_progress: Optional[Any] = None,
    ) -> List[UploadResponse]:
        """Batch uploads are no longer supported."""
        raise PluggedInError(
            "Batch uploads are no longer supported via the API."
        )

    def check_upload_status(self, upload_id: str) -> UploadResponse:
        """Legacy upload tracking has been removed."""
        raise PluggedInError(
            "Upload status tracking is no longer available via the API."
        )

    def track_upload(
        self,
        upload_id: str,
        on_update: Any,
        poll_interval: float = 1.0,
    ) -> None:
        """Legacy upload tracking has been removed."""
        raise PluggedInError(
            "Upload status tracking is no longer available via the API."
        )

    def stop_tracking(self, upload_id: str) -> None:  # pragma: no cover - noop
        """No-op retained for backwards compatibility."""

    def stop_all_tracking(self) -> None:  # pragma: no cover - noop
        """No-op retained for backwards compatibility."""


class AsyncUploadService:
    """Asynchronous upload service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, Path],
        metadata: Dict[str, Any],
        on_progress: Optional[Any] = None,
    ) -> UploadResponse:
        """Binary uploads are no longer exposed via the public API."""
        raise PluggedInError(
            "Binary file uploads are no longer supported via the API. "
            "Please use the Plugged.in web interface or forthcoming upload workflow."
        )

    async def upload_document(
        self,
        content: str,
        metadata: UploadMetadata,
    ) -> DocumentWithContent:
        """Upload an AI generated document."""
        payload = {
            "title": metadata.title,
            "content": content,
            "description": metadata.description,
            "tags": metadata.tags,
            "category": metadata.category,
            "format": metadata.format or "md",
            "metadata": metadata.metadata,
        }

        response = await self.client.request("POST", "/api/documents/ai", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload document"))

        document_id = data.get("documentId")
        if not document_id:
            raise PluggedInError("Server did not return a document id")

        document_response = await self.client.request(
            "GET",
            f"/api/documents/{document_id}",
            params={"includeContent": "true"},
        )
        document_data = document_response.json()
        return DocumentWithContent(**document_data)

    async def upload_batch(
        self,
        files: List[Dict[str, Any]],
        on_progress: Optional[Any] = None,
    ) -> List[UploadResponse]:
        """Batch uploads are no longer supported."""
        raise PluggedInError(
            "Batch uploads are no longer supported via the API."
        )

    async def check_upload_status(self, upload_id: str) -> UploadResponse:
        """Legacy upload tracking has been removed."""
        raise PluggedInError(
            "Upload status tracking is no longer available via the API."
        )

    async def track_upload(
        self,
        upload_id: str,
        on_update: Any,
        poll_interval: float = 1.0,
    ) -> None:
        """Legacy upload tracking has been removed."""
        raise PluggedInError(
            "Upload status tracking is no longer available via the API."
        )

    def stop_tracking(self, upload_id: str) -> None:  # pragma: no cover - noop
        """No-op retained for backwards compatibility."""

    def stop_all_tracking(self) -> None:  # pragma: no cover - noop
        """No-op retained for backwards compatibility."""
