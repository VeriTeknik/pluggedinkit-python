"""Jungian Intelligence Layer service for Plugged.in SDK

Provides access to the Jungian-inspired intelligence layer including
archetype-aware pattern search, individuation scoring, synchronicity
detection, and dream-cycle consolidation history.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..exceptions import PluggedInError
from ..types import (
    ArchetypedPattern,
    ArchetypeSearchResponse,
    DreamConsolidation,
    IndividuationHistoryEntry,
    IndividuationResponse,
    SynchronicityPattern,
)

if TYPE_CHECKING:
    from ..client import AsyncPluggedInClient, PluggedInClient


# -----------------------------------------------------------------------------
# Shared Helper Functions
# -----------------------------------------------------------------------------


def _parse_archetype_search(data: Dict[str, Any]) -> ArchetypeSearchResponse:
    """Parse the archetype search response into typed model."""
    patterns_raw = data.get("patterns", [])
    patterns = [ArchetypedPattern(**p) for p in patterns_raw]
    return ArchetypeSearchResponse(patterns=patterns)


def _parse_individuation(data: Dict[str, Any]) -> IndividuationResponse:
    """Parse the individuation score response into typed model."""
    return IndividuationResponse(**data)


def _parse_individuation_history(data: Any) -> List[IndividuationHistoryEntry]:
    """Parse the individuation history response into typed list."""
    if isinstance(data, list):
        return [IndividuationHistoryEntry(**entry) for entry in data]
    # If wrapped in an object, try the 'history' key
    if isinstance(data, dict):
        entries = data.get("history", data.get("entries", []))
        return [IndividuationHistoryEntry(**entry) for entry in entries]
    return []


def _parse_synchronicity_patterns(data: Any) -> List[SynchronicityPattern]:
    """Parse synchronicity patterns response."""
    if isinstance(data, list):
        return [SynchronicityPattern(**p) for p in data]
    if isinstance(data, dict):
        patterns = data.get("patterns", [])
        return [SynchronicityPattern(**p) for p in patterns]
    return []


def _parse_dream_history(data: Any) -> List[DreamConsolidation]:
    """Parse dream consolidation history response."""
    if isinstance(data, list):
        return [DreamConsolidation(**d) for d in data]
    if isinstance(data, dict):
        entries = data.get("history", data.get("consolidations", []))
        return [DreamConsolidation(**d) for d in entries]
    return []


# -----------------------------------------------------------------------------
# Synchronous Jungian Service
# -----------------------------------------------------------------------------


class JungianService:
    """Synchronous Jungian Intelligence Layer service for Plugged.in.

    Provides archetype-aware pattern search, individuation scoring,
    synchronicity detection, and dream-cycle consolidation history.
    """

    def __init__(self, client: "PluggedInClient"):
        self.client = client

    def search_with_context(
        self,
        query: str,
        tool_name: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> ArchetypeSearchResponse:
        """Search patterns with archetype context injection.

        Sends a query to the archetype inject endpoint which returns
        patterns enriched with Jungian archetype classifications.

        Args:
            query: Natural language search query
            tool_name: Optional tool name for context
            outcome: Optional outcome description for context

        Returns:
            ArchetypeSearchResponse with classified patterns

        Raises:
            PluggedInError: If the API request fails
        """
        payload: Dict[str, Any] = {"query": query}
        if tool_name is not None:
            payload["tool_name"] = tool_name
        if outcome is not None:
            payload["outcome"] = outcome

        response = self.client.request(
            "POST", "/api/memory/archetype/inject", json=payload
        )
        return _parse_archetype_search(response.json())

    def get_individuation_score(self) -> IndividuationResponse:
        """Get the current individuation score.

        The individuation score measures the agent's psychological
        development across four components: memory depth, learning
        velocity, collective contribution, and self-awareness.

        Returns:
            IndividuationResponse with score, level, trend, and components

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request("GET", "/api/memory/individuation")
        return _parse_individuation(response.json())

    def get_individuation_history(
        self, days: int = 30
    ) -> List[IndividuationHistoryEntry]:
        """Get individuation score history over a time period.

        Args:
            days: Number of days of history to retrieve (default: 30)

        Returns:
            List of IndividuationHistoryEntry ordered by date

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request(
            "GET",
            "/api/memory/individuation",
            params={"history": "true", "days": str(days)},
        )
        return _parse_individuation_history(response.json())

    def get_synchronicity_patterns(self) -> List[SynchronicityPattern]:
        """Get detected synchronicity patterns.

        Synchronicity patterns are meaningful coincidences detected
        across multiple profiles in the collective unconscious layer.

        Returns:
            List of SynchronicityPattern instances

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request("GET", "/api/memory/sync/patterns")
        return _parse_synchronicity_patterns(response.json())

    def get_dream_history(self) -> List[DreamConsolidation]:
        """Get dream-cycle consolidation history.

        Dream consolidations represent periodic memory compression
        cycles that merge similar patterns and reduce token usage.

        Returns:
            List of DreamConsolidation records

        Raises:
            PluggedInError: If the API request fails
        """
        response = self.client.request("GET", "/api/memory/dream/history")
        return _parse_dream_history(response.json())


