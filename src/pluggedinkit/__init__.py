"""
Plugged.in Library SDK for Python

Official SDK for interacting with Plugged.in's document library and RAG capabilities.
"""

__version__ = "1.0.0"

from .client import PluggedInClient
from .exceptions import (
    PluggedInError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)
from .types import (
    # Clipboard types
    ClipboardEntry,
    ClipboardListResponse,
    ClipboardSetRequest,
    ClipboardPushRequest,
    ClipboardGetFilters,
    ClipboardDeleteRequest,
    ClipboardResponse,
    ClipboardDeleteResponse,
    ClipboardEncoding,
    ClipboardVisibility,
    # Document types
    Document,
    DocumentWithContent,
    DocumentListResponse,
    DocumentFilters,
    SearchResponse,
    SearchResult,
    UpdateDocumentRequest,
    UploadMetadata,
    UploadResponse,
    RagResponse,
    RagSourceDocument,
    RagStorageStats,
    ModelInfo,
    AIMetadata,
)

__all__ = [
    "PluggedInClient",
    "PluggedInError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    # Clipboard types
    "ClipboardEntry",
    "ClipboardListResponse",
    "ClipboardSetRequest",
    "ClipboardPushRequest",
    "ClipboardGetFilters",
    "ClipboardDeleteRequest",
    "ClipboardResponse",
    "ClipboardDeleteResponse",
    "ClipboardEncoding",
    "ClipboardVisibility",
    # Document types
    "Document",
    "DocumentWithContent",
    "DocumentListResponse",
    "DocumentFilters",
    "SearchResponse",
    "SearchResult",
    "UpdateDocumentRequest",
    "UploadMetadata",
    "UploadResponse",
    "RagResponse",
    "RagSourceDocument",
    "RagStorageStats",
    "ModelInfo",
    "AIMetadata",
]
