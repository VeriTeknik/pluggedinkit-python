"""Type definitions for Plugged.in SDK"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class DocumentSource(str, Enum):
    """Document source types"""
    ALL = "all"
    UPLOAD = "upload"
    AI_GENERATED = "ai_generated"
    API = "api"


class DocumentVisibility(str, Enum):
    """Document visibility levels"""
    PRIVATE = "private"
    WORKSPACE = "workspace"
    PUBLIC = "public"


class DocumentCategory(str, Enum):
    """Document categories"""
    REPORT = "report"
    ANALYSIS = "analysis"
    DOCUMENTATION = "documentation"
    GUIDE = "guide"
    RESEARCH = "research"
    CODE = "code"
    OTHER = "other"


class DocumentFormat(str, Enum):
    """Document formats"""
    MARKDOWN = "md"
    TEXT = "txt"
    JSON = "json"
    HTML = "html"


class SortOrder(str, Enum):
    """Sort order options"""
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    TITLE = "title"
    SIZE = "size"


class UpdateOperation(str, Enum):
    """Document update operations"""
    REPLACE = "replace"
    APPEND = "append"
    PREPEND = "prepend"


class ModelInfo(BaseModel):
    """AI model information"""
    name: str
    provider: str
    version: Optional[str] = None


class GenerationParams(BaseModel):
    """AI generation parameters"""
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, gt=0)
    top_p: Optional[float] = Field(None, ge=0, le=1)


class AIMetadata(BaseModel):
    """AI-related metadata for documents"""
    model: Optional[ModelInfo] = None
    timestamp: Optional[str] = None
    context: Optional[str] = None
    generation_params: Optional[GenerationParams] = None
    prompt: Optional[str] = None
    conversation_context: Optional[Union[List[str], List[Dict[str, str]]]] = None
    update_reason: Optional[str] = None
    changes_from_prompt: Optional[str] = None
    change_summary: Optional[str] = None
    source_documents: Optional[List[str]] = None
    visibility: Optional[str] = None
    session_id: Optional[str] = None
    last_updated_by: Optional[ModelInfo] = None
    last_update_timestamp: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields


class ModelAttribution(BaseModel):
    """Model attribution information"""
    model_name: str
    model_provider: str
    contribution_type: Literal["created", "updated", "reviewed"]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class DocumentFilters(BaseModel):
    """Filters for document listing"""
    source: Optional[DocumentSource] = None
    model_name: Optional[str] = None
    model_provider: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    visibility: Optional[Union[DocumentVisibility, Literal["all"]]] = None
    search_query: Optional[str] = None
    sort: Optional[SortOrder] = None
    limit: Optional[int] = Field(None, gt=0, le=100)
    offset: Optional[int] = Field(None, ge=0)


class Document(BaseModel):
    """Document model"""
    id: str
    title: str
    description: Optional[str] = None
    file_name: str
    file_size: int
    mime_type: str
    tags: List[str] = []
    source: str
    visibility: str
    version: int
    created_at: datetime
    updated_at: datetime
    ai_metadata: Optional[AIMetadata] = None
    model_attributions: Optional[List[ModelAttribution]] = None
    content_hash: Optional[str] = None
    parent_document_id: Optional[str] = None


class DocumentWithContent(Document):
    """Document with content included"""
    content: str
    content_encoding: Literal["utf-8", "base64"]


class DocumentVersion(BaseModel):
    """Document version information"""
    version_number: int
    created_at: datetime
    created_by_model: Optional[ModelInfo] = None
    change_summary: Optional[str] = None
    content_diff: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response for document listing"""
    documents: List[Document]
    total: int
    limit: int
    offset: int


class SearchFilters(BaseModel):
    """Filters for document search"""
    model_name: Optional[str] = None
    model_provider: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[DocumentSource] = None


class SearchResult(BaseModel):
    """Search result item"""
    id: str
    title: str
    description: Optional[str] = None
    snippet: str
    relevance_score: float
    source: str
    ai_metadata: Optional[AIMetadata] = None
    tags: List[str] = []
    visibility: str
    created_at: datetime
    model_attributions: Optional[List[ModelAttribution]] = None


class SearchResponse(BaseModel):
    """Response for document search"""
    results: List[SearchResult]
    total: int
    limit: int
    offset: int
    has_more: bool


class UpdateDocumentRequest(BaseModel):
    """Request for updating a document"""
    operation: UpdateOperation
    content: str = Field(..., min_length=1, max_length=10000000)
    metadata: Optional[Dict[str, Any]] = None


class UpdateDocumentResponse(BaseModel):
    """Response for document update"""
    success: bool
    document_id: str
    version: int
    file_written: bool
    message: Optional[str] = None


class UploadMetadata(BaseModel):
    """Metadata for document upload"""
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[DocumentCategory] = None
    format: Optional[DocumentFormat] = None
    metadata: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    document_id: Optional[str] = None
    upload_id: Optional[str] = None
    rag_processed: Optional[bool] = None
    rag_error: Optional[str] = None
    error: Optional[str] = None


class UploadProgress(BaseModel):
    """Upload progress information"""
    upload_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None


class RagSourceDocument(BaseModel):
    """RAG source document"""
    id: str
    name: str
    relevance: Optional[float] = None
    model: Optional[ModelInfo] = None
    source: Optional[str] = None
    is_unresolved: Optional[bool] = None


class RagResponse(BaseModel):
    """Response for RAG queries"""
    success: bool
    answer: Optional[str] = None
    sources: Optional[List[str]] = None
    document_ids: Optional[List[str]] = None
    documents: Optional[List[RagSourceDocument]] = None
    error: Optional[str] = None