from src.mcp.types.json_rpc import JSONRPCMessage,JSONRPCResponse
from src.mcp.exception import MCPError
from src.mcp.exception import MCPError
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
        self, request: JSONRPCMessage
    ) -> JSONRPCResponse | None:
        """
        Send a JSON-RPC request to the MCP server and wait for a response.

        Args:
            request: JSONRPCMessage object

        Returns:
            JSONRPCResponse or None

        Raises:
            TimeoutError: If the request times out.
            Exception: If the request fails.
        """
        pass

    @abstractmethod
    async def send_notification(self, notification: JSONRPCMessage) -> None:
        """
        Send a JSON-RPC notification to the MCP server.

        Args:
            notification: JSONRPCMessage object
        """
        pass

    @abstractmethod
    async def send_response(self, response: JSONRPCResponse) -> None:
        """
        Send a JSON-RPC response to the MCP server.
        """
        pass

    async def handle_request(self, request: JSONRPCMessage) -> JSONRPCResponse | None:
        """
        Handle a JSON-RPC request from the MCP server.
        """
        from src.mcp.types.sampling import CreateMessageRequestParams
        from src.mcp.types.elicitation import ElicitRequestParams
        from src.mcp.types.common import RequestParams
        from src.mcp.types.json_rpc import Method
        from pydantic import TypeAdapter
        
        match request.method:
            case Method.SAMPLING_CREATE_MESSAGE:
                params=TypeAdapter(CreateMessageRequestParams).validate_python(request.params)
                sampling_callback = self.callbacks.get("sampling")
                if sampling_callback is None:
                    raise Exception("Sampling callback not found")
                result=await sampling_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(by_alias=True, exclude_none=True))
            
            case Method.ELICITATION_CREATE:
                params=TypeAdapter(ElicitRequestParams).validate_python(request.params)
                elicitation_callback = self.callbacks.get("elicitation")
                if elicitation_callback is None:
                    raise Exception("Elicitation callback not found")
                result=await elicitation_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(by_alias=True, exclude_none=True))
            
            case Method.ROOTS_LIST:
                params = TypeAdapter(RequestParams).validate_python(request.params) if request.params else None
                list_roots_callback = self.callbacks.get("list_roots")
                if list_roots_callback is None:
                    raise Exception("List roots callback not found")
                result=await list_roots_callback(params=params)
                return JSONRPCResponse(id=request.id,result=result.model_dump(by_alias=True, exclude_none=True))
            
            case _:
                raise MCPError(code=-1, message=f"Unknown method: {request.method}")

    async def handle_notification(self, notification: JSONRPCMessage) -> None:
        """
        Handle a JSON-RPC notification from the MCP server.
        """
        from src.mcp.types.json_rpc import Method
        from src.mcp.types.logging import LogMessageNotificationParams
        
        match notification.method:
            case Method.NOTIFICATION_MESSAGE:
                 if notification.params:
                    params = LogMessageNotificationParams.model_validate(notification.params)
                    logging_callback = self.callbacks.get("logging")
                    if logging_callback:
                        await logging_callback(params=params)
            
            case _:
                # Ignore unknown notifications
                pass

