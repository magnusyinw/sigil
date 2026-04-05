# Sigil

**Turn documents into symbols.**

> Symbol over vector. Address over chunk. Every answer has an address.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Spec](https://img.shields.io/badge/spec-v1.0.0-green.svg)](SPEC.md)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)]()

---

## What is Sigil?

Sigil is an open-source knowledge indexing engine that converts unstructured documents into **symbolic address indexes** — a deterministic, token-efficient, and auditable alternative to vector-based RAG retrieval.

Instead of this:

```
Query → Embedding → Cosine similarity → Top-k chunks → Probabilistic answer
```

Sigil does this:

```
Query → Symbol lookup → Exact address → Precise content fragment
```

**Example:**

```
ai.definition.mccarthy.what
  → [§2.s2 | anchor:"制造智能机器的科学与工程"]
  → "约翰·麦卡锡于1955年对人工智能的定义是'制造智能机器的科学与工程'"
  → 42 tokens used (vs ~1,800 for RAG)
```

---

## Why Sigil?

| | RAG | Sigil |
|--|-----|-------|
| Retrieval | Vector similarity | Symbolic address lookup |
| Result | Probabilistic | Deterministic |
| Token cost | High (full chunks) | Low (targeted fragments) |
| Auditability | Black box | Full path trace |
| Cross-document links | Implicit | Explicit backlinks |
| Embedding model needed | Yes | No |
| Works with any LLM | Partial | Yes |
| Structured doc accuracy | Poor | Excellent |

RAG is optimized for fuzzy natural language queries.
Sigil is optimized for **knowledge that has a right address**.

---

## How It Works

### Step 1 — Ingest a document

Sigil sends your document through its indexing prompt (powered by any LLM you configure) and generates a symbolic address index:

```
equipment.pump.fault.seal_leak.symptom → [§3.2.s1 | anchor:"vibration at shaft coupling"]
equipment.pump.fault.seal_leak.how     → [§4.1.s2 | anchor:"replace mechanical seal and"]
equipment.pump.fault.seal_leak.ref     → [§4.1.s4 | anchor:"See Maintenance Manual Rev.3"]
```

### Step 2 — Query by address

```bash
sigil query "equipment.pump.fault.seal_leak.symptom"
# → returns exact content fragment + source location + backlinks
```

### Step 3 — Plug into any AI product

Sigil exposes an MCP server. Any MCP-compatible AI product (Claude, GPT, Coze, Dify, etc.) can mount it as a knowledge source with zero code changes.

```yaml
# In your AI product's MCP config
mcp_servers:
  - name: sigil
    url: http://localhost:3000/mcp
```

---

## Quickstart

### Requirements

- Node.js 18+ or Python 3.10+
- Any LLM API key (Anthropic, OpenAI, or local Ollama)

### Install

```bash
git clone https://github.com/your-org/sigil.git
cd sigil
npm install
cp config/sigil.config.example.yaml sigil.config.yaml
```

### Configure your LLM

```yaml
# sigil.config.yaml
llm:
  provider: anthropic           # anthropic | openai | ollama
  model: claude-sonnet-4-6
  api_key: ${ANTHROPIC_API_KEY}
```

Sigil works with any instruction-following model. For local/offline use, set `provider: ollama`.

### Index your first document

```bash
# Index a single file
sigil index ./docs/my-document.pdf

# Index a folder
sigil index ./docs/
```

### Query

```bash
# Exact address
sigil query "ai.definition.mccarthy.what"

# Prefix query — returns all nodes under this path
sigil query "ai.definition"

# List all addresses
sigil list

# Filter by prefix
sigil list --prefix "equipment.pump"
```

### Start MCP server

```bash
sigil serve --mcp
# MCP server running at http://localhost:3000
```

---

## Address Format

Every piece of knowledge gets a precise symbolic address:

```
[domain].[subdomain].[concept].[dimension]
```

**Domains** — top-level subject area

```
ai  |  agent  |  equipment  |  medicine  |  law  |  finance  |  engineering
```

**Subdomains** — thematic category

```
definition  |  architecture  |  workflow  |  capability
method  |  metric  |  challenge  |  validation  |  standard
```

**Concepts** — specific named element, lowercase with underscores

```
mccarthy  |  seal_leak  |  weak_ai  |  oauth2  |  capa_workflow
```

**Dimensions** — always exactly one of seven values

| Dimension | Meaning |
|-----------|---------|
| `.what` | Definition, identity, description |
| `.why` | Cause, reason, background |
| `.how` | Method, process, steps |
| `.symptom` | Observable sign, phenomenon |
| `.effect` | Outcome, consequence, impact |
| `.limit` | Boundary, constraint, failure mode |
| `.ref` | Citation, source, attribution |

**Full example:**

```
equipment.pump.fault.seal_leak.symptom
└─domain  └─subdomain └─concept       └─dimension
```

---

## Multi-Document Support

Sigil handles multiple documents with a namespace system that automatically:

- **Merges** complementary nodes from different documents into joint nodes
- **Flags** contradictory nodes for human review
- **Registers** bidirectional backlinks across documents automatically

```
doc_a: agent.validation.workflow.how    → coexists with ↓
doc_b: agent.validation.rag.how         → both returned on prefix query

doc_a: agent.metric.accuracy.what       → merged with ↓
doc_b: agent.metric.accuracy.what       → joint node, both sources shown

doc_a: agent.standard.api.what          → conflicts with ↓
doc_b: agent.standard.api.what          → ⚠ flagged for human review
```

---

## Skill Cards

Every document generates a **Skill Card** — a structured declaration of what it can answer:

```yaml
skill_card:
  purpose: "Explains AI agent architecture for industrial integration"
  strengths:
    - Module architecture queries
    - Step-by-step implementation queries
    - GMP compliance queries
  weaknesses:
    - Specific algorithm implementation
    - Post-2024 regulatory updates
```

Skill Cards let AI products decide which document to query before retrieving content — no wasted tokens on the wrong source.

---

## Backlinks

Sigil automatically detects relationships between documents and creates bidirectional backlinks with confidence scoring:

```
ai.component.learning.what
  → backlinks:
      agent.architecture.cognitive.what   [EXTERNAL | HIGH]
      ai.capability.weak.how              [INTERNAL | MEDIUM]
```

Confidence levels: `HIGH` — explicitly named / `MEDIUM` — strongly related / `LOW` — peripheral overlap

---

## Token Efficiency

Same query. Same content. Dramatically fewer tokens.

```
Traditional RAG:   ~1,800 tokens per query  (full chunk retrieval)
Sigil:                 42 tokens per query  (targeted fragment)
Reduction:             97.7%
```

The difference compounds with index size. At 1,000 queries/day, Sigil's token savings pay for itself.

---

## Repository Structure

```
sigil/
├── README.md                     ← you are here
├── SPEC.md                       ← full open specification
├── LICENSE                       ← Apache 2.0
├── sigil.config.example.yaml     ← configuration template
│
├── core/
│   ├── indexer/                  ← document → symbolic address engine
│   ├── router/                   ← three-tier query router
│   └── resolver/                 ← conflict resolution + version control
│
├── mcp/
│   └── server/                   ← Sigil MCP server
│
├── api/
│   └── rest/                     ← REST API server
│
├── registry/
│   └── namespace.yaml            ← global domain/subdomain registry
│
└── examples/
    ├── technical/                 ← English technical document example
    └── multi-doc/                 ← Multi-document namespace example
```

---

## Configuration Reference

```yaml
# sigil.config.yaml

llm:
  provider: anthropic           # anthropic | openai | ollama | custom
  model: claude-sonnet-4-6
  api_key: ${SIGIL_LLM_KEY}
  base_url: ~                   # optional: local or proxy endpoint

indexing:
  key_depth_min: 3
  key_depth_max: 4
  language: auto                # auto | zh | en | ja | ...
  anchor_min_chars: 7
  anchor_max_chars: 15
  confidence_threshold: 0.8
  auto_backlink: true

storage:
  backend: sqlite               # sqlite | postgres | neo4j
  path: ./sigil.db

interface:
  mcp:
    enabled: true
    port: 3000
  rest_api:
    enabled: true
    port: 3001

logging:
  level: info
  audit_trail: true
```

---

## REST API

```bash
# Query by address
GET /api/query?address=ai.definition.mccarthy.what

# List all addresses under a prefix
GET /api/list?prefix=ai.definition

# Get backlinks
GET /api/backlinks?address=ai.definition.mccarthy.what&direction=both

# List all Skill Cards
GET /api/skill-cards

# Index a new document
POST /api/index
Content-Type: multipart/form-data
Body: file=@document.pdf
```

---

## Roadmap

```
v1.0  Core engine
  ✓ Symbolic address indexing
  ✓ Dual-anchor location system
  ✓ Multi-document namespace
  ✓ Backlink protocol
  ✓ MCP server
  ✓ REST API
  ✓ SQLite storage

v1.1  Stability
  ○ Postgres backend
  ○ Index quality dashboard
  ○ CLI improvements

v1.2  Ecosystem
  ○ Neo4j backend
  ○ Community registry
  ○ Domain templates (legal, medical, engineering)

v2.0  Scale
  ○ Distributed index
  ○ Real-time document sync
  ○ Sigil Cloud
```

---

## Contributing

Contributions are welcome in four areas:

**Core engine** — indexer, router, resolver improvements

**Registry proposals** — new domains and subdomains for the global registry
Open an issue with label `registry-proposal`. Requirements in [SPEC.md §10](SPEC.md#10-global-registry).

**Domain templates** — pre-built configurations for specific industries
(pharmaceutical GMP, legal contracts, engineering manuals, academic papers)

**Examples** — real-world indexing cases in `examples/`

---

## Specification

The full open specification is in [`SPEC.md`](SPEC.md). It defines address format rules, the V3 indexing prompt, namespace protocol, query routing, backlink protocol, version control, the global registry, and MCP interface.

Sigil's indexing behavior is fully defined by the spec. Any LLM that follows the spec produces a compatible index. The spec itself is open — proposals and improvements welcome.

---

## License

Apache 2.0 — see [LICENSE](LICENSE). Free to use, modify, and distribute. Commercial use permitted. The core engine will always be open source.

---

*Every answer has an address.*
