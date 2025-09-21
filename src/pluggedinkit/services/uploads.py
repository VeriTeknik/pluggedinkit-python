"""Upload service for Plugged.in SDK"""

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Callable, Dict, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import Document, UploadMetadata, UploadProgress, UploadResponse

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class UploadService:
    """Synchronous upload service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client
        self.upload_trackers: Dict[str, bool] = {}

    def upload_file(
        self,
        file: Union[BinaryIO, bytes, Path],
        metadata: Dict[str, Any],
        on_progress: Optional[Callable[[int], None]] = None,
    ) -> UploadResponse:
        """Upload a file to the library"""
        # Prepare file for upload
        if isinstance(file, Path):
            with open(file, "rb") as f:
                file_data = f.read()
            file_name = file.name
        elif isinstance(file, bytes):
            file_data = file
            file_name = metadata.get("name", "upload.bin")
        else:
            file_data = file.read()
            file_name = metadata.get("name", getattr(file, "name", "upload.bin"))

        # Prepare form data
        files = {
            "file": (file_name, file_data),
        }

        # Add metadata fields
        form_data = {
            "name": metadata.get("name", file_name),
        }

        if "description" in metadata:
            form_data["description"] = metadata["description"]
        if "tags" in metadata:
            form_data["tags"] = ",".join(metadata["tags"])
        if "purpose" in metadata:
            form_data["purpose"] = metadata["purpose"]
        if "relatedTo" in metadata:
            form_data["relatedTo"] = metadata["relatedTo"]
        if "notes" in metadata:
            form_data["notes"] = metadata["notes"]

        # Make upload request
        response = self.client.request(
            "POST",
            "/api/library/upload",
            files=files,
            params=form_data,
        )
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload file"))

        return UploadResponse(**data)

    def upload_document(
        self,
        content: str,
        metadata: UploadMetadata,
    ) -> Document:
        """Upload a document with content directly (for AI-generated content)"""
        payload = {
            "title": metadata.title,
            "content": content,
            "description": metadata.description,
            "tags": metadata.tags,
            "category": metadata.category,
            "format": metadata.format or "md",
            "metadata": metadata.metadata,
        }

        response = self.client.request("POST", "/api/documents", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload document"))

        return Document(**data["document"])

    def upload_batch(
        self,
        files: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> List[UploadResponse]:
        """Upload multiple files in batch"""
        results = []
        total = len(files)

        for i, file_info in enumerate(files):
            try:
                result = self.upload_file(
                    file_info["file"],
                    file_info["metadata"],
                )
                results.append(result)

                if on_progress:
                    on_progress(i + 1, total)
            except Exception as e:
                results.append(
                    UploadResponse(
                        success=False,
                        error=str(e),
                    )
                )

                if on_progress:
                    on_progress(i + 1, total)

        return results

    def check_upload_status(self, upload_id: str) -> UploadProgress:
        """Check upload status"""
        response = self.client.request("GET", f"/api/upload-status/{upload_id}")
        data = response.json()

        return UploadProgress(
            upload_id=upload_id,
            status=data.get("status", "pending"),
            progress=data.get("progress"),
            message=data.get("message"),
            error=data.get("error"),
        )

    def track_upload(
        self,
        upload_id: str,
        on_update: Callable[[UploadProgress], None],
        poll_interval: float = 1.0,
    ) -> None:
        """Track upload progress with polling"""
        self.upload_trackers[upload_id] = True

        while self.upload_trackers.get(upload_id):
            try:
                status = self.check_upload_status(upload_id)
                on_update(status)

                if status.status in ["completed", "failed"]:
                    self.stop_tracking(upload_id)
                    break

                import time
                time.sleep(poll_interval)
            except Exception as e:
                on_update(
                    UploadProgress(
                        upload_id=upload_id,
                        status="failed",
                        error=str(e),
                    )
                )
                self.stop_tracking(upload_id)
                break

    def stop_tracking(self, upload_id: str) -> None:
        """Stop tracking an upload"""
        self.upload_trackers.pop(upload_id, None)

    def stop_all_tracking(self) -> None:
        """Stop tracking all uploads"""
        self.upload_trackers.clear()


class AsyncUploadService:
    """Asynchronous upload service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client
        self.upload_trackers: Dict[str, bool] = {}

    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, Path],
        metadata: Dict[str, Any],
        on_progress: Optional[Callable[[int], None]] = None,
    ) -> UploadResponse:
        """Upload a file to the library"""
        # Prepare file for upload
        if isinstance(file, Path):
            with open(file, "rb") as f:
                file_data = f.read()
            file_name = file.name
        elif isinstance(file, bytes):
            file_data = file
            file_name = metadata.get("name", "upload.bin")
        else:
            file_data = file.read()
            file_name = metadata.get("name", getattr(file, "name", "upload.bin"))

        # Prepare form data
        files = {
            "file": (file_name, file_data),
        }

        # Add metadata fields
        form_data = {
            "name": metadata.get("name", file_name),
        }

        if "description" in metadata:
            form_data["description"] = metadata["description"]
        if "tags" in metadata:
            form_data["tags"] = ",".join(metadata["tags"])
        if "purpose" in metadata:
            form_data["purpose"] = metadata["purpose"]
        if "relatedTo" in metadata:
            form_data["relatedTo"] = metadata["relatedTo"]
        if "notes" in metadata:
            form_data["notes"] = metadata["notes"]

        # Make upload request
        response = await self.client.request(
            "POST",
            "/api/library/upload",
            files=files,
            params=form_data,
        )
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload file"))

        return UploadResponse(**data)

    async def upload_document(
        self,
        content: str,
        metadata: UploadMetadata,
    ) -> Document:
        """Upload a document with content directly (for AI-generated content)"""
        payload = {
            "title": metadata.title,
            "content": content,
            "description": metadata.description,
            "tags": metadata.tags,
            "category": metadata.category,
            "format": metadata.format or "md",
            "metadata": metadata.metadata,
        }

        response = await self.client.request("POST", "/api/documents", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to upload document"))

        return Document(**data["document"])

    async def upload_batch(
        self,
        files: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> List[UploadResponse]:
        """Upload multiple files in batch"""
        results = []
        total = len(files)

        for i, file_info in enumerate(files):
            try:
                result = await self.upload_file(
                    file_info["file"],
                    file_info["metadata"],
                )
                results.append(result)

                if on_progress:
                    on_progress(i + 1, total)
            except Exception as e:
                results.append(
                    UploadResponse(
                        success=False,
                        error=str(e),
                    )
                )

                if on_progress:
                    on_progress(i + 1, total)

        return results

    async def check_upload_status(self, upload_id: str) -> UploadProgress:
        """Check upload status"""
        response = await self.client.request("GET", f"/api/upload-status/{upload_id}")
        data = response.json()

        return UploadProgress(
            upload_id=upload_id,
            status=data.get("status", "pending"),
            progress=data.get("progress"),
            message=data.get("message"),
            error=data.get("error"),
        )

    async def track_upload(
        self,
        upload_id: str,
        on_update: Callable[[UploadProgress], None],
        poll_interval: float = 1.0,
    ) -> None:
        """Track upload progress with polling"""
        self.upload_trackers[upload_id] = True

        while self.upload_trackers.get(upload_id):
            try:
                status = await self.check_upload_status(upload_id)
                on_update(status)

                if status.status in ["completed", "failed"]:
                    self.stop_tracking(upload_id)
                    break

                await asyncio.sleep(poll_interval)
            except Exception as e:
                on_update(
                    UploadProgress(
                        upload_id=upload_id,
                        status="failed",
                        error=str(e),
                    )
                )
                self.stop_tracking(upload_id)
                break

    def stop_tracking(self, upload_id: str) -> None:
        """Stop tracking an upload"""
        self.upload_trackers.pop(upload_id, None)

    def stop_all_tracking(self) -> None:
        """Stop tracking all uploads"""
        self.upload_trackers.clear()