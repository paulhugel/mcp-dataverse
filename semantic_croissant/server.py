import datetime as dt
import json
import logging
import sys
import urllib
from urllib.parse import quote as url_quote, urlparse as url_urlparse
import time
from urllib.error import HTTPError
import anyio
import click
from fastapi import Request
import httpx
from mcp.server.lowlevel import Server
from mcp.server.session import ServerSession
import mcp.types as types
from pyDataverse.Croissant import Croissant
import requests
#from mcp.server.lowlevel import TextContent
#from mcp.schema import TextContent
#from utils.MultiMedia import MultiMedia
import pydoi
import os

from utils.dataframe import CroissantRecipe
####################################################################################
# Temporary monkeypatch which avoids crashing when a POST message is received
# before a connection has been initialized, e.g: after a deployment.
# pylint: disable-next=protected-access
old__received_request = ServerSession._received_request


async def _received_request(self, *args, **kwargs):
    try:
        return await old__received_request(self, *args, **kwargs)
    except RuntimeError:
        pass


# pylint: disable-next=protected-access
ServerSession._received_request = _received_request
####################################################################################\
logger = logging.getLogger(__name__)

def resolve_doi( doi_str):
    if not doi_str.startswith('doi:'):
        doi_str = f"doi:{doi_str}"
    doi = pydoi.get_url(url_quote(doi_str.replace("doi:", "")))
    print(doi)
    if 'http' in doi:
        parsed = url_urlparse(doi)
        return f"{parsed.scheme}://{parsed.hostname}"
    else:
        print(f"DOI is {doi}")
        return None

async def fetch_website(
    url: str,
) -> str:
    headers = {
        "User-Agent": "MCP Croissant Server"
    }
    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

def serialize_data(data):
    """Recursively convert non-JSON types (datetime/date/time) to strings.

    Ensures external clients never see Python datetime objects which
    would otherwise raise "Object of type datetime is not JSON serializable".
    """
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, (dt.datetime, dt.date, dt.time)):
        return data.isoformat()
    return data

def convert_dataset_to_croissant_ml(doi: str, max_retries: int = 3, retry_delay: int = 5) -> dict:
    if not doi.startswith('doi:'):
        doi = f"doi:{doi}"
    host = resolve_doi(doi)

    print(f"Getting Croissant record for Dataverse doi: {doi}", file=sys.stderr)
    
    for attempt in range(max_retries):
        try:
            croissant = Croissant(doi=doi, host=host)
            record = croissant.get_record()
            return record
        except HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                print(f"Rate limited, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})", file=sys.stderr)
                time.sleep(retry_delay)
                continue
            raise
        except Exception as e:
            logger.error(f"Error fetching record: {e}")
            return {"error": "Unable to fetch record from Dataverse."}
    
    return {"error": "Maximum retry attempts reached. Please try again later."}

