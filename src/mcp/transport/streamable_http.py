from src.mcp.types.json_rpc import (
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCError,
    Error,
    Method,
)
from src.mcp.transport.base import BaseTransport
from src.mcp.exception import MCPError
from httpx import AsyncClient, Limits
from typing import Optional, Dict
import asyncio
import json


class StreamableHTTPTransport(BaseTransport):
    """
    HTTP transport supporting streaming JSON-RPC responses
    using asyncio.Future for one-shot request/response handling.
    """

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}
        self.mcp_session_id = None
        self.protocol_version = None
        self.client: Optional[AsyncClient] = None
        self.listen_task: Optional[asyncio.Task] = None
        self.pending: Dict[str, asyncio.Future] = {}

    async def connect(self):
        """Create an HTTP client and start the listener."""
        self.client = AsyncClient(
            timeout=10,
            headers=self.headers,
            limits=Limits(max_connections=10),
        )
        self.listen_task = asyncio.create_task(self.listen())

    async def listen(self):
        """
        Persistent stream listener for JSON-RPC responses.
        Keeps connection open and dispatches responses to pending Futures.
        """
        try:
            async with self.client.stream("GET", self.url, headers=self.headers) as response:
                if self.mcp_session_id is None:
                    self.mcp_session_id = response.headers.get("mcp-session-id")

                buffer = bytearray()

                async for chunk in response.aiter_bytes():
                    buffer.extend(chunk)
                    try:
                        decoded = buffer.decode(errors="ignore").strip()
                        for raw in decoded.splitlines():
                            if not raw.strip():
                                continue
                            try:
                                content = json.loads(raw)
                            except json.JSONDecodeError:
                                continue

                            print(content)
                            msg_id = content.get("id")
                            message = None

                            if "result" in content:
                                message = JSONRPCResponse.model_validate(content)
                            elif "error" in content:
                                err = Error.model_validate(content["error"])
                                message = JSONRPCError(
                                    id=msg_id,
                                    error=err,
                                    message=err.message,
                                )

                            # Resolve pending Future
                            if msg_id in self.pending:
                                fut = self.pending.pop(msg_id)
                                if not fut.done():
                                    fut.set_result(message)

                            buffer.clear()

                    except Exception as e:
                        print(f"[Stream Parse Error] {e}")
                        continue
        except Exception as e:
            print(f"[Listen Error] {e}")

    async def send_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """
        Send a JSON-RPC request and await its response via Future.
        """
        if not self.client:
            raise MCPError(code=-1, message="HTTP client not connected")

        future = asyncio.get_event_loop().create_future()
        self.pending[request.id] = future

        headers = {
            **self.headers,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        if self.mcp_session_id:
            headers["mcp-session-id"] = self.mcp_session_id
        if self.protocol_version:
            headers["mcp-protocol-version"] = self.protocol_version

        await self.client.post(self.url, headers=headers, json=request.model_dump())

        try:
            response = await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            self.pending.pop(request.id, None)
            raise MCPError(code=-1, message="Request timed out")

        if isinstance(response, JSONRPCError):
            raise MCPError(code=response.error.code, message=response.error.message)

        # If initialize method, capture protocol version
        if request.method == Method.INITIALIZE and isinstance(response, JSONRPCResponse):
            self.protocol_version = response.result.get("protocolVersion")

        return response

    async def send_notification(self, notification: JSONRPCNotification):
        """Send a fire-and-forget notification."""
        if not self.client:
            raise MCPError(code=-1, message="HTTP client not connected")

        headers = {
            **self.headers,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        if self.mcp_session_id:
            headers["mcp-session-id"] = self.mcp_session_id

        await self.client.post(self.url, headers=headers, json=notification.model_dump())

    async def disconnect(self):
        """Gracefully close the session and cancel pending Futures."""
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
            finally:
                self.listen_task = None

        if self.client:
            headers = {
                **self.headers,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if self.mcp_session_id:
                headers["mcp-session-id"] = self.mcp_session_id
            try:
                await self.client.delete(self.url, headers=headers)
            finally:
                await self.client.aclose()
                self.client = None

        # Cancel pending futures
        for fut in self.pending.values():
            if not fut.done():
                fut.cancel()
        self.pending.clear()

        self.mcp_session_id = None
        self.protocol_version = None
