from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Calculator MCP Server")

# Add an addition tool
@mcp.tool(name="add")
def add(a: int, b: int) -> str:
    """Add two numbers"""
    return f'{a} + {b} = {a + b}'

@mcp.tool(name="subtract")
def subtract(a: int, b: int) -> str:
    """Subtract two numbers"""
    return f'{a} - {b} = {a - b}'

@mcp.tool(name="multiply")
def multiply(a: int, b: int) -> str:
    """Multiply two numbers"""
    return f'{a} * {b} = {a * b}'

@mcp.tool(name="divide")
def divide(a: int, b: int) -> str:
    """Divide two numbers"""
    return f'{a} / {b} = {a / b}'

if __name__ == "__main__":
    mcp.run()