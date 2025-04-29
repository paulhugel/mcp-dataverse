from datetime import datetime
import json
import logging
import sys
from typing import Optional
import urllib

import anyio
import click
from fastapi import Body
from fastapi import Request
from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import httpx
from mcp.server.lowlevel import Server
import mcp.types as types
from pyDataverse.Croissant import Croissant
import pydoi

from utils.dataframe import CroissantRecipe

logger = logging.getLogger(__name__)

def resolve_doi( doi_str):
    if not doi_str.startswith('doi:'):
        doi_str = f"doi:{doi_str}"
    doi = pydoi.get_url(urllib.parse.quote(doi_str.replace("doi:", "")))
    print(doi)
    if 'http' in doi:
        return f"{urllib.parse.urlparse(doi).scheme}://{urllib.parse.urlparse(doi).hostname}"
    else:
        print(f"DOI is {doi}")
        return None

async def fetch_website(
    url: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    headers = {
        "User-Agent": "MCP Croissant Server"
    }
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return [types.TextContent(type="text", text=response.text)]

def serialize_data(data):
    """Recursively convert datetime objects to strings."""
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, datetime):  # Ensure you import datetime
        return data.isoformat()  # Convert datetime to ISO format string
    return data

def convert_dataset_to_croissant_ml(doi: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if not doi.startswith('doi:'):
        doi = f"doi:{doi}"
    host = resolve_doi(doi)

    print(f"Getting Croissant record for Dataverse doi: {doi}", file=sys.stderr)
    
    # Fix DOI handling - check if it starts with 'doi:' prefix
    
    croissant = Croissant(doi=doi, host=host)
    try:
        record = croissant.get_record()
        return record
        #return Response(content=record, media_type="application/json")  # Return the record as JSON
    except Exception as e:
        logger.error(f"Error fetching record: {e}")
        return {"error": "Unable to fetch record from Dataverse."}

def datatool(input: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    doi = input["doi"]
    file = input["file"]
    logger.info(f"Datatool DOI is {doi}")
    semantic_croissant = CroissantRecipe(doi)
    semantic_croissant.get_files()

    # Process all files
    semantic_croissant.process_all_files(file)
    serializable_columns = {k: {col: str(v) for col, v in v.items()} for k, v in semantic_croissant.columns.items()}
    logger.info(serializable_columns)
    return serializable_columns


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-website-fetcher")

    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "fetch":
            raise ValueError(f"Unknown tool: {name}")
        if "url" not in arguments:
            raise ValueError("Missing required argument 'url'")
        return await fetch_website(arguments["url"])

    @app.call_tool()
    async def get_croissant_record(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "get_croissant_record":
            raise ValueError(f"Unknown tool: {name}")
        return await convert_dataset_to_croissant_ml(arguments["doi"])

    @app.call_tool()
    async def datatool(
        name: str, input: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "datatool":
            raise ValueError(f"Unknown tool: {name}")
        return await datatool(input)

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tools = [
            types.Tool(
                name="fetch",
                endpoint="fetch",
                description="Fetches a website and returns its content",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_croissant_record",
                endpoint="get_croissant_record",
                description="Convert a dataset to Croissant ML format",
                inputSchema={
                    "type": "object",
                    "required": ["doi"],
                    "properties": {
                        "doi": {"type": "string", "description": "DOI of the dataset"}
                    },
                },
            ),
            types.Tool(
                name="datatool",
                endpoint="datatool",
                description="Process a file in a dataset with DOI with datatool tool",
                inputSchema={
                    "type": "object",
                    "required": ["doi", "file"],
                    "properties": {
                        "doi": {"type": "string", "description": "DOI of the dataset"},
                        "file": {"type": "string", "description": "File to process"}
                    },
                },
            ),
        ]
        return tools

    if transport == "sse":
        from fastapi.responses import JSONResponse
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount
        from starlette.routing import Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        async def get_tools(request: Request):
            tools = await list_tools()
            # Convert tools to a serializable format
            serializable_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
            return JSONResponse(content={"tools": serializable_tools})

        async def get_status(request: Request):
            return JSONResponse(content={"status": "ok"})

        async def run_get_croissant_record(request: Request):
            if request.method == "GET":
                doi = request.query_params.get("doi")
                host = request.query_params.get("host", "https://dataverse.nl")
            else:
                body = await request.json()
                doi = body.get("doi")
                host = body.get("host", "https://dataverse.nl")

            if not doi:
                return JSONResponse(content={"error": "Missing required field 'doi'"}, status_code=400)
            
            result = convert_dataset_to_croissant_ml(doi)
            serialized_result = serialize_data(result)
            return JSONResponse(content=serialized_result)

        async def run_datatool(request: Request):
            if request.method == "GET":
                doi = request.query_params.get("doi")
                file = request.query_params.get("file")
            else:
                body = await request.json()
                doi = body.get("doi")
                file = body.get("file")

            if not doi or not file:
                return JSONResponse(content={"error": "Missing required fields 'doi' and 'file'"}, status_code=400)

            input_data = {"doi": doi, "file": file}
            result = await datatool(input_data)
            serialized_result = serialize_data(result)
            return JSONResponse(content=serialized_result)

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
                Route("/tools", endpoint=get_tools),
                Route("/status", endpoint=get_status),
                Route("/tools/get_croissant_record", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/tools/croissant/dataverse", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/tools/croissant/kaggle", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/github", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/huggingface", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/openml", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/zenodo", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/figshare", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant/dspace", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/croissant", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
                Route("/datatool", endpoint=run_datatool, methods=["GET", "POST"]),
                Route("/mcp", endpoint=run_get_croissant_record, methods=["GET", "POST"]),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0
