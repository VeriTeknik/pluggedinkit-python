"""RAG service for Plugged.in SDK"""

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from ..exceptions import PluggedInError
from ..types import RagResponse, RagSourceDocument, RagStorageStats

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


class RagService:
    """Synchronous RAG service"""

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def query(self, query: str, include_metadata: bool = True) -> RagResponse:
        """Query the knowledge base with a natural language question"""
        payload = {
            "query": query,
            "includeMetadata": include_metadata,
        }

        response = self.client.request("POST", "/api/rag/query", json=payload)
        data = self._parse_rag_response(response)
        return self._transform_rag_response(data)

    def ask_question(self, query: str) -> str:
        """Query knowledge base and get only the answer text"""
        response = self.query(query, include_metadata=False)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return response.answer

    def query_with_sources(self, query: str) -> Dict[str, Union[str, List[RagSourceDocument]]]:
        """Query knowledge base and get answer with source documents"""
        response = self.query(query, include_metadata=True)

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
        limit: int = 5,
    ) -> List[RagSourceDocument]:
        """Get relevant documents for a query without generating an answer"""
        response = self.query(query, include_metadata=True)

        if not response.success:
            raise PluggedInError(response.error or "Failed to search documents")

        documents = response.documents or []
        return documents[:limit]

    def check_availability(self) -> Dict[str, Union[bool, Optional[str]]]:
        """Check if RAG is available and configured"""
        try:
            self.query("__pluggedin_health_check__", include_metadata=False)
            return {"available": True}
        except Exception as exc:  # pragma: no cover - best effort
            return {
                "available": False,
                "message": str(exc),
            }

    def get_storage_stats(self, user_id: str) -> RagStorageStats:
        """Get RAG storage statistics for the authenticated user"""
        if not user_id:
            raise PluggedInError("user_id is required to fetch storage statistics")

        response = self.client.request(
            "GET",
            "/api/rag/storage-stats",
            params={"user_id": user_id},
        )
        data = response.json()

        return RagStorageStats(
            documents_count=data.get("documents_count", 0),
            total_chunks=data.get("total_chunks", 0),
            estimated_storage_mb=data.get("estimated_storage_mb", 0.0),
            vectors_count=data.get("vectors_count"),
            embedding_dimension=data.get("embedding_dimension"),
            is_estimate=data.get("is_estimate", True),
        )

    def refresh_document(self, *args, **kwargs) -> None:
        """Legacy refresh flow is no longer exposed via the public API."""
        raise PluggedInError(
            "Document refresh is no longer available via the public API."
        )

    def remove_document(self, *args, **kwargs) -> None:
        """Legacy remove flow is no longer exposed via the public API."""
        raise PluggedInError(
            "Document removal is no longer available via the public API."
        )

    def _parse_rag_response(self, response) -> Union[str, Dict]:
        """Best-effort parsing for RAG responses that may return text or JSON."""
        try:
            return response.json()
        except ValueError:
            return response.text

    def _transform_rag_response(self, data: Union[str, Dict]) -> RagResponse:
        """Transform API response to RagResponse type"""
        if isinstance(data, str):
            return RagResponse(
                success=True,
                answer=data,
                sources=[],
                document_ids=[],
                documents=[],
            )

        if not isinstance(data, dict):
            return RagResponse(
                success=False,
                error="Unexpected response format from RAG query endpoint",
            )

        answer = (
            data.get("answer")
            or data.get("response")
            or data.get("results")
            or data.get("message")
            or ""
        )

        sources = data.get("sources") or []
        document_ids = data.get("documentIds") or data.get("document_ids") or []

        documents = [
            RagSourceDocument(
                id=document_id,
                name=sources[index] if index < len(sources) else f"Document {index + 1}",
            )
            for index, document_id in enumerate(document_ids)
        ]

        return RagResponse(
            success=data.get("success", True),
            answer=answer,
            sources=sources,
            document_ids=document_ids,
            documents=documents,
            error=data.get("error"),
        )


