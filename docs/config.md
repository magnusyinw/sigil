# Configuration Reference

All Sigil configuration lives in `sigil.config.yaml`.

---

## llm

Controls which LLM is used for indexing documents.

```yaml
llm:
  provider: anthropic         # anthropic | openai | ollama | custom
  model: claude-sonnet-4-6    # model name for the chosen provider
  api_key: ${ANTHROPIC_API_KEY}  # env var or literal string
  base_url: ~                 # optional override URL
```

**Anthropic (default)**
```yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-6
  api_key: ${ANTHROPIC_API_KEY}
```

**OpenAI**
```yaml
llm:
  provider: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}
```

**Ollama (local, no API key)**
```yaml
llm:
  provider: ollama
  model: llama3.2
  base_url: http://localhost:11434
```

**Custom OpenAI-compatible endpoint**
```yaml
llm:
  provider: custom
  model: my-model
  api_key: ${MY_API_KEY}
  base_url: https://my-llm-proxy.example.com/v1
```

---

## indexing

Controls how documents are indexed.

```yaml
indexing:
  language: auto          # auto-detect | zh | en | ja | ...
  anchor_min_chars: 7     # minimum anchor phrase length
  anchor_max_chars: 15    # maximum anchor phrase length
  confidence_threshold: 0.8  # minimum confidence for backlinks
  auto_backlink: true     # automatically register reverse backlinks
  max_chars: 12000        # truncate documents longer than this
```

---

## storage

```yaml
storage:
  backend: sqlite         # sqlite (default) | postgres (v1.1)
  path: ./sigil.db        # path to SQLite database file
```

---

## interface

```yaml
interface:
  mcp:
    enabled: true
    port: 3000
  rest_api:
    enabled: true
    port: 3001
```

---

## logging

```yaml
logging:
  level: info             # debug | info | warning | error
  audit_trail: true       # log all queries for auditability
```

---

## Environment Variables

Any config value can reference an environment variable:

```yaml
api_key: ${ANTHROPIC_API_KEY}
```

Sigil resolves `${VAR_NAME}` patterns at startup.
