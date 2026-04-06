"""
Sigil MCP Server
Exposes Sigil tools via Model Context Protocol.
Any MCP-compatible AI product can mount this as a knowledge source.

Integration example (Claude Desktop):
  {
    "mcpServers": {
      "sigil": { "url": "http://localhost:3000/tools" }
    }
  }
"""

import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

from core.router import SigilRouter


_TOOLS = [
    {
        "name": "sigil_query",
        "description": (
            "Query the Sigil symbolic address index. "
            "Accepts exact symbolic addresses (e.g. 'equipment.pump.fault.seal_leak.symptom'), "
            "address prefixes (e.g. 'equipment.pump'), or natural language. "
            "Returns exact knowledge fragments with source location and provenance."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Symbolic address, prefix, or natural language query",
                }
            },
            "required": ["address"],
        },
    },
    {
        "name": "sigil_list",
        "description": (
            "List all symbolic addresses in the index. "
            "Use this to explore what knowledge is available before querying."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prefix": {
                    "type": "string",
                    "description": "Optional prefix to filter (e.g. 'equipment.pump')",
                }
            },
        },
    },
    {
        "name": "sigil_backlinks",
        "description": (
            "Get all knowledge nodes that link to a given address. "
            "Useful for discovering related knowledge across documents."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Symbolic address to find backlinks for",
                }
            },
            "required": ["address"],
        },
    },
    {
        "name": "sigil_skill_cards",
        "description": (
            "List all document Skill Cards. "
            "Each Skill Card describes what a document can and cannot answer. "
            "Use this to route queries to the right document before retrieving evidence."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def create_mcp_app(router: SigilRouter) -> FastAPI:
    app = FastAPI(
        title="Sigil MCP Server",
        description="Symbolic knowledge indexing — Every answer has an address.",
        version="1.0.0",
    )

    @app.get("/")
    async def root():
        return {
            "name": "sigil",
            "version": "1.0.0",
            "description": "Sigil — Symbolic knowledge indexing. Every answer has an address.",
            "protocol": "MCP-compatible",
            "tools": len(_TOOLS),
        }

    @app.get("/tools")
    async def list_tools():
        """MCP tool discovery endpoint."""
        return {"tools": _TOOLS}

    @app.post("/tools/call")
    async def call_tool(request: Request):
        """Execute a tool call."""
        body = await request.json()
        name  = body.get("name", "")
        inp   = body.get("input", {})

        try:
            if name == "sigil_query":
                result = router.query(inp.get("address", ""))
            elif name == "sigil_list":
                result = router.list_addresses(prefix=inp.get("prefix", ""))
            elif name == "sigil_backlinks":
                result = router.get_backlinks(inp.get("address", ""))
            elif name == "sigil_skill_cards":
                result = router.get_skill_cards()
            else:
                return JSONResponse(status_code=400, content={"error": f"Unknown tool: {name}"})

            return {
                "content": [
                    {"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}
                ]
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.get("/mcp")
    async def sse_endpoint():
        """SSE endpoint for MCP streaming clients."""
        async def stream():
            yield f"data: {json.dumps({'jsonrpc':'2.0','method':'notifications/tools/list_changed','params':{}})}\n\n"
        return StreamingResponse(stream(), media_type="text/event-stream")

    return app


def run(router: SigilRouter, host: str = "0.0.0.0", port: int = 3000):
    app = create_mcp_app(router)
    uvicorn.run(app, host=host, port=port, log_level="warning")
