# Getting Started with Sigil

> Every answer has an address.

---

## What you need

- Python 3.10+
- API key for any supported LLM (Anthropic, OpenAI, or local Ollama)
- A document to index (PDF, DOCX, Markdown, TXT, or HTML)

---

## Install

```bash
git clone https://github.com/sigil-index/sigil.git
cd sigil
pip install -r requirements.txt
```

---

## Configure

```bash
sigil init
```

This creates `sigil.config.yaml`. Open it and set your LLM provider:

```yaml
llm:
  provider: anthropic           # or: openai | ollama | custom
  model: claude-sonnet-4-6      # or: gpt-4o | llama3.2 | etc.
  api_key: ${ANTHROPIC_API_KEY} # reads from environment variable
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # Anthropic
# or
export OPENAI_API_KEY=sk-...            # OpenAI
```

For Ollama (fully local, no API key needed):

```yaml
llm:
  provider: ollama
  model: llama3.2
  base_url: http://localhost:11434
```

---

## Index your first document

```bash
sigil index ./my-document.pdf
```

Sigil calls your LLM to generate a symbolic address index. You'll see:

```
Sigil  Indexing: ./my-document.pdf

✓ Indexed: My Document
  Doc ID : a1b2c3d4
  Domain : equipment
  Nodes  : 23 symbolic addresses

Skill Card
  Purpose : Explains centrifugal pump fault diagnosis and maintenance.
  ✓ Fault symptom queries
  ✓ Corrective action queries
  ✗ General hydraulics theory
```

---

## Query the index

```bash
# Exact address — deterministic, ~42 tokens
sigil query "equipment.pump.fault.seal_leak.symptom"

# Prefix — returns all children
sigil query "equipment.pump.fault"

# Natural language — fuzzy search
sigil query "vibration in centrifugal pump"

# Browse everything
sigil list
sigil list --prefix "equipment.pump"
```

---

## Start the servers

```bash
sigil serve
```

This starts:
- **MCP server** at `http://localhost:3000` — for AI product integration
- **REST API** at `http://localhost:3001` — for direct HTTP access
- **API docs** at `http://localhost:3001/docs`

---

## Connect to an AI product

Add Sigil as an MCP server in your AI product's configuration:

**Claude Desktop** (`config.json`):
```json
{
  "mcpServers": {
    "sigil": { "url": "http://localhost:3000/tools" }
  }
}
```

**Generic MCP client**:
```
Tool discovery: GET http://localhost:3000/tools
Tool execution: POST http://localhost:3000/tools/call
```

Your AI product now has access to four tools:
- `sigil_query` — retrieve evidence by address
- `sigil_list` — browse available addresses
- `sigil_backlinks` — find related nodes
- `sigil_skill_cards` — route queries to the right document

---

## Next steps

- [Architecture](architecture.md) — how Sigil works internally
- [Configuration](config.md) — all config options explained
- [MCP Integration](mcp.md) — detailed MCP setup for different AI products
- [SPEC.md](../SPEC.md) — the full open specification
