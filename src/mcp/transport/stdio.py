from src.mcp.types.json_rpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCNotification,
    Error, Method
)
from src.mcp.transport.utils import get_default_environment
from src.mcp.types.elicitation import ElicitRequest
from src.mcp.types.stdio import StdioServerParams
from src.mcp.types.sampling import MessageRequest
from src.mcp.transport.base import BaseTransport
from src.mcp.types.roots import ListRootsRequest
from src.mcp.exception import MCPError
from asyncio.subprocess import Process
import asyncio
import json
import sys


class StdioTransport(BaseTransport):
    """
    Stdio Transport for MCP
    """

    def __init__(self, params: StdioServerParams):
        self.params = params
        self.process: Process | None = None
        self.listen_task: asyncio.Task | None = None
        self.pending: dict[str | int, asyncio.Future] = {}

    async def connect(self) -> None:
        """Create a subprocess and start the listener."""
        command = self.params.command
        args = self.params.args

        env = get_default_environment() if self.params.env is None else {
            **get_default_environment(),
            **self.params.env,
        }

        # Handle Windows npx quirk
        if sys.platform == "win32" and command == "npx":
            command = "cmd"
            args = ["/c", "npx", *args]

        self.process = await asyncio.create_subprocess_exec(
            command,
            *args,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        self.listen_task = asyncio.create_task(self.listen())

    async def send_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """
        Send a JSON-RPC request to the MCP server and await response.
        """
        if not self.process or not self.process.stdin:
            raise MCPError(code=-1, message="Process not connected")

        future = asyncio.get_event_loop().create_future()
        self.pending[request.id] = future

        # Send request
        if self.process.stdin.is_closing():
            raise MCPError(code=-1, message="Process stdin is closing")
        self.process.stdin.write((json.dumps(request.model_dump()) + "\n").encode())
        await self.process.stdin.drain()

        try:
            response = await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            self.pending.pop(request.id, None)
            raise MCPError(code=-1, message="Request timed out")

        if isinstance(response, JSONRPCError):
            raise MCPError(code=response.error.code, message=response.error.message)

        return response
    
    async def send_response(self, response: JSONRPCResponse):
        if not self.process or not self.process.stdin:
            raise MCPError(code=-1, message="Process not connected")
        
        if self.process.stdin.is_closing():
             raise MCPError(code=-1, message="Process stdin is closing")

        self.process.stdin.write((json.dumps(response.model_dump()) + "\n").encode())
        await self.process.stdin.drain()
    
    async def send_notification(self, notification: JSONRPCNotification) -> None:
        """
        Send a JSON-RPC notification (fire-and-forget).
        """
        if not self.process or not self.process.stdin:
            raise MCPError(code=-1, message="Process not connected")

        self.process.stdin.write((json.dumps(notification.model_dump()) + "\n").encode())
        await self.process.stdin.drain()

    async def listen(self):
        """
        Listen for responses from the subprocess (stdout).
        """
        while True:
            try:
                line = await self.process.stdout.readline()
                if not line:
                    break
                
                try:
                    content: dict = json.loads(line.decode().strip())

                    if "result" in content: # Response
                        message = JSONRPCResponse.model_validate(content)
                    elif "method" in content: # Request
                        message = JSONRPCRequest.model_validate(content)
                        response=await self.handle_request(message)
                        await self.send_response(response)
                    elif "error" in content: # Error
                        err = Error.model_validate(content["error"])
                        message = JSONRPCError(id=content.get("id"), error=err, message=err.message)
                    else:
                        continue

                    msg_id = content.get("id")
                    future = self.pending.pop(msg_id, None)
                    if future and not future.done():
                        future.set_result(message)

                except json.JSONDecodeError:
                    continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error reading from process: {e}")

    async def disconnect(self):
        """Gracefully disconnect and terminate the process."""
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
            finally:
                self.listen_task = None

        if self.process:
            if self.process.stdin:
                try:
                    self.process.stdin.write_eof()
                except Exception:
                    pass
                self.process.stdin.close()
                if hasattr(self.process.stdin, "wait_closed"):
                    await self.process.stdin.wait_closed()

            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                print("Process did not terminate in time; killing it.")
                self.process.kill()
                await self.process.wait()

            self.process = None

        # Cancel pending futures
        for fut in self.pending.values():
            if not fut.done():
                fut.cancel()
        self.pending.clear()