class AsyncRagService:
    """Asynchronous RAG service"""

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def query(self, query: str, include_metadata: bool = True) -> RagResponse:
        """Query the knowledge base with a natural language question"""
        payload = {
            "query": query,
            "includeMetadata": include_metadata,
        }

        response = await self.client.request("POST", "/api/rag/query", json=payload)
        data = self._parse_rag_response(response)
        return self._transform_rag_response(data)

    async def ask_question(self, query: str) -> str:
        """Query knowledge base and get only the answer text"""
        response = await self.query(query, include_metadata=False)

        if not response.success or not response.answer:
            raise PluggedInError(
                response.error or "No answer received from knowledge base"
            )

        return response.answer

    async def query_with_sources(
        self,
        query: str,
    ) -> Dict[str, Union[str, List[RagSourceDocument]]]:
        """Query knowledge base and get answer with source documents"""
        response = await self.query(query, include_metadata=True)

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
        limit: int = 5,
    ) -> List[RagSourceDocument]:
        """Get relevant documents for a query without generating an answer"""
        response = await self.query(query, include_metadata=True)

        if not response.success:
            raise PluggedInError(response.error or "Failed to search documents")

        documents = response.documents or []
        return documents[:limit]

    async def check_availability(self) -> Dict[str, Union[bool, Optional[str]]]:
        """Check if RAG is available and configured"""
        try:
            await self.query("__pluggedin_health_check__", include_metadata=False)
            return {"available": True}
        except Exception as exc:  # pragma: no cover - best effort
            return {
                "available": False,
                "message": str(exc),
            }

    async def get_storage_stats(self, user_id: str) -> RagStorageStats:
        """Get RAG storage statistics for the authenticated user"""
        if not user_id:
            raise PluggedInError("user_id is required to fetch storage statistics")

        response = await self.client.request(
            "GET",
            "/api/rag/storage-stats",
            params={"user_id": user_id},
        )
        data = response.json()

        return RagStorageStats(
            documents_count=data.get("documents_count", 0),
            total_chunks=data.get("total_chunks", 0),
            estimated_storage_mb=data.get("estimated_storage_mb", 0.0),
            vectors_count=data.get("vectors_count"),
            embedding_dimension=data.get("embedding_dimension"),
            is_estimate=data.get("is_estimate", True),
        )

    async def refresh_document(self, *args, **kwargs) -> None:
        """Legacy refresh flow is no longer exposed via the public API."""
        raise PluggedInError(
            "Document refresh is no longer available via the public API."
        )

    async def remove_document(self, *args, **kwargs) -> None:
        """Legacy remove flow is no longer exposed via the public API."""
        raise PluggedInError(
            "Document removal is no longer available via the public API."
        )

    def _parse_rag_response(self, response) -> Union[str, Dict]:
        """Best-effort parsing for RAG responses that may return text or JSON."""
        try:
            return response.json()
        except ValueError:
            return response.text

    def _transform_rag_response(self, data: Union[str, Dict]) -> RagResponse:
        """Transform API response to RagResponse type"""
        if isinstance(data, str):
            return RagResponse(
                success=True,
                answer=data,
                sources=[],
                document_ids=[],
                documents=[],
            )

        if not isinstance(data, dict):
            return RagResponse(
                success=False,
                error="Unexpected response format from RAG query endpoint",
            )

        answer = (
            data.get("answer")
            or data.get("response")
            or data.get("results")
            or data.get("message")
            or ""
        )

        sources = data.get("sources") or []
        document_ids = data.get("documentIds") or data.get("document_ids") or []

        documents = [
            RagSourceDocument(
                id=document_id,
                name=sources[index] if index < len(sources) else f"Document {index + 1}",
            )
            for index, document_id in enumerate(document_ids)
        ]

        return RagResponse(
            success=data.get("success", True),
            answer=answer,
            sources=sources,
            document_ids=document_ids,
            documents=documents,
            error=data.get("error"),
        )
