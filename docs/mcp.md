# MCP Integration Guide

Sigil exposes four tools via the Model Context Protocol (MCP).
Any MCP-compatible AI product can mount Sigil as a knowledge source.

---

## Start the MCP Server

```bash
sigil serve          # starts both MCP (port 3000) and REST API (port 3001)
sigil serve --mcp-only   # MCP server only
```

---

## Tool Reference

### sigil_query

Retrieve knowledge nodes by address, prefix, or natural language.

```json
{
  "name": "sigil_query",
  "input": { "address": "equipment.pump.fault.seal_leak.symptom" }
}
```

**Tier 1** — exact address → deterministic, ~42 tokens
**Tier 2** — address prefix → returns all children
**Tier 3** — natural language → fuzzy anchor search

### sigil_list

Browse the address space.

```json
{
  "name": "sigil_list",
  "input": { "prefix": "equipment.pump" }
}
```

### sigil_backlinks

Find related nodes across documents.

```json
{
  "name": "sigil_backlinks",
  "input": { "address": "equipment.pump.fault.seal_leak.symptom" }
}
```

### sigil_skill_cards

List Skill Cards for all indexed documents. Use this to route a query to the right document before retrieving evidence.

```json
{
  "name": "sigil_skill_cards",
  "input": {}
}
```

---

## Integration Examples

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sigil": {
      "url": "http://localhost:3000/tools"
    }
  }
}
```

### Generic MCP Client

```
Tool discovery:  GET  http://localhost:3000/tools
Tool execution:  POST http://localhost:3000/tools/call
```

Request body:
```json
{
  "name": "sigil_query",
  "input": { "address": "equipment.pump.fault.seal_leak.symptom" }
}
```

Response:
```json
{
  "content": [
    {
      "type": "text",
      "text": "{ \"tier\": 1, \"results\": [...] }"
    }
  ]
}
```

### OpenClaw (multi-agent example)

Each department agent queries its own Sigil namespace:

```python
# Equipment Agent
result = sigil_query("equipment.pump.fault.seal_leak.symptom")

# Quality Agent
result = sigil_query("quality.deviation.yield_loss.why")

# Safety Agent
result = sigil_query("safety.hazardous.chemical.handling.how")
```

---

## Recommended Workflow for AI Products

1. Call `sigil_skill_cards` to identify which document covers the query topic
2. Call `sigil_list` with the relevant prefix to see available addresses
3. Call `sigil_query` with the exact address for deterministic evidence retrieval
4. Use the returned fragment as grounded evidence in the LLM response
