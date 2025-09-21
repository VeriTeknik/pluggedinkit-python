"""RAG service for Plugged.in SDK"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..exceptions import PluggedInError
from ..types import RagResponse, RagSourceDocument

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class RagService:
    """Synchronous RAG service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def query(self, query: str, project_uuid: Optional[str] = None) -> RagResponse:
        """Query the knowledge base with a natural language question"""
        payload = {"query": query}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        # Try library endpoint first, fallback to documents endpoint
        try:
            response = self.client.request("POST", "/api/library/rag/query", json=payload)
        except Exception:
            if self.client.debug:
                print("[PluggedIn SDK] Falling back to documents RAG endpoint")
            response = self.client.request("POST", "/api/documents/rag/query", json=payload)

        data = response.json()
        return self._transform_rag_response(data)

    def ask_question(self, query: str, project_uuid: Optional[str] = None) -> str:
        """Query knowledge base and get only the answer text"""
        response = self.query(query, project_uuid)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return response.answer

    def query_with_sources(
        self, query: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Query knowledge base and get answer with source documents"""
        response = self.query(query, project_uuid)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return {
            "answer": response.answer,
            "sources": response.documents or [],
        }

    def find_relevant_documents(
        self,
        query: str,
        project_uuid: Optional[str] = None,
        limit: int = 5,
    ) -> List[RagSourceDocument]:
        """Get relevant documents for a query without generating an answer"""
        payload = {
            "query": query,
            "limit": limit,
            "returnAnswer": False,
        }
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = self.client.request("POST", "/api/documents/rag/search", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to search documents"))

        documents = data.get("documents", [])
        return [RagSourceDocument(**doc) for doc in documents]

    def check_availability(self) -> Dict[str, any]:
        """Check if RAG is available and configured"""
        try:
            response = self.client.request("GET", "/api/rag/health")
            data = response.json()
            return {
                "available": data.get("available", False),
                "message": data.get("message"),
            }
        except Exception:
            return {
                "available": False,
                "message": "RAG service is not available",
            }

    def get_storage_stats(self, project_uuid: Optional[str] = None) -> Dict[str, any]:
        """Get RAG storage statistics"""
        params = {"projectUuid": project_uuid} if project_uuid else {}
        response = self.client.request("GET", "/api/rag/stats", params=params)
        data = response.json()

        return {
            "document_count": data.get("documentCount", 0),
            "total_size": data.get("totalSize", 0),
            "vector_count": data.get("vectorCount"),
            "last_updated": data.get("lastUpdated"),
        }

    def refresh_document(
        self, document_id: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Refresh RAG index for a specific document"""
        payload = {}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = self.client.request(
            "POST", f"/api/rag/refresh/{document_id}", json=payload
        )
        data = response.json()

        return {
            "success": data.get("success", False),
            "message": data.get("message"),
        }

    def remove_document(
        self, document_id: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Remove a document from the RAG index"""
        payload = {}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = self.client.request(
            "DELETE", f"/api/rag/documents/{document_id}", json=payload
        )
        data = response.json()

        return {
            "success": data.get("success", False),
            "message": data.get("message"),
        }

    def _transform_rag_response(self, data: Dict) -> RagResponse:
        """Transform API response to RagResponse type"""
        if "success" in data:
            return RagResponse(**data)

        # Transform legacy format
        if "answer" in data or "results" in data:
            return RagResponse(
                success=True,
                answer=data.get("answer") or data.get("results"),
                sources=data.get("sources", []),
                document_ids=data.get("documentIds") or data.get("document_ids", []),
                documents=data.get("documents", []),
            )

        # Error response
        return RagResponse(
            success=False,
            error=data.get("error", "Unknown error occurred"),
        )


class AsyncRagService:
    """Asynchronous RAG service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def query(self, query: str, project_uuid: Optional[str] = None) -> RagResponse:
        """Query the knowledge base with a natural language question"""
        payload = {"query": query}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        # Try library endpoint first, fallback to documents endpoint
        try:
            response = await self.client.request("POST", "/api/library/rag/query", json=payload)
        except Exception:
            if self.client.debug:
                print("[PluggedIn SDK] Falling back to documents RAG endpoint")
            response = await self.client.request("POST", "/api/documents/rag/query", json=payload)

        data = response.json()
        return self._transform_rag_response(data)

    async def ask_question(self, query: str, project_uuid: Optional[str] = None) -> str:
        """Query knowledge base and get only the answer text"""
        response = await self.query(query, project_uuid)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return response.answer

    async def query_with_sources(
        self, query: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Query knowledge base and get answer with source documents"""
        response = await self.query(query, project_uuid)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return {
            "answer": response.answer,
            "sources": response.documents or [],
        }

    async def find_relevant_documents(
        self,
        query: str,
        project_uuid: Optional[str] = None,
        limit: int = 5,
    ) -> List[RagSourceDocument]:
        """Get relevant documents for a query without generating an answer"""
        payload = {
            "query": query,
            "limit": limit,
            "returnAnswer": False,
        }
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = await self.client.request("POST", "/api/documents/rag/search", json=payload)
        data = response.json()

        if not data.get("success"):
            raise PluggedInError(data.get("error", "Failed to search documents"))

        documents = data.get("documents", [])
        return [RagSourceDocument(**doc) for doc in documents]

    async def check_availability(self) -> Dict[str, any]:
        """Check if RAG is available and configured"""
        try:
            response = await self.client.request("GET", "/api/rag/health")
            data = response.json()
            return {
                "available": data.get("available", False),
                "message": data.get("message"),
            }
        except Exception:
            return {
                "available": False,
                "message": "RAG service is not available",
            }

    async def get_storage_stats(self, project_uuid: Optional[str] = None) -> Dict[str, any]:
        """Get RAG storage statistics"""
        params = {"projectUuid": project_uuid} if project_uuid else {}
        response = await self.client.request("GET", "/api/rag/stats", params=params)
        data = response.json()

        return {
            "document_count": data.get("documentCount", 0),
            "total_size": data.get("totalSize", 0),
            "vector_count": data.get("vectorCount"),
            "last_updated": data.get("lastUpdated"),
        }

    async def refresh_document(
        self, document_id: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Refresh RAG index for a specific document"""
        payload = {}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = await self.client.request(
            "POST", f"/api/rag/refresh/{document_id}", json=payload
        )
        data = response.json()

        return {
            "success": data.get("success", False),
            "message": data.get("message"),
        }

    async def remove_document(
        self, document_id: str, project_uuid: Optional[str] = None
    ) -> Dict[str, any]:
        """Remove a document from the RAG index"""
        payload = {}
        if project_uuid:
            payload["projectUuid"] = project_uuid

        response = await self.client.request(
            "DELETE", f"/api/rag/documents/{document_id}", json=payload
        )
        data = response.json()

        return {
            "success": data.get("success", False),
            "message": data.get("message"),
        }

    def _transform_rag_response(self, data: Dict) -> RagResponse:
        """Transform API response to RagResponse type"""
        if "success" in data:
            return RagResponse(**data)

        # Transform legacy format
        if "answer" in data or "results" in data:
            return RagResponse(
                success=True,
                answer=data.get("answer") or data.get("results"),
                sources=data.get("sources", []),
                document_ids=data.get("documentIds") or data.get("document_ids", []),
                documents=data.get("documents", []),
            )

        # Error response
        return RagResponse(
            success=False,
            error=data.get("error", "Unknown error occurred"),
        )