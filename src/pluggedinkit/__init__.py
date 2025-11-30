"""
Plugged.in Library SDK for Python

Official SDK for interacting with Plugged.in's document library and RAG capabilities.
"""

__version__ = "1.0.0"

from .client import PluggedInClient, AsyncPluggedInClient
from .exceptions import (
    PluggedInError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)
from .services.clipboard import ClearAllResult
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
    ClipboardSource,
    DEFAULT_CLIPBOARD_SOURCE,
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
from .services.agents import (
    Agent,
    CreateAgentRequest,
    ResourceRequirements,
    Heartbeat,
    Metrics,
    LifecycleEvent,
    AgentDetails,
    AgentService,
    AsyncAgentService,
)

__all__ = [
    "PluggedInClient",
    "AsyncPluggedInClient",
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
    "ClipboardSource",
    "ClearAllResult",
    "DEFAULT_CLIPBOARD_SOURCE",
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
    "Agent",
    "CreateAgentRequest",
    "ResourceRequirements",
    "Heartbeat",
    "Metrics",
    "LifecycleEvent",
    "AgentDetails",
    "AgentService",
    "AsyncAgentService",
]
