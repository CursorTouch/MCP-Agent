from src.mcp.types.json_rpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCNotification,
)
from abc import ABC, abstractmethod
from typing import Callable

class BaseTransport(ABC):
    """
    Abstract base class for all MCP transport implementations.
    Provides the minimal interface for sending requests,
    sending notifications, and listening for incoming messages.
    """

    def attach_callbacks(self, callbacks:dict[str,Callable]):
        self.callbacks = callbacks

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the MCP server.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close connection to the MCP server.
        """
        pass

    @abstractmethod
    async def send_request(
        self, request: JSONRPCRequest
    ) -> JSONRPCResponse | JSONRPCError | None:
        """
        Send a JSON-RPC request to the MCP server and wait for a response.

        Args:
            request: JSONRPCRequest object

        Returns:
            JSONRPCResponse or JSONRPCError

        Raises:
            TimeoutError: If the request times out.
            Exception: If the request fails.
        """
        pass

    @abstractmethod
    async def send_notification(self, notification: JSONRPCNotification) -> None:
        """
        Send a JSON-RPC notification to the MCP server.

        Args:
            notification: JSONRPCNotification object
        """
        pass

    @abstractmethod
    async def send_response(self, response: JSONRPCResponse) -> None:
        """
        Send a JSON-RPC response to the MCP server.
        """
        pass

    async def handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """
        Handle a JSON-RPC request from the MCP server.
        """
        from src.mcp.types.sampling import MessageRequest
        from src.mcp.types.elicitation import ElicitRequest
        from src.mcp.types.roots import ListRootsRequest
        from src.mcp.types.json_rpc import Method
        
        match request.method:
            case Method.SAMPLING_CREATE_MESSAGE:
                params=MessageRequest.model_validate(request.params)
                sampling_callback = self.callbacks.get("sampling")
                if sampling_callback is None:
                    raise Exception("Sampling callback not found")
                result=await sampling_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(exclude_none=True))
            
            case Method.ELICITATION_CREATE:
                params=ElicitRequest.model_validate(request.params)
                elicitation_callback = self.callbacks.get("elicitation")
                if elicitation_callback is None:
                    raise Exception("Elicitation callback not found")
                result=await elicitation_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(exclude_none=True))
            
            case Method.ROOTS_LIST:
                params=ListRootsRequest.model_validate(request.params)
                list_roots_callback = self.callbacks.get("list_roots")
                if list_roots_callback is None:
                    raise Exception("List roots callback not found")
                result=await list_roots_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(exclude_none=True))
            
            case _:
                raise MCPError(code=-1, message=f"Unknown method: {request.method}")
