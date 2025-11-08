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
    async def recieved_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """
        Receive a JSON-RPC request from the MCP server and await response.

        Args:
            request: JSONRPCRequest object

        Returns:
            JSONRPCResponse
        """
        pass
