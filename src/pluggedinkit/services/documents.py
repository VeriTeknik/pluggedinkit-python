"""Document service for Plugged.in SDK"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import (
    Document,
    DocumentFilters,
    DocumentListResponse,
    DocumentVersion,
    DocumentWithContent,
    SearchFilters,
    SearchResponse,
    UpdateDocumentRequest,
    UpdateDocumentResponse,
)

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class DocumentService:
    """Synchronous document service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def list(self, filters: Optional[DocumentFilters] = None) -> DocumentListResponse:
        """List documents with optional filters"""
        params = filters.model_dump(exclude_none=True) if filters else {}

        response = self.client.request("GET", "/api/documents", params=params)
        data = response.json()

        # Convert to response model
        return DocumentListResponse(**data)

    def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Search documents semantically"""
        payload = {
            "query": query,
            "limit": limit,
            "offset": offset,
        }

        if filters:
            payload["filters"] = filters.model_dump(exclude_none=True)

        response = self.client.request("POST", "/api/documents/search", json=payload)
        data = response.json()

        return SearchResponse(**data)

    def get(
        self,
        document_id: str,
        include_content: bool = False,
        include_versions: bool = False,
    ) -> Union[Document, DocumentWithContent]:
        """Get a single document by ID"""
        params = {}
        if include_content:
            params["includeContent"] = "true"
        if include_versions:
            params["includeVersions"] = "true"

        response = self.client.request("GET", f"/api/documents/{document_id}", params=params)
        data = response.json()

        if include_content and "content" in data:
            return DocumentWithContent(**data)
        return Document(**data)

    def update(
        self,
        document_id: str,
        request: UpdateDocumentRequest,
    ) -> UpdateDocumentResponse:
        """Update an existing document"""
        response = self.client.request(
            "PATCH",
            f"/api/documents/{document_id}",
            json=request.model_dump(exclude_none=True),
        )
        data = response.json()

        return UpdateDocumentResponse(**data)

    def delete(self, document_id: str) -> None:
        """Delete a document"""
        self.client.request("DELETE", f"/api/documents/{document_id}")

    def download(
        self,
        document_id: str,
        project_uuid: Optional[str] = None,
    ) -> bytes:
        """Download a document file"""
        params = {}
        if project_uuid:
            params["projectUuid"] = project_uuid

        response = self.client.request(
            "GET",
            f"/api/library/download/{document_id}",
            params=params,
        )

        return response.content

    def get_versions(self, document_id: str) -> List[DocumentVersion]:
        """Get document versions"""
        params = {"includeVersions": "true"}

        response = self.client.request("GET", f"/api/documents/{document_id}", params=params)
        data = response.json()

        versions = data.get("versions", [])
        return [DocumentVersion(**v) for v in versions]

    def get_version(
        self,
        document_id: str,
        version_number: int,
    ) -> DocumentWithContent:
        """Get a specific version of a document"""
        response = self.client.request(
            "GET",
            f"/api/documents/{document_id}/versions/{version_number}",
        )
        data = response.json()

        return DocumentWithContent(**data)

    def create(
        self,
        title: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> Document:
        """Create a new AI-generated document"""
        payload = {
            "title": title,
            "content": content,
            "format": metadata.get("format", "md"),
            "category": metadata.get("category", "other"),
            "tags": metadata.get("tags", []),
            "metadata": metadata,
        }

        response = self.client.request("POST", "/api/documents/ai", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to create document"))

        return Document(**data["document"])


class AsyncDocumentService:
    """Asynchronous document service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def list(self, filters: Optional[DocumentFilters] = None) -> DocumentListResponse:
        """List documents with optional filters"""
        params = filters.model_dump(exclude_none=True) if filters else {}

        response = await self.client.request("GET", "/api/documents", params=params)
        data = response.json()

        return DocumentListResponse(**data)

    async def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> SearchResponse:
        """Search documents semantically"""
        payload = {
            "query": query,
            "limit": limit,
            "offset": offset,
        }

        if filters:
            payload["filters"] = filters.model_dump(exclude_none=True)

        response = await self.client.request("POST", "/api/documents/search", json=payload)
        data = response.json()

        return SearchResponse(**data)

    async def get(
        self,
        document_id: str,
        include_content: bool = False,
        include_versions: bool = False,
    ) -> Union[Document, DocumentWithContent]:
        """Get a single document by ID"""
        params = {}
        if include_content:
            params["includeContent"] = "true"
        if include_versions:
            params["includeVersions"] = "true"

        response = await self.client.request("GET", f"/api/documents/{document_id}", params=params)
        data = response.json()

        if include_content and "content" in data:
            return DocumentWithContent(**data)
        return Document(**data)

    async def update(
        self,
        document_id: str,
        request: UpdateDocumentRequest,
    ) -> UpdateDocumentResponse:
        """Update an existing document"""
        response = await self.client.request(
            "PATCH",
            f"/api/documents/{document_id}",
            json=request.model_dump(exclude_none=True),
        )
        data = response.json()

        return UpdateDocumentResponse(**data)

    async def delete(self, document_id: str) -> None:
        """Delete a document"""
        await self.client.request("DELETE", f"/api/documents/{document_id}")

    async def download(
        self,
        document_id: str,
        project_uuid: Optional[str] = None,
    ) -> bytes:
        """Download a document file"""
        params = {}
        if project_uuid:
            params["projectUuid"] = project_uuid

        response = await self.client.request(
            "GET",
            f"/api/library/download/{document_id}",
            params=params,
        )

        return response.content

    async def get_versions(self, document_id: str) -> List[DocumentVersion]:
        """Get document versions"""
        params = {"includeVersions": "true"}

        response = await self.client.request("GET", f"/api/documents/{document_id}", params=params)
        data = response.json()

        versions = data.get("versions", [])
        return [DocumentVersion(**v) for v in versions]

    async def get_version(
        self,
        document_id: str,
        version_number: int,
    ) -> DocumentWithContent:
        """Get a specific version of a document"""
        response = await self.client.request(
            "GET",
            f"/api/documents/{document_id}/versions/{version_number}",
        )
        data = response.json()

        return DocumentWithContent(**data)

    async def create(
        self,
        title: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> Document:
        """Create a new AI-generated document"""
        payload = {
            "title": title,
            "content": content,
            "format": metadata.get("format", "md"),
            "category": metadata.get("category", "other"),
            "tags": metadata.get("tags", []),
            "metadata": metadata,
        }

        response = await self.client.request("POST", "/api/documents/ai", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to create document"))

        return Document(**data["document"])