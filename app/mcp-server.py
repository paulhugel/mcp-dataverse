import asyncio
import json
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

import httpx
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl, BaseModel

class InitializationOptions(BaseModel):
    server_name: str
    server_version: str
    capabilities: dict

server = Server("croissant")

@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_croissant_record",
            description="Get a record from Dataverse in Croissant format for Machine Learning",
            parameters=types.ToolParameter(
                name="doi",
                description="The DOI of the Dataverse dataset",
                required=True,
            ),
        ),
        types.Tool(
            name="search_croissant_record",
            description="Search for a record from Dataverse in Croissant format for Machine Learning",
            parameters=types.ToolParameter(
                name="doi",
                description="The DOI of the Dataverse dataset",
                required=True,
            ),
        ),
    ]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="huggingface",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())

