from src.mcp.types.json_rpc import JSONRPCRequest, JSONRPCError, Error, JSONRPCResponse, JSONRPCNotification, JSONRPCMessage, JSONRPCResultResponse, JSONRPCErrorResponse
from src.mcp.transport.base import BaseTransport
from src.mcp.logger import get_logger
from httpx import AsyncClient, Limits
from httpx_sse import aconnect_sse
from src.mcp.exception import MCPError
from urllib.parse import urljoin
from typing import Optional
import asyncio
import json

logger = get_logger(__name__)


class SSETransport(BaseTransport):
    """
    SSE Transport for MCP
    """

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None):
        self.url = url
        self.session_url = None
        self.headers = headers or {}
        self.client: AsyncClient | None = None
        self.listen_task: asyncio.Task | None = None
        self.ready_event = asyncio.Event()
        self.pending: dict[str, asyncio.Future] = {}  # Maps request id -> Future

    async def connect(self):
        """Create SSE Client and wait until endpoint is ready."""
        self.client = AsyncClient(timeout=30, headers=self.headers, limits=Limits(max_connections=10))
        self.listen_task = asyncio.create_task(self.listen())
        await self.ready_event.wait()

    async def send_request(self, request: JSONRPCMessage) -> JSONRPCResponse:
        """
        Send JSON-RPC request and wait for its response.
        """
        if not self.session_url:
            raise MCPError(code=-1, message="Session not initialized.")

        future = asyncio.get_event_loop().create_future()
        self.pending[str(request.id)] = future

        headers = {
            **self.headers,
            "Content-Type": "application/json",
        }

        await self.client.post(self.session_url, headers=headers, json=request.model_dump(by_alias=True))

        try:
            response = await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            self.pending.pop(str(request.id), None)
            raise MCPError(code=-1, message="Request timed out.")

        if isinstance(response, JSONRPCErrorResponse):
            raise MCPError(code=response.error.code, message=response.error.message)

        return response

    async def send_notification(self, notification: JSONRPCMessage):
        """Send a notification without expecting a response."""
        if not self.session_url:
            raise MCPError(code=-1, message="Session not initialized.")
        headers = {
            **self.headers,
            "Content-Type": "application/json",
        }
        await self.client.post(self.session_url, headers=headers, json=notification.model_dump(by_alias=True))

    async def send_response(self, response: JSONRPCResponse):
        """Send a JSON-RPC response."""
        if not self.session_url:
             raise MCPError(code=-1, message="Session not initialized.")
        headers = {
            **self.headers,
            "Content-Type": "application/json",
        }
        await self.client.post(self.session_url, headers=headers, json=response.model_dump(by_alias=True))

    async def listen(self):
        """Listen for messages from the MCP server."""
        async with aconnect_sse(self.client, "GET", self.url) as iter:
            async for obj in iter.aiter_sse():
                try:
                    if obj.event == "endpoint":
                        self.session_url = urljoin(self.url, obj.data)
                        self.ready_event.set()

                    elif obj.event == "message":
                        content = json.loads(obj.data)
                        
                        if "result" in content: # Response
                             message_id = str(content.get("id"))
                             message = JSONRPCResultResponse.model_validate(content)
                             future = self.pending.pop(message_id, None)
                             if future and not future.done():
                                 future.set_result(message)
                        
                        elif "method" in content: # Request
                            message = JSONRPCRequest.model_validate(content)
                            response = await self.handle_request(message)
                            await self.send_response(response)

                        elif "error" in content: # Error
                            message_id = str(content.get("id"))
                            error = Error.model_validate(content["error"])
                            message = JSONRPCErrorResponse(id=message_id, error=error)
                            future = self.pending.pop(message_id, None)
                            if future and not future.done():
                                future.set_result(message)
                        else:
                            continue

                except Exception as e:
                    logger.error(f"Error processing SSE message: {e}", exc_info=True)

    async def disconnect(self):
        """Gracefully close connection."""
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
            finally:
                self.listen_task = None

        if self.client:
            await self.client.aclose()
            self.client = None

        # Cancel all pending futures
        for fut in self.pending.values():
            if not fut.done():
                fut.cancel()
        self.pending.clear()
