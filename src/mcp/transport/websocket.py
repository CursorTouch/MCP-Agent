from src.mcp.types.json_rpc import JSONRPCRequest, JSONRPCResponse, JSONRPCError, Error, JSONRPCNotification
from src.mcp.exception import MCPError
from typing import Optional, Dict
import websockets
import asyncio
import json


class WebSocketTransport:
    """
    WebSocket Transport for MCP
    Uses asyncio.Future for one-shot request/response correlation.
    """

    def __init__(self, url: str, headers: Optional[dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}
        self.websocket: Optional[websockets.ClientConnection] = None
        self.listen_task: Optional[asyncio.Task] = None
        self.pending: Dict[str, asyncio.Future] = {}  # request.id -> Future

    async def connect(self):
        """Create a WebSocket client and start listening."""
        self.websocket = await websockets.connect(
            self.url,
            additional_headers=self.headers,
            subprotocols=["mcp"],
        )
        self.listen_task = asyncio.create_task(self.listen())

    async def send_response(self, response: JSONRPCResponse):
        """Send a JSON-RPC response."""
        if not self.websocket:
             raise MCPError(code=-1, message="WebSocket not connected")
        await self.websocket.send(json.dumps(response.model_dump()))

    async def listen(self):
        """Listen for JSON-RPC messages from the MCP server."""
        try:
            async for data in self.websocket:
                try:
                    content: dict = json.loads(data)
                    
                    if "result" in content:
                        msg_id = content.get("id")
                        message = JSONRPCResponse.model_validate(content)
                        # Resolve the corresponding pending future
                        future = self.pending.pop(msg_id, None)
                        if future and not future.done():
                             future.set_result(message)

                    elif "method" in content:
                         message = JSONRPCRequest.model_validate(content)
                         response = await self.handle_request(message)
                         await self.send_response(response)

                    elif "error" in content:
                        msg_id = content.get("id")
                        err = Error.model_validate(content["error"])
                        message = JSONRPCError(id=msg_id, error=err, message=err.message)
                        # Resolve the corresponding pending future
                        future = self.pending.pop(msg_id, None)
                        if future and not future.done():
                            future.set_result(message)
                    else:
                        # Ignore notifications or invalid messages for now
                        continue

                except Exception as e:
                    print(f"Error parsing WebSocket message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"WebSocket listen error: {e}")

    async def send_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """
        Send a JSON-RPC request and wait for its response.
        """
        if not self.websocket:
            raise MCPError(code=-1, message="WebSocket not connected")

        future = asyncio.get_event_loop().create_future()
        self.pending[request.id] = future

        await self.websocket.send(json.dumps(request.model_dump()))

        try:
            response = await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            self.pending.pop(request.id, None)
            raise MCPError(code=-1, message="Request timed out.")

        if isinstance(response, JSONRPCError):
            raise MCPError(code=response.error.code, message=response.error.message)

        return response

    async def send_notification(self, notification: JSONRPCNotification):
        """
        Send a JSON-RPC notification (fire and forget).
        """
        if not self.websocket:
            raise MCPError(code=-1, message="WebSocket not connected")

        await self.websocket.send(json.dumps(notification.model_dump()))

    async def disconnect(self):
        """Gracefully close the WebSocket connection."""
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
            finally:
                self.listen_task = None

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        # Cancel any unresolved Futures
        for fut in self.pending.values():
            if not fut.done():
                fut.cancel()
        self.pending.clear()
