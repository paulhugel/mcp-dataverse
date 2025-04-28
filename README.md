# MCP server for Dataverse

Usage:
```
docker-compose build
docker-compose up -d
```

Go to http://127.0.0.1:8000/tools to get overview of available tools.

You can register MCP in Cursor or Visual Studio:
```
{
  "mcpServers": {
    "Croissant": {
      "url": "http://127.0.0.1:8000/sse",
      "headers": {
        "Content-Type": "application/json"
      }
    }
}
}

```
