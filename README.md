# Plugged.in Python SDK

[![PyPI version](https://badge.fury.io/py/pluggedinkit.svg)](https://pypi.org/project/pluggedinkit/)
[![Python Support](https://img.shields.io/pypi/pyversions/pluggedinkit.svg)](https://pypi.org/project/pluggedinkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the Plugged.in Library API. Full support for both synchronous and asynchronous operations with comprehensive type hints.

**PyPI**: [https://pypi.org/project/pluggedinkit/](https://pypi.org/project/pluggedinkit/)

## Installation

```bash
pip install pluggedinkit
```

## Quick Start

### Synchronous Client

```python
from pluggedinkit import PluggedInClient

# Initialize the client
client = PluggedInClient(
    api_key="your-api-key",
    # base_url defaults to https://plugged.in
)

# List documents
documents = client.documents.list()
print(f"Found {documents.total} documents")

# Search documents
results = client.documents.search("machine learning")
for result in results.results:
    print(f"{result.title} - Relevance: {result.relevance_score}")

# Query knowledge base
answer = client.rag.ask_question("What are the main features?")
print(answer)
```

### Asynchronous Client

```python
import asyncio
from pluggedinkit import AsyncPluggedInClient

async def main():
    # Initialize async client
    async with AsyncPluggedInClient(api_key="your-api-key") as client:
        # List documents
        documents = await client.documents.list()
        print(f"Found {documents.total} documents")

        # Query RAG
        answer = await client.rag.ask_question("What's new in the project?")
        print(answer)

asyncio.run(main())
```

## Features

- 📄 **Document Management** - Full CRUD operations with type safety
- 🔍 **Semantic Search** - AI-powered document search
- 🤖 **RAG Integration** - Natural language queries to your knowledge base
- 📋 **Clipboard/Memory** - Persistent key-value storage for MCP tools and AI agents
- 📤 **File Uploads** - Support for various file formats
- 🔄 **Version Control** - Document versioning and history
- ⚡ **Async Support** - Both sync and async clients
- 🐍 **Type Hints** - Full typing support with Pydantic models
- 🔁 **Retry Logic** - Automatic retries with exponential backoff
- 📊 **Rate Limiting** - Built-in rate limit handling

## Authentication

Get your API key from your Plugged.in profile settings:

```python
import os
from pluggedinkit import PluggedInClient

client = PluggedInClient(
    api_key=os.environ["PLUGGEDIN_API_KEY"],
    # For local development:
    # base_url="http://localhost:12005"
)
```

## Documentation

### Document Operations

#### List Documents

```python
from pluggedin.types import DocumentFilters, DocumentSource

filters = DocumentFilters(
    source=DocumentSource.AI_GENERATED,
    tags=["report", "analysis"],
    sort="date_desc",
    limit=20,
    offset=0
)

response = client.documents.list(filters)
for doc in response.documents:
    print(f"{doc.title} ({doc.file_size} bytes)")
```

#### Get Document

```python
# Get document metadata
doc = client.documents.get("document-id")

# Get document with content
doc_with_content = client.documents.get(
    "document-id",
    include_content=True,
    include_versions=True
)

print(doc_with_content.content)
```

#### Search Documents

```python
from pluggedin.types import SearchFilters

filters = SearchFilters(
    model_provider="anthropic",
    date_from="2024-01-01T00:00:00Z",
    tags=["finance", "q4"]
)

results = client.documents.search(
    "quarterly report",
    filters=filters,
    limit=10,
    offset=0
)

for result in results.results:
    print(f"{result.title}")
    print(f"  Relevance: {result.relevance_score}")
    print(f"  Snippet: {result.snippet}")
```

#### Update Document

```python
from pluggedin.types import UpdateDocumentRequest, UpdateOperation

request = UpdateDocumentRequest(
    operation=UpdateOperation.APPEND,
    content="\n\n## New Section\n\nAdditional content here.",
    metadata={
        "changeSummary": "Added implementation details",
        "model": {
            "name": "claude-3-opus",
            "provider": "anthropic",
            "version": "20240229"
        }
    }
)

response = client.documents.update("document-id", request)
print(f"Updated to version {response.version}")
```

#### Create AI Document

```python
metadata = {
    "format": "md",
    "category": "documentation",
    "tags": ["api", "guide"],
    "model": {
        "name": "gpt-4",
        "provider": "openai",
        "version": "0613"
    },
    "prompt": "Create an API integration guide",
    "visibility": "workspace"
}

doc = client.documents.create(
    title="API Integration Guide",
    content="# API Integration Guide\n\n## Introduction\n\n...",
    metadata=metadata
)

print(f"Created document: {doc.id}")
```

### RAG Operations

#### Query Knowledge Base

```python
# Simple query
answer = client.rag.ask_question("What are the deployment procedures?")
print(answer)

# Query with sources
result = client.rag.query_with_sources(
    "Explain the authentication flow",
    project_uuid="project-uuid"  # Optional
)

print(f"Answer: {result['answer']}")
print("Sources:")
for source in result["sources"]:
    print(f"- {source.name} (relevance: {source.relevance}%)")
```

#### Find Relevant Documents

```python
documents = client.rag.find_relevant_documents(
    "user authentication",
    project_uuid="project-uuid",
    limit=5
)

for doc in documents:
    print(f"- {doc.name}")
    if doc.model:
        print(f"  By: {doc.model.provider}/{doc.model.name}")
```

#### Check RAG Status

```python
# Check availability
status = client.rag.check_availability()
print(f"RAG Available: {status['available']}")

# Get storage stats
stats = client.rag.get_storage_stats()
print(f"Documents: {stats['document_count']}")
print(f"Total size: {stats['total_size']} bytes")
```

### File Upload Operations

#### Upload Single File

```python
from pathlib import Path

# Upload from file path
file_path = Path("./report.pdf")
metadata = {
    "name": "Q4 Report.pdf",
    "description": "Quarterly financial report",
    "tags": ["finance", "q4", "2024"],
    "purpose": "Financial documentation",
    "relatedTo": "PROJECT-123"
}

def on_progress(percent):
    print(f"Upload progress: {percent}%")

response = client.uploads.upload_file(
    file_path,
    metadata,
    on_progress=on_progress
)

if response.success:
    print(f"Uploaded: {response.document_id}")

    # Track processing
    if response.upload_id:
        def on_update(status):
            print(f"Status: {status.status} - {status.message}")

        client.uploads.track_upload(
            response.upload_id,
            on_update
        )
```

#### Upload from Memory

```python
# Upload bytes directly
content = b"File content here..."
metadata = {
    "name": "data.txt",
    "description": "Data file",
    "tags": ["data"]
}

response = client.uploads.upload_file(content, metadata)
```

#### Batch Upload

```python
files = [
    {
        "file": Path("doc1.pdf"),
        "metadata": {"name": "doc1.pdf", "tags": ["batch"]}
    },
    {
        "file": Path("doc2.txt"),
        "metadata": {"name": "doc2.txt", "tags": ["batch"]}
    }
]

def on_batch_progress(current, total):
    print(f"Uploaded {current}/{total} files")

results = client.uploads.upload_batch(
    files,
    on_progress=on_batch_progress
)

for i, result in enumerate(results):
    if result.success:
        print(f"✓ {files[i]['metadata']['name']}")
    else:
        print(f"✗ {files[i]['metadata']['name']}: {result.error}")
```

### Async Examples

#### Async Document Operations

```python
import asyncio

async def document_operations():
    async with AsyncPluggedInClient(api_key="your-key") as client:
        # List documents
        docs = await client.documents.list()

        # Search concurrently
        search_tasks = [
            client.documents.search("api"),
            client.documents.search("guide"),
            client.documents.search("tutorial")
        ]
        results = await asyncio.gather(*search_tasks)

        for result in results:
            print(f"Found {result.total} matches")

asyncio.run(document_operations())
```

#### Async RAG Queries

```python
async def rag_operations():
    async with AsyncPluggedInClient(api_key="your-key") as client:
        # Multiple queries concurrently
        questions = [
            "What is the authentication process?",
            "How do I deploy the application?",
            "What are the API rate limits?"
        ]

        tasks = [client.rag.ask_question(q) for q in questions]
        answers = await asyncio.gather(*tasks)

        for q, a in zip(questions, answers):
            print(f"Q: {q}")
            print(f"A: {a}\n")

asyncio.run(rag_operations())
```

### Clipboard Operations

The clipboard provides persistent key-value storage for MCP tools and AI agents.

#### Set Named Entry

```python
entry = client.clipboard.set(
    name="user_preferences",
    value='{"theme": "dark", "lang": "en"}',
    content_type="application/json",
    encoding="utf-8",
    visibility="private",
    ttl_seconds=86400  # 24 hours
)

print(f"Created entry: {entry.uuid}")
print(f"Source: {entry.source}")  # 'sdk' - automatically set
```

#### Get Entry

```python
# By name
entry = client.clipboard.get(name="user_preferences")
print(entry.value)

# By index (stack access)
latest = client.clipboard.get(idx=0)
```

#### Push to Stack

```python
entry = client.clipboard.push(
    value="Processing step 1 result",
    content_type="text/plain"
)

print(f"Pushed to index: {entry.idx}")
```

#### Pop from Stack

```python
entry = client.clipboard.pop()
if entry:
    print(f"Popped value: {entry.value}")
```

#### List and Delete

```python
# List all entries
response = client.clipboard.list()
for entry in response.entries:
    label = entry.name or f"idx:{entry.idx}"
    print(f"{label} - source: {entry.source}")

# Delete by name
client.clipboard.delete(name="old_entry")

# Clear all
client.clipboard.clear_all()
```

#### Clipboard Entry Structure

```python
from pluggedinkit import ClipboardEntry, ClipboardSource

# ClipboardEntry fields:
# - uuid: str
# - name: Optional[str]           # Semantic key
# - idx: Optional[int]            # Stack index
# - value: str
# - content_type: str
# - encoding: "utf-8" | "base64" | "hex"
# - size_bytes: int
# - visibility: "private" | "workspace" | "public"
# - created_by_tool: Optional[str]
# - created_by_model: Optional[str]
# - source: Optional[ClipboardSource]  # Auto-set: ui, sdk, or mcp
# - created_at: datetime
# - updated_at: datetime
# - expires_at: Optional[datetime]
```

> **Note**: The `source` field is automatically set to `ClipboardSource.SDK` when using this SDK. It indicates how the entry was created (UI, SDK, or MCP proxy).

### Error Handling

```python
from pluggedinkit import (
    PluggedInError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError
)

try:
    doc = client.documents.get("invalid-id")
except AuthenticationError as e:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NotFoundError as e:
    print("Document not found")
except ValidationError as e:
    print(f"Validation error: {e.details}")
except PluggedInError as e:
    print(f"API error: {e}")
```

### Advanced Configuration

```python
client = PluggedInClient(
    api_key="your-api-key",
    base_url="https://plugged.in",
    timeout=60.0,  # 60 seconds
    max_retries=5,
    debug=True  # Enable debug logging
)

# Update API key at runtime
client.set_api_key("new-api-key")
```

## Type Safety

The SDK uses Pydantic for comprehensive type safety:

```python
from pluggedin.types import (
    Document,
    DocumentFilters,
    DocumentSource,
    DocumentVisibility,
    UpdateOperation,
    ModelInfo
)

# All types are validated
filters = DocumentFilters(
    source=DocumentSource.AI_GENERATED,
    limit=10  # Validated: must be > 0 and <= 100
)

# IDE autocomplete and type checking
doc: Document = client.documents.get("id")
print(doc.title)  # Type-safe attribute access
```

## Environment Variables

Store your API key securely:

```bash
# .env
PLUGGEDIN_API_KEY=your-api-key
PLUGGEDIN_BASE_URL=https://plugged.in
```

```python
import os
from dotenv import load_dotenv
from pluggedin import PluggedInClient

load_dotenv()

client = PluggedInClient(
    api_key=os.environ["PLUGGEDIN_API_KEY"],
    base_url=os.environ.get("PLUGGEDIN_BASE_URL")
)
```

## Rate Limiting

The SDK automatically handles rate limiting:

- **API Endpoints**: 60 requests per minute
- **Document Search**: 10 requests per hour for AI documents
- **RAG Queries**: Subject to plan limits

## Examples

See the [examples](./examples) directory for complete working examples:

- [Basic Usage](./examples/basic.py)
- [Document Management](./examples/documents.py)
- [RAG Queries](./examples/rag.py)
- [File Upload](./examples/upload.py)
- [Async Operations](./examples/async_example.py)
- [Error Handling](./examples/errors.py)

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT - see [LICENSE](LICENSE) for details.

## Support

- **PyPI Package**: [https://pypi.org/project/pluggedinkit/](https://pypi.org/project/pluggedinkit/)
- **GitHub Repository**: [https://github.com/VeriTeknik/pluggedinkit-python](https://github.com/VeriTeknik/pluggedinkit-python)
- **Documentation**: [https://docs.plugged.in](https://docs.plugged.in)
- **Issues**: [GitHub Issues](https://github.com/VeriTeknik/pluggedinkit-python/issues)
- **Discord**: [Join our community](https://discord.gg/pluggedin)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.