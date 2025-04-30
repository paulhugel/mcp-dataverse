from fastapi import Request
from mcp.server.lowlevel import Server
import mcp.types as types
import uvicorn
from fastapi.responses import JSONResponse
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from fastapi.responses import StreamingResponse
import asyncio
import click

import logging

logger = logging.getLogger(__name__)
server = Server("semantic-croissant")

# Register tool metadata
@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="hello",
            endpoint="/hello",
            description="Say hello to a name",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                }
            }
        )
    ]

# Register actual tool logic
async def hello_tool(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return JSONResponse(content={"error": "Invalid JSON body"}, status_code=400)


# Expose FastAPI app
@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("semantic-croissant")

    @app.call_tool()
    async def hello_tool(request: Request):
        data = await request.json()
        name = data.get("name", "world")
        return {"message": f"Hello, {name}!"}

    async def some_async_stream_function():
        yield "data: Hello, world!\n\n"  # Send a string formatted for SSE

    async def sse_server(request: Request):
        async def stream_response():
            try:
                async for chunk in some_async_stream_function():  # Ensure this function yields strings or bytes
                    yield chunk  # Ensure chunk is a string or bytes
            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                yield "data: Streaming error occurred\n\n"  # Send a string formatted for SSE

        return StreamingResponse(stream_response(), media_type="text/event-stream")

    async def mcp_server(request: Request):
        return JSONResponse(content={"message": "Hello, world!"})

    if transport == "sse":

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            try:
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    try:
                        await app.run(
                            streams[0], streams[1], app.create_initialization_options()
                        )
                    except Exception as e:
                        logger.error(f"Error in app.run: {e}")
                        raise
            except Exception as e:
                logger.error(f"Error in SSE connection: {e}")
                raise

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=sse_server),
                Route("/mcp", endpoint=mcp_server),

            ],
        )

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)