# -----------------------------------------------------------------------------
# Asynchronous Jungian Service
# -----------------------------------------------------------------------------


class AsyncJungianService:
    """Asynchronous Jungian Intelligence Layer service for Plugged.in.

    Provides archetype-aware pattern search, individuation scoring,
    synchronicity detection, and dream-cycle consolidation history.
    """

    def __init__(self, client: "AsyncPluggedInClient"):
        self.client = client

    async def search_with_context(
        self,
        query: str,
        tool_name: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> ArchetypeSearchResponse:
        """Search patterns with archetype context injection.

        Sends a query to the archetype inject endpoint which returns
        patterns enriched with Jungian archetype classifications.

        Args:
            query: Natural language search query
            tool_name: Optional tool name for context
            outcome: Optional outcome description for context

        Returns:
            ArchetypeSearchResponse with classified patterns

        Raises:
            PluggedInError: If the API request fails
        """
        payload: Dict[str, Any] = {"query": query}
        if tool_name is not None:
            payload["tool_name"] = tool_name
        if outcome is not None:
            payload["outcome"] = outcome

        response = await self.client.request(
            "POST", "/api/memory/archetype/inject", json=payload
        )
        return _parse_archetype_search(response.json())

    async def get_individuation_score(self) -> IndividuationResponse:
        """Get the current individuation score.

        The individuation score measures the agent's psychological
        development across four components: memory depth, learning
        velocity, collective contribution, and self-awareness.

        Returns:
            IndividuationResponse with score, level, trend, and components

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request("GET", "/api/memory/individuation")
        return _parse_individuation(response.json())

    async def get_individuation_history(
        self, days: int = 30
    ) -> List[IndividuationHistoryEntry]:
        """Get individuation score history over a time period.

        Args:
            days: Number of days of history to retrieve (default: 30)

        Returns:
            List of IndividuationHistoryEntry ordered by date

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request(
            "GET",
            "/api/memory/individuation",
            params={"history": "true", "days": str(days)},
        )
        return _parse_individuation_history(response.json())

    async def get_synchronicity_patterns(self) -> List[SynchronicityPattern]:
        """Get detected synchronicity patterns.

        Synchronicity patterns are meaningful coincidences detected
        across multiple profiles in the collective unconscious layer.

        Returns:
            List of SynchronicityPattern instances

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request("GET", "/api/memory/sync/patterns")
        return _parse_synchronicity_patterns(response.json())

    async def get_dream_history(self) -> List[DreamConsolidation]:
        """Get dream-cycle consolidation history.

        Dream consolidations represent periodic memory compression
        cycles that merge similar patterns and reduce token usage.

        Returns:
            List of DreamConsolidation records

        Raises:
            PluggedInError: If the API request fails
        """
        response = await self.client.request("GET", "/api/memory/dream/history")
        return _parse_dream_history(response.json())
