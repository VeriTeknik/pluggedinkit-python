"""Agent management service for PAP (Plugged.in Agent Protocol)"""

from typing import Any, Dict, List, Literal, Optional, TypedDict


class Agent(TypedDict, total=False):
    """PAP Agent"""
    uuid: str
    name: str
    dns_name: str
    state: Literal['NEW', 'PROVISIONED', 'ACTIVE', 'DRAINING', 'TERMINATED', 'KILLED']
    kubernetes_namespace: Optional[str]
    kubernetes_deployment: Optional[str]
    created_at: str
    provisioned_at: Optional[str]
    activated_at: Optional[str]
    terminated_at: Optional[str]
    last_heartbeat_at: Optional[str]
    metadata: Optional[Dict[str, Any]]


class ResourceRequirements(TypedDict, total=False):
    """Kubernetes resource requirements"""
    cpu_request: Optional[str]
    memory_request: Optional[str]
    cpu_limit: Optional[str]
    memory_limit: Optional[str]


class CreateAgentRequest(TypedDict, total=False):
    """Request to create a new agent"""
    name: str
    description: Optional[str]
    image: Optional[str]
    resources: Optional[ResourceRequirements]


class Heartbeat(TypedDict):
    """Agent heartbeat (liveness only - zombie prevention)"""
    mode: Literal['EMERGENCY', 'IDLE', 'SLEEP']
    uptime_seconds: float
    timestamp: str


class Metrics(TypedDict, total=False):
    """Agent metrics (resource telemetry - separate from heartbeat)"""
    cpu_percent: float
    memory_mb: float
    requests_handled: int
    timestamp: str
    custom_metrics: Optional[Dict[str, Any]]


class LifecycleEvent(TypedDict):
    """Agent lifecycle event"""
    event_type: str
    from_state: Optional[str]
    to_state: str
    timestamp: str
    metadata: Optional[Dict[str, Any]]


class AgentDetails(TypedDict):
    """Detailed agent information"""
    agent: Agent
    recentHeartbeats: List[Heartbeat]
    recentMetrics: List[Metrics]
    lifecycleEvents: List[LifecycleEvent]
    kubernetesStatus: Optional[Dict[str, Any]]


class AgentService:
    """Synchronous agent service"""

    def __init__(self, client: 'PluggedInClient'):
        self.client = client

    def list(self) -> List[Agent]:
        """List all PAP agents"""
        response = self.client.request('GET', '/api/agents')
        return response.json()

    def create(self, request: CreateAgentRequest) -> Dict[str, Any]:
        """Create a new PAP agent"""
        response = self.client.request('POST', '/api/agents', json=request)
        return response.json()

    def get(self, agent_id: str) -> AgentDetails:
        """Get details for a specific agent"""
        response = self.client.request('GET', f'/api/agents/{agent_id}')
        return response.json()

    def delete(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent (terminates deployment)"""
        response = self.client.request('DELETE', f'/api/agents/{agent_id}')
        return response.json()

    def export(
        self,
        agent_id: str,
        include_telemetry: bool = True,
        telemetry_limit: int = 100
    ) -> Dict[str, Any]:
        """Export agent data including telemetry"""
        response = self.client.request(
            'POST',
            f'/api/agents/{agent_id}/export',
            json={
                'include_telemetry': include_telemetry,
                'telemetry_limit': telemetry_limit,
            }
        )
        return response.json()

    def heartbeat(
        self,
        agent_id: str,
        mode: Literal['EMERGENCY', 'IDLE', 'SLEEP'],
        uptime_seconds: float
    ) -> Dict[str, str]:
        """
        Submit a heartbeat for an agent.

        CRITICAL: Heartbeats are liveness-only (PAP zombie prevention).
        Never include resource data (CPU, memory) in heartbeats - use metrics() instead.
        """
        response = self.client.request(
            'POST',
            f'/api/agents/{agent_id}/heartbeat',
            json={
                'mode': mode,
                'uptime_seconds': uptime_seconds,
            }
        )
        return response.json()

    def metrics(
        self,
        agent_id: str,
        cpu_percent: float,
        memory_mb: float,
        requests_handled: int,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Submit metrics for an agent.

        CRITICAL: Metrics are separate from heartbeats (PAP zombie prevention).
        Heartbeats are liveness-only, metrics are resource telemetry.
        """
        response = self.client.request(
            'POST',
            f'/api/agents/{agent_id}/metrics',
            json={
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'requests_handled': requests_handled,
                'custom_metrics': custom_metrics,
            }
        )
        return response.json()


class AsyncAgentService:
    """Asynchronous agent service"""

    def __init__(self, client: 'AsyncPluggedInClient'):
        self.client = client

    async def list(self) -> List[Agent]:
        """List all PAP agents"""
        response = await self.client.request('GET', '/api/agents')
        return response.json()

    async def create(self, request: CreateAgentRequest) -> Dict[str, Any]:
        """Create a new PAP agent"""
        response = await self.client.request('POST', '/api/agents', json=request)
        return response.json()

    async def get(self, agent_id: str) -> AgentDetails:
        """Get details for a specific agent"""
        response = await self.client.request('GET', f'/api/agents/{agent_id}')
        return response.json()

    async def delete(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent (terminates deployment)"""
        response = await self.client.request('DELETE', f'/api/agents/{agent_id}')
        return response.json()

    async def export(
        self,
        agent_id: str,
        include_telemetry: bool = True,
        telemetry_limit: int = 100
    ) -> Dict[str, Any]:
        """Export agent data including telemetry"""
        response = await self.client.request(
            'POST',
            f'/api/agents/{agent_id}/export',
            json={
                'include_telemetry': include_telemetry,
                'telemetry_limit': telemetry_limit,
            }
        )
        return response.json()

    async def heartbeat(
        self,
        agent_id: str,
        mode: Literal['EMERGENCY', 'IDLE', 'SLEEP'],
        uptime_seconds: float
    ) -> Dict[str, str]:
        """
        Submit a heartbeat for an agent.

        CRITICAL: Heartbeats are liveness-only (PAP zombie prevention).
        Never include resource data (CPU, memory) in heartbeats - use metrics() instead.
        """
        response = await self.client.request(
            'POST',
            f'/api/agents/{agent_id}/heartbeat',
            json={
                'mode': mode,
                'uptime_seconds': uptime_seconds,
            }
        )
        return response.json()

    async def metrics(
        self,
        agent_id: str,
        cpu_percent: float,
        memory_mb: float,
        requests_handled: int,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Submit metrics for an agent.

        CRITICAL: Metrics are separate from heartbeats (PAP zombie prevention).
        Heartbeats are liveness-only, metrics are resource telemetry.
        """
        response = await self.client.request(
            'POST',
            f'/api/agents/{agent_id}/metrics',
            json={
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'requests_handled': requests_handled,
                'custom_metrics': custom_metrics,
            }
        )
        return response.json()
