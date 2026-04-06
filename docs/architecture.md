# Sigil Architecture

---

## The Three-Layer Problem

LLM retrieval pipelines conflate three distinct functions:

```
1. Candidate discovery  — find relevant regions of a corpus
2. Evidence access      — retrieve the exact fragment that grounds a claim
3. Answer generation    — reason over evidence to produce a response
```

Most systems optimize heavily for 1 and hand off coarse chunks to 3. Function 2 — evidence access — is left under-specified. Sigil fills that gap.

---

## System Architecture

```
┌──────────────────────────────────────┐
│         AI Product / LLM             │
│  (Claude, GPT, Coze, Dify, etc.)     │
└──────────────┬───────────────────────┘
               │ MCP or REST
┌──────────────▼───────────────────────┐
│            Sigil                     │
│                                      │
│  ┌─────────────┐  ┌───────────────┐  │
│  │  MCP Server │  │   REST API    │  │
│  └──────┬──────┘  └──────┬────────┘  │
│         └────────┬────────┘          │
│              ┌───▼────┐              │
│              │ Router │              │
│              └───┬────┘              │
│         ┌────────┼────────┐          │
│      Tier 1   Tier 2   Tier 3        │
│      Exact    Prefix   Fuzzy         │
│         └────────┼────────┘          │
│              ┌───▼────┐              │
│              │  DB    │              │
│              └────────┘              │
└──────────────────────────────────────┘
               │
┌──────────────▼───────────────────────┐
│          Document Corpus             │
│   PDF | DOCX | MD | TXT | HTML       │
└──────────────────────────────────────┘
```

---

## Components

### Indexer (`core/indexer.py`)

Converts documents into symbolic address indexes using the V3 prompt.

1. Parse document (PDF/DOCX/MD/TXT/HTML)
2. Truncate if needed (max 12,000 chars)
3. Call LLM with V3 prompt → JSON index
4. Parse JSON → KnowledgeNode objects
5. Save to SQLite

LLM is only called during indexing. Queries require zero LLM calls at Tier 1 and Tier 2.

### Router (`core/router.py`)

Routes queries through three tiers:

| Tier | Trigger | Mechanism | LLM calls |
|------|---------|-----------|-----------|
| 1 | Exact symbolic address | String match | 0 |
| 2 | Address prefix | LIKE query | 0 |
| 3 | Natural language | Text search | 0 |

### Storage (`storage/db.py`)

SQLite with four tables:

- `documents` — document registry with Skill Cards
- `knowledge_nodes` — all indexed fragments (address, location, anchor, content)
- `transitions` — query sequence tracking for predictive layer
- `conflict_flags` — contradictory nodes pending human review

### MCP Server (`mcp/server.py`)

Exposes four standard tools via Model Context Protocol:

- `sigil_query` — query by address, prefix, or natural language
- `sigil_list` — browse address space
- `sigil_backlinks` — find related nodes
- `sigil_skill_cards` — document routing aid

### REST API (`api/rest.py`)

Same four operations over HTTP + document upload endpoint.
Interactive Swagger docs at `/docs`.

---

## Data Model

### Knowledge Node

```
address              equipment.pump.fault.seal_leak.symptom
structural_location  §3.1.s1
anchor_phrase        "vibration at shaft coupling"
content              "Visible liquid dripping from shaft seal..."
doc_id               a1b2c3d4
doc_title            Pump Maintenance SOP
doc_version          hash:abc12345
backlinks            []
```

### Skill Card

```
purpose    "Explains centrifugal pump fault diagnosis and maintenance."
strengths  ["Fault symptom queries", "Corrective action queries"]
weaknesses ["General hydraulics theory"]
```

---

## Conflict Detection

When two documents generate the same symbolic address, Sigil checks content overlap:

- Overlap ≥ 30% → **Joint Node** (complementary content, both sources shown)
- Overlap < 30% → **Conflict Flag** (contradictory content, human review required)

---

## Token Efficiency

```
Standard chunk retrieval:  ~1,800 tokens/query  (full chunk as context)
Sigil Tier 1 exact lookup:     ~42 tokens/query  (targeted fragment only)
Reduction: 97.7%
```

---

## Extending Sigil

**New storage backend**: Implement the same interface as `SigilStorage` in `storage/db.py`.

**New document format**: Add a parser function in `core/parser.py` and register it in the dispatch dict.

**New LLM provider**: Add a method in `core/llm.py` following the `_anthropic()` pattern.
