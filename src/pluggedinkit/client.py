"""Main client for Plugged.in SDK"""

import asyncio
from typing import Optional, Union
from urllib.parse import urljoin

import httpx

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    PluggedInError,
    RateLimitError,
)
from .services.documents import DocumentService, AsyncDocumentService
from .services.rag import RagService, AsyncRagService
from .services.uploads import UploadService, AsyncUploadService

DEFAULT_BASE_URL = "https://plugged.in"
DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 3


class BaseClient:
    """Base client with common functionality"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        debug: bool = False,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

    def _build_url(self, path: str) -> str:
        """Build full URL from path"""
        return urljoin(self.base_url, path)

    def _get_headers(self) -> dict:
        """Get default headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses"""
        if response.status_code == 401:
            raise AuthenticationError(
                response.json().get("error", "Invalid API key")
            )
        elif response.status_code == 404:
            raise NotFoundError(
                response.json().get("error", "Resource not found")
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(
                response.json().get("error", "Rate limit exceeded"),
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise PluggedInError(
                error_data.get("error", f"Request failed with status {response.status_code}"),
                status_code=response.status_code,
                details=error_data.get("details"),
            )


class PluggedInClient(BaseClient):
    """Synchronous client for Plugged.in API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        debug: bool = False,
    ):
        super().__init__(api_key, base_url, timeout, max_retries, debug)

        # Create HTTP client
        self.http = httpx.Client(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=timeout,
            follow_redirects=True,
        )

        # Initialize services
        self.documents = DocumentService(self)
        self.rag = RagService(self)
        self.uploads = UploadService(self)

    def request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None,
        stream: bool = False,
    ) -> httpx.Response:
        """Make a synchronous HTTP request"""
        url = self._build_url(path)

        if self.debug:
            print(f"[PluggedIn SDK] {method} {url}")
            if json:
                print(f"[PluggedIn SDK] Request body: {json}")

        # Prepare request kwargs
        kwargs = {
            "params": params,
        }

        if files:
            kwargs["files"] = files
        elif json is not None:
            kwargs["json"] = json

        # Make request with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self.http.request(method, url, **kwargs)

                if self.debug:
                    print(f"[PluggedIn SDK] Response: {response.status_code}")

                # Handle errors
                if response.status_code >= 400:
                    self._handle_response_error(response)

                return response

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    if self.debug:
                        print(f"[PluggedIn SDK] Retrying after {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    import time
                    time.sleep(wait_time)
                    continue
                break

        # If we got here, all retries failed
        raise PluggedInError(f"Request failed after {self.max_retries} attempts: {last_exception}")

    def set_api_key(self, api_key: str) -> None:
        """Update the API key"""
        self.api_key = api_key
        self.http.headers["Authorization"] = f"Bearer {api_key}"

    def close(self) -> None:
        """Close the HTTP client"""
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncPluggedInClient(BaseClient):
    """Asynchronous client for Plugged.in API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        debug: bool = False,
    ):
        super().__init__(api_key, base_url, timeout, max_retries, debug)

        # Create async HTTP client
        self.http = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=timeout,
            follow_redirects=True,
        )

        # Initialize async services
        self.documents = AsyncDocumentService(self)
        self.rag = AsyncRagService(self)
        self.uploads = AsyncUploadService(self)

    async def request(
        self,
        method: str,
        path: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None,
        stream: bool = False,
    ) -> httpx.Response:
        """Make an asynchronous HTTP request"""
        url = self._build_url(path)

        if self.debug:
            print(f"[PluggedIn SDK] {method} {url}")
            if json:
                print(f"[PluggedIn SDK] Request body: {json}")

        # Prepare request kwargs
        kwargs = {
            "params": params,
        }

        if files:
            kwargs["files"] = files
        elif json is not None:
            kwargs["json"] = json

        # Make request with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await self.http.request(method, url, **kwargs)

                if self.debug:
                    print(f"[PluggedIn SDK] Response: {response.status_code}")

                # Handle errors
                if response.status_code >= 400:
                    self._handle_response_error(response)

                return response

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    if self.debug:
                        print(f"[PluggedIn SDK] Retrying after {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                break

        # If we got here, all retries failed
        raise PluggedInError(f"Request failed after {self.max_retries} attempts: {last_exception}")

    def set_api_key(self, api_key: str) -> None:
        """Update the API key"""
        self.api_key = api_key
        self.http.headers["Authorization"] = f"Bearer {api_key}"

    async def close(self) -> None:
        """Close the async HTTP client"""
        await self.http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()