def process_datatool(input: dict) -> dict:
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
    app = Server("semantic-croissant")

    @app.call_tool()
    async def fetch_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "fetch":
            raise ValueError(f"Unknown tool: {name}")
        if "url" not in arguments:
            raise ValueError("Missing required argument 'url'")
        html = await fetch_website(arguments["url"])
        return [types.TextContent(type="text", text=html, mimeType="text/html")]

    @app.call_tool()
    async def get_croissant_record(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        logger.info(f"Tool name received: {name}")
        if name != "get_croissant_record":
            raise ValueError(f"Unknown tool: {name}")
        record = convert_dataset_to_croissant_ml(arguments["doi"])
        serialized = serialize_data(record)
        return [types.TextContent(type="text", text=json.dumps(serialized), mimeType="application/ld+json")]

    @app.call_tool()
    async def datatool(
        name: str, input: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "datatool":
            raise ValueError(f"Unknown tool: {name}")
        result = process_datatool(input)
        return [types.TextContent(type="text", text=json.dumps(serialize_data(result)), mimeType="application/json")]

    # MCP tool: now (current time in ISO 8601 UTC)
    @app.call_tool()
    async def now(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "now":
            raise ValueError(f"Unknown tool: {name}")
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
        payload = {"now": now_iso}
        return [types.TextContent(type="text", text=json.dumps(payload), mimeType="application/json")]

    # MCP tool: overview
    @app.call_tool()
    async def overview(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "overview":
            raise ValueError(f"Unknown tool: {name}")
        url = os.environ.get("DATAVERSES")
        if not url:
            payload = {"error": "DATAVERSES env not set"}
        else:
            resp = requests.get(url)
            payload = {"installations": resp.json().get("installations")}
        return [types.TextContent(type="text", text=json.dumps(payload), mimeType="application/json")]

    # MCP tool: overview_datasets
    @app.call_tool()
    async def overview_datasets(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "overview_datasets":
            raise ValueError(f"Unknown tool: {name}")
        host = arguments.get("host")
        if not host:
            raise ValueError("Missing required argument 'host'")
        if "http" not in host:
            host = f"https://{host}"
        url = f"{host}/api/search?q=*&type=dataset&per_page=0"
        data = requests.get(url)
        content = {"datasets": data.json().get("data")}
        return [types.TextContent(type="text", text=json.dumps(content), mimeType="application/json")]

    # MCP tool: overview_files
    @app.call_tool()
    async def overview_files(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "overview_files":
            raise ValueError(f"Unknown tool: {name}")
        host = arguments.get("host")
        if not host:
            raise ValueError("Missing required argument 'host'")
        if "http" not in host:
            host = f"https://{host}"
        url = f"{host}/api/search?q=*&type=file&per_page=0"
        data = requests.get(url)
        content = {"files": data.json().get("data")}
        return [types.TextContent(type="text", text=json.dumps(content), mimeType="application/json")]

    # MCP tool: search_datasets
    @app.call_tool()
    async def search_datasets(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "search_datasets":
            raise ValueError(f"Unknown tool: {name}")
        host = arguments.get("host")
        query = arguments.get("query", "*")
        if not host:
            raise ValueError("Missing required argument 'host'")
        q = f"q={query}" if query else "q=%2A"
        if "http" not in host:
            host = f"https://{host}"
        url = f"{host}/api/search?{q}&type=dataset"
        data = requests.get(url)
        content = {"datasets": data.json().get("data")}
        return [types.TextContent(type="text", text=json.dumps(content), mimeType="application/json")]

    # Helper endpoint removed; use convert_dataset_to_croissant_ml directly in HTTP route

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tools = [
            types.Tool(
                name="fetch",
                endpoint="/fetch",
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
                endpoint="/get_croissant_record",
                description="Convert a dataset to Croissant ML format with get_croissant_record tool and explore the dataset with DOI or handle.",
                inputSchema={
                    "type": "object",
                    "required": ["doi"],
                    "properties": {
                        "doi": {"type": "string", "description": "DOI of the dataset"}
                    },
                },
            ),
            types.Tool(
                name="now",
                endpoint="/time",
                description="Returns current UTC time as ISO 8601.",
                inputSchema={
                    "type": "object",
                    "required": [],
                    "properties": {},
                },
            ),
            types.Tool(
                name="datatool",
                endpoint="/tools/datatool",
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
            types.Tool(
                name="overview",
                endpoint="/overview",
                description="Get an overview of the Dataverse installations around the world sorted by country. Entrance point for the overview tools if no hosts are provided.",
                inputSchema={
                    "type": "object",
                    "required": [],
                    "properties": {},
                },
            ),
            types.Tool(
                name="overview_datasets",
                endpoint="/overview/datasets",
                description="Get an overview of the Dataverse datasets statistics by host",
                inputSchema={
                    "type": "object",
                    "required": ["host"],
                    "properties": {
                        "host": {"type": "string", "description": "Host of the Dataverse installation (e.g. dataverse.nl)"}
                    },
                },
            ),
            types.Tool(
                name="overview_files",
                endpoint="/overview/files",
                description="Get an overview of the Dataverse files statistics by host",
                inputSchema={
                    "type": "object",
                    "required": ["host"],
                    "properties": {
                        "host": {"type": "string", "description": "Host of the Dataverse installation (e.g. dataverse.nl)"}
                    },
                },
            ),
            types.Tool(
                name="search_datasets",
                endpoint="/search/datasets",
                description="Search for datasets in a Dataverse installation",
                inputSchema={
                    "type": "object",
                    "required": ["host", "query"],
                    "properties": {
                        "host": {"type": "string", "description": "Host of the Dataverse installation (e.g. dataverse.nl)"},
                        "query": {"type": "string", "description": "Query to search for datasets"}
                    },
                },
            ),
        ]
        return tools

    if transport == "sse":
        from fastapi.responses import JSONResponse
        from fastapi import Response
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount
        from starlette.routing import Route

        sse = SseServerTransport("/messages/")

        # Middleware to relax health checks that POST to /messages/ without a valid session.
        # If a POST to /messages/ yields a 400, convert it to 202 Accepted so clients like Jan
        # don't get stuck in a health-check loop. Real sessions continue to work via SSE.
        from starlette.middleware.base import BaseHTTPMiddleware
        class MessagesHealthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                response = await call_next(request)
                try:
                    path = request.url.path or ""
                except Exception:
                    path = ""
                # Some clients probe POST /messages without a valid session.
                # If the underlying transport returns 400, convert to 204 No Content
                # so health checks pass without affecting real SSE sessions.
                if request.method == "POST" and path.startswith("/messages") and response.status_code == 400:
                    return Response(status_code=204)
                return response

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
                    "inputSchema": tool.inputSchema,
                    "endpoint": tool.endpoint
                }
                for tool in tools
            ]
            return JSONResponse(content={"tools": serializable_tools})

        async def get_status(request: Request):
            return JSONResponse(content={"status": "ok"})

        async def run_time(request: Request):
            now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
            return JSONResponse(content={"now": now_iso})

        async def run_get_croissant_record(request: Request):
            if request.method == "GET":
                doi = request.query_params.get("doi")
            else:
                body = await request.json()
                doi = body.get("doi")
                host = None

            if not doi:
                return JSONResponse(content={"error": "Missing required field 'doi'. Please provide a DOI in the format '10.18710/CHMWOB'"}, status_code=200)
            
            try:
                result = convert_dataset_to_croissant_ml(doi)
                serialized_result = serialize_data(result)
                return JSONResponse(content=serialized_result, media_type="application/ld+json")
            except Exception as e:
                logger.error(f"Error in get_croissant_record: {e}")
                return JSONResponse(content={"error": str(e)}, status_code=500)

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

            try:
                input_data = {"doi": doi, "file": file}
                result = process_datatool(input_data)
                serialized_result = serialize_data(result)
                return JSONResponse(content=serialized_result, media_type="application/json")
            except Exception as e:
                logger.error(f"Error in datatool: {e}")
                return JSONResponse(content={"error": str(e)}, status_code=500)

        async def get_mcp(request: Request):
            tools = await list_tools()
            # Convert tools to a serializable format
            serializable_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                    "endpoint": tool.endpoint
                }
                for tool in tools
            ]
            return JSONResponse(content={"tools": serializable_tools})

        async def mcp_croissant_record_endpoint(request: Request):
            logger.info(f"New croissant record endpoint called")
            data = await request.json()
            if request.method == "POST":
                doi = data.get("doi")
            else:
                doi = request.query_params.get("doi")
            #return {"status": "ok", "doi": doi}

            if request.method == "GET":
                doi = request.query_params.get("doi")
            else:
                body = await request.json()
                doi = body.get("doi")

            if not doi:
                return JSONResponse(content={"error": "Missing required field 'doi'. Please provide a DOI in the format '10.18710/CHMWOB'"}, status_code=200)

            logger.info(f"New croissant record endpoint called with doi: {doi}")
            try:
                result = convert_dataset_to_croissant_ml(doi)
                logger.info(f"Result received for DOI {doi}")
                serialized_result = serialize_data(result)
                return JSONResponse(
                    content={
                        "type": "text",
                        "mimeType": "application/ld+json",
                        "text": json.dumps(serialized_result, indent=2),
                    }
                )
                #return JSONResponse(content={"result": f"{serialized_result}"})
            except Exception as e:
                logger.error(f"Error in get_croissant_record: {e}")
                return JSONResponse(content={"error": str(e)}, status_code=500)

        async def run_fetch_website(request: Request):
            url = request.query_params["url"]
            result = await fetch_website(url)
            #serialized_result = serialize_data(result)  # Serialize the result
            #return JSONResponse(content=serialized_result)
            return Response(content=result, media_type="text/html")

        async def run_get_overview(request: Request):
            url = os.environ.get("DATAVERSES")
            if not url:
                return JSONResponse(content={"error": "DATAVERSES env not set"}, status_code=500)
            data = requests.get(url)
            installations = data.json().get('installations')
            return JSONResponse(content={"installations": installations})
            
        async def run_get_overview_datasets(request: Request):
            if request.method == "GET":
                host = request.query_params.get("host")
            else:
                body = await request.json()
                host = body.get("host")

            return search_datasets_http(host, "*")

        async def run_search_datasets(request: Request):
            if request.method == "GET":
                host = request.query_params.get("host")
                query = request.query_params.get("query")
            else:
                body = await request.json()
                host = body.get("host")
                query = body.get("query")
            return search_datasets_http(host, query)

        def search_datasets_http(host: str, query: str):
            if query:
                query = f"q={query}"
            else:
                query = "q=%2A"

            if not 'http' in host:
                host = f"https://{host}"
            url = f"{host}/api/search?{query}&type=dataset"
            data = requests.get(url)
            datasets = data.json()['data']
            return JSONResponse(content={"datasets": datasets})

        async def run_get_overview_files(request: Request):
            if request.method == "GET":
                host = request.query_params.get("host")
            else:
                body = await request.json()
                host = body.get("host")

            if not 'http' in host:
                host = f"https://{host}"
            url = f"{host}/api/search?q=*&type=file&per_page=0"
            data = requests.get(url)
            files = data.json()['data']
            return JSONResponse(content={"files": files})


        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
                # Root alias for health checks (some clients probe "/").
                Route("/", endpoint=get_status),
                Route("/tools", endpoint=get_tools, methods=["GET", "POST"]),
                Route("/status", endpoint=get_status),
                Route("/time", endpoint=run_time),
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
                Route("/mcp", endpoint=get_mcp, methods=["GET", "POST"]),
                Route("/mcp/list_tools", endpoint=get_mcp, methods=["GET", "POST"]),
                Route("/get_croissant_record", endpoint=mcp_croissant_record_endpoint, methods=["GET", "POST"]),
                Route("/fetch", endpoint=run_fetch_website, methods=["GET", "POST"]),
                Route("/overview", endpoint=run_get_overview, methods=["GET", "POST"]),
                Route("/overview/datasets", endpoint=run_get_overview_datasets, methods=["GET", "POST"]),
                Route("/search/datasets", endpoint=run_search_datasets, methods=["GET", "POST"]),
                Route("/overview/files", endpoint=run_get_overview_files, methods=["GET", "POST"]),
            ],
        )

        # Ensure the server is ready before starting
        async def startup():
            logger.info("Server is ready to handle requests")

        starlette_app.add_event_handler("startup", startup)
        # Install middleware after app creation
        starlette_app.add_middleware(MessagesHealthMiddleware)

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server
        logger.info("Starting MCP server in stdio mode")
        async def arun():
            try:
                # Initialize the stdio server
                async with stdio_server() as streams:
                    logger.info("Server is ready to handle requests")
                    
                    # Create initialization options
                    init_options = app.create_initialization_options()
                    
                    # Run the app with proper error handling
                    try:
                        await app.run(streams[0], streams[1], init_options)
                    except Exception as e:
                        logger.error(f"Error running app: {e}")
                        raise
                        
            except Exception as e:
                logger.error(f"Error in stdio server: {e}")
                raise

        anyio.run(arun)

    return 0
