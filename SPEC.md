# Sigil Specification
**Version:** 1.0.0
**License:** Apache 2.0
**Status:** Draft

> Turn documents into symbols.
> Symbol over vector. Address over chunk.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Concept](#2-core-concept)
3. [Symbolic Address Format](#3-symbolic-address-format)
4. [Indexing Rules](#4-indexing-rules)
5. [Multi-Document Namespace](#5-multi-document-namespace)
6. [Query & Routing](#6-query--routing)
7. [Backlink Protocol](#7-backlink-protocol)
8. [Version Control](#8-version-control)
9. [Indexing Prompt (V3)](#9-indexing-prompt-v3)
10. [Global Registry](#10-global-registry)
11. [MCP Interface](#11-mcp-interface)
12. [Configuration](#12-configuration)

---

## 1. Overview

### What is Sigil?

Sigil is an open knowledge indexing engine that converts unstructured documents into **symbolic address indexes** — a deterministic, token-efficient, and auditable alternative to vector-based RAG retrieval.

### The Problem with RAG

```
Traditional RAG:
  Query → Embedding → Cosine similarity → Top-k chunks → LLM generates answer
  Problem: Probabilistic, expensive, non-auditable, chunk boundary artifacts

Sigil:
  Query → Symbol lookup → Exact address → Precise content fragment
  Result: Deterministic, token-efficient, fully auditable
```

### Key Properties

| Property | RAG | Sigil |
|----------|-----|-------|
| Retrieval mechanism | Vector similarity | Symbolic address lookup |
| Result type | Probabilistic | Deterministic |
| Token cost per query | High (full chunks) | Low (targeted fragments) |
| Auditability | Black box | Full path trace |
| Cross-document linking | Implicit | Explicit backlinks |
| LLM dependency | Embedding model required | Any LLM for indexing only |
| Structured doc performance | Poor | Excellent |

### Design Principles

1. **Symbol over vector** — a precise address is always better than a similarity score
2. **Address over chunk** — return the exact location, not an approximate neighborhood
3. **Any LLM** — indexing uses any configurable LLM; no embedding model required
4. **Any AI product** — expose knowledge via MCP; plugs into any AI system
5. **Human-readable** — every address is interpretable without tooling
6. **Self-auditing** — every index includes a quality check block

---

## 2. Core Concept

### The Knowledge Node

Every indexed fragment of a document becomes a **Knowledge Node**:

```yaml
knowledge_node:
  address: "ai.definition.mccarthy.what"
  location:
    structural: "§2.s2"
    anchor: "制造智能机器的科学与工程"
  content_summary: "约翰·麦卡锡1955年对AI的定义"
  source:
    doc_id: "DOC-2024-001"
    doc_version: "1.0"
  backlinks: []
  confidence: 1.0
  created_at: "2024-01-01T00:00:00Z"
```

### The Skill Card

Every document generates one **Skill Card** — a structured declaration of what the document can answer:

```yaml
skill_card:
  purpose: "一句话说明这份文档能回答什么问题"
  strengths:
    - "最适合的查询类型 1"
    - "最适合的查询类型 2"
    - "最适合的查询类型 3"
  weaknesses:
    - "不适合的查询类型 1"
    - "不适合的查询类型 2"
```

---

## 3. Symbolic Address Format

### Structure

```
[domain].[subdomain].[concept].[dimension]
```

All addresses are **exactly 3 or 4 levels deep**. No exceptions.

### Level Definitions

```
Level 1 — domain
  The top-level subject area of the document.
  Examples: ai, agent, equipment, medicine, law, finance

Level 2 — subdomain
  The thematic category within the domain.
  Must be selected from the Global Registry (Section 10).
  Examples: definition, architecture, workflow, capability, method

Level 3 — concept
  The specific concept, entity, or named element.
  Rules:
    - Lowercase only
    - Use underscores for compound terms: weak_ai, job_replacement
    - People: use surname in lowercase: mccarthy, kaplan
    - No abbreviations: natural_language_processing not nlp

Level 4 — dimension (mandatory)
  Must be exactly one of the following seven values:

  .what      → definition, description, identity
  .why       → cause, reason, background
  .how       → method, process, steps
  .symptom   → observable sign, phenomenon
  .effect    → outcome, consequence, impact
  .limit     → boundary, constraint, failure mode
  .ref       → citation, source, attribution
```

### Valid Examples

```
ai.definition.mccarthy.what
agent.architecture.cognitive.how
equipment.pump.fault.seal_leak.symptom
medicine.diagnosis.diabetes.effect
law.contract.termination.how
```

### Invalid Examples

```
ai.definition.what                     ✗  Only 3 levels — concept missing
ai.definition.mccarthy.academic.what   ✗  5 levels — too deep
agent.arch.cog.how                     ✗  Abbreviations not allowed
ai.definition.mccarthy.description     ✗  Dimension not in allowed set
AI.Definition.McCarthy.What            ✗  Must be lowercase
```

---

## 4. Indexing Rules

### Rule 1 — Dual-Anchor Location System

Every address must specify location using **both** a structural position and an anchor phrase.

```
Format:
  address → [structural_position | anchor:"phrase"]

Structural position by document type:
  Numbered sections  → §3.2.s1         (section 3.2, sentence 1)
  Unnumbered prose   → §2.s3           (paragraph 2, sentence 3)
  List items         → §2.list.3       (paragraph 2, list item 3)
  Table cells        → §3.table.2.1    (paragraph 3, row 2, col 1)

Anchor phrase rules:
  - Extract 7–15 characters from the original text
  - Must be unique within the document
  - Must be from the beginning or most distinctive part of the target sentence
  - Wrap in double quotes
  - FORBIDDEN: generic openers like "此外", "因此", "In addition", "However"

Example:
  ai.definition.mccarthy.what → [§2.s2 | anchor:"制造智能机器的科学与工程"]
  agent.architecture.cognitive.how → [§2.1.list.2 | anchor:"Integrates safety sandboxes"]
```

### Rule 2 — Naming Consistency

```
Within a single document:
  - All nodes of the same category must use the same Level 2 word
  - Synonyms are forbidden: if you use "component", never use "element", "part", or "module"
  - One document = one vocabulary

Cross-document:
  - Level 2 words must match the Global Registry definition
  - New Level 2 words require a registry proposal (see Section 10)
```

### Rule 3 — Mandatory Dimension Splitting

A single address must represent a single dimension. Multi-dimension content must be split.

```
WRONG:
  ai.capability.current.what → [§4] "Current AI capabilities include weak AI results,
                                     outperforming humans in image recognition,
                                     while AGI remains a distant goal"

CORRECT:
  ai.capability.weak.what    → [§4.s1 | anchor:"弱人工智能已有初步"]
  ai.capability.weak.effect  → [§4.s2 | anchor:"影像识别、语言分析、棋"]
  ai.capability.agi.limit    → [§4.s3 | anchor:"具备思考能力的统合强"]
```

### Rule 4 — Mandatory Self-Audit Block

Every indexing run must end with a quality check:

```
【Index Audit】
Total addresses generated:
Uncovered important concepts (if any):
Naming conflicts detected (if any):
Ambiguity warnings (if any):
```

### Rule 5 — List and Enumeration Coverage

All items in a list or enumeration must be indexed individually. List items must not be collapsed into a single address.

### Rule 6 — Document Registration

Before indexing, every document must declare:

```yaml
document_registration:
  domain: "agent"
  subdomain_claims:           # Exclusive — no other doc in this workspace may use these combinations
    - architecture
    - workflow
    - challenge
  subdomain_shared:           # Shared — multiple docs may index under these
    - metric
    - validation
  new_subdomain_proposals:    # Subdomains not in Global Registry — requires justification
    - name: "rag_validation"
      justification: "Distinct from generic validation; specific to retrieval system testing"
```

---

## 5. Multi-Document Namespace

### The Core Problem

When two documents generate addresses with identical paths, the system must decide: conflict, coexist, or merge.

### Resolution Priority

**Priority 1 — Different Level 3 or Level 4: Coexist**

```
doc_a: agent.validation.workflow.how   ← different concept
doc_b: agent.validation.rag.how        ← different concept
Result: Both exist. Query returns both with source labels.
```

**Priority 2 — Identical path, complementary content: Merge into Joint Node**

```
doc_a: agent.metric.retrieval_accuracy.what → definition
doc_b: agent.metric.retrieval_accuracy.what → empirical data (92%)

Merged node:
  agent.metric.retrieval_accuracy.what:
    sources:
      - DOC-2024-001 §3.1 | "definition of retrieval accuracy"
      - DOC-2024-002 §4.2 | "RAG system retrieved 92% of relevant"
```

**Priority 3 — Identical path, contradictory content: Conflict Flag**

```
doc_a: agent.standard.api.what → "RESTful APIs with OAuth 2.0"
doc_b: agent.standard.api.what → "GraphQL APIs with JWT"

Result:
  agent.standard.api.what:
    status: ⚠ CONFLICT
    sources:
      - DOC-2024-001: "RESTful APIs with OAuth 2.0"
      - DOC-2024-003: "GraphQL APIs with JWT"
    resolution: PENDING_HUMAN_REVIEW
```

### Document Identity Card

```yaml
document:
  id: "DOC-2024-001"             # Auto-generated. Format: DOC-YYYY-NNN
  title: "AI Agent Integration Technical Overview"
  domain: "agent"
  subdomain_claims:
    - architecture
    - workflow
    - challenge
  subdomain_shared:
    - metric
    - validation
  language: "en"
  version: "1.0"
  version_hash: "sha256:abc123..."
  created_at: "2024-01-01T00:00:00Z"
  updated_at: "2024-01-01T00:00:00Z"
```

---

## 6. Query & Routing

### Three-Tier Query Router

```
Incoming query
  │
  ▼
Tier 1: Exact address match
  → Hit: return node + location + anchor
  → Miss: proceed to Tier 2
  │
  ▼
Tier 2: Prefix match (partial address)
  → Hit: apply Route Table, return default node or expanded set
  → Miss: proceed to Tier 3
  │
  ▼
Tier 3: Keyword match against anchor phrases
  → Hit: return candidates with confidence scores
  → Miss: return empty + suggest related addresses
```

### Route Table

When a Level 2 prefix has 3 or more children, a Route Table entry is required:

```
[ROUTE: ai.definition]   → default: .general.what  | academic query: expand all .ref nodes
[ROUTE: ai.capability]   → default: .weak.what     | goal query: redirect to .agi.what
[ROUTE: agent.workflow]  → default: return all in step order
[ROUTE: agent.challenge] → default: return all .symptom nodes first, then .how
```

### Query Response Format

```yaml
query: "ai.definition.mccarthy.what"
result:
  address: "ai.definition.mccarthy.what"
  location: "§2.s2"
  anchor: "制造智能机器的科学与工程"
  content: "约翰·麦卡锡于1955年对人工智能的定义是"制造智能机器的科学与工程""
  source:
    doc_id: "DOC-2024-001"
    doc_title: "人工智能 Wikipedia"
    doc_version: "1.0"
  backlinks:
    - address: "ai.component.learning.what"
      relation: "domain_sibling"
      confidence: "HIGH"
  tokens_used: 47       # content fragment only, not full chunk
```

---

## 7. Backlink Protocol

### Backlink Types

```
INTERNAL  — Both nodes are in the same document
EXTERNAL  — Nodes are in different documents (cross-document link)
```

### Confidence Levels

```
HIGH    — Source document explicitly names the target topic
MEDIUM  — Source content is strongly related to target but does not name it directly
LOW     — Peripheral conceptual overlap; requires human confirmation before use
```

### Backlink Format

```yaml
backlink:
  from: "agent.architecture.cognitive.what"
  to: "ai.component.learning.what"
  type: "EXTERNAL"
  confidence: "HIGH"
  reason: "Entity overlap: 'LLMs', 'reasoning engines'"
  source_doc: "DOC-2024-001"
  target_doc: "DOC-2024-002"
```

### Bidirectional Auto-Registration

When Document A creates a backlink to Document B, the system automatically writes the reverse backlink into Document B's index. No manual maintenance required.

---

## 8. Version Control

### Address Versioning

Addresses are never deleted. Updated documents create versioned nodes:

```
agent.architecture.perception.what @v1.0
  → [§2.1.list.1 | anchor:"Collects structured and unstructured"] DOC-2024-001

agent.architecture.perception.what @v2.0
  → [§2.1.list.1 | anchor:"Perceives multimodal sensor streams"] DOC-2024-001-v2
```

### Query Behavior

```
Default query  → returns latest version
Pinned query   → agent.architecture.perception.what?version=1.0
History query  → agent.architecture.perception.what?history=all
```

### Version Hash

Every document version is identified by a SHA-256 hash of its content. When the hash changes, a new version node is created automatically.

---

## 9. Indexing Prompt (V3)

This is the canonical prompt used to generate Sigil-compliant symbolic address indexes from any document. It may be used with any LLM that supports instruction following.

```
You are a Sigil indexing engine. Convert the following document into a
symbolic address index compliant with the Sigil Specification v1.0.

═══ RULE 1: ADDRESS FORMAT ═══
Dot-notation hierarchy, fixed 3–4 levels:
  Level 1: domain        (e.g. ai / agent / equipment / medicine)
  Level 2: subdomain     (must exist in Global Registry)
  Level 3: concept       (lowercase, underscores, no abbreviations)
  Level 4: dimension     (exactly one of: .what .why .how .symptom .effect .limit .ref)

═══ RULE 2: DUAL-ANCHOR LOCATION ═══
Every address must include both a structural position and an anchor phrase.
Format: address → [structural_position | anchor:"7–15 char unique phrase"]

Structural position formats:
  Numbered sections  → §3.2.s1
  Unnumbered prose   → §2.s3
  List items         → §2.list.3
  Table cells        → §3.table.2.1

Anchor phrase rules:
  - 7–15 characters from original text
  - Must be unique within the document
  - From the beginning or most distinctive part of the sentence
  - Forbidden: generic openers ("此外", "因此", "In addition", "However")

═══ RULE 3: NAMING CONSISTENCY ═══
  - Use the same Level 2 word for all nodes of the same category
  - No synonyms within a document
  - People: lowercase surname (mccarthy, kaplan)
  - Compound terms: underscores (weak_ai, job_replacement)
  - No abbreviations (natural_language_processing not nlp)

═══ RULE 4: MANDATORY DIMENSION SPLITTING ═══
If a paragraph contains multiple dimensions, split into separate addresses.
Never merge multiple dimensions into a single address.

WRONG:
  ai.capability.current.what → [§4] "describes current AI capability"

CORRECT:
  ai.capability.weak.what    → [§4.s1 | anchor:"..."]
  ai.capability.weak.effect  → [§4.s2 | anchor:"..."]
  ai.capability.agi.limit    → [§4.s3 | anchor:"..."]

═══ RULE 5: ROUTE TABLE ═══
When a Level 2 prefix has 3 or more child nodes, declare a route:
  [ROUTE: parent.address] → default: child_key | condition: behavior

═══ RULE 6: BACKLINK CONFIDENCE ═══
  HIGH   — document explicitly names the linked topic
  MEDIUM — content is strongly related but does not name it
  LOW    — peripheral overlap, requires human review

Format:
  address | linkable topic | confidence level

═══ RULE 7: DOCUMENT REGISTRATION ═══
Output document registration before the index:

【Document Registration】
domain:
subdomain_claims (exclusive, comma-separated):
subdomain_shared (shared, comma-separated):
new subdomain proposals (if any, with justification):

═══ OUTPUT FORMAT (in this exact order) ═══

【Skill Card】
Purpose: (one sentence — what questions does this document answer?)
Strengths: (up to 3 query types this document handles well)
Weaknesses: (up to 2 query types this document handles poorly)

【Document Registration】
(see Rule 7)

【Symbolic Address Index】
address → [structural_position | anchor:"phrase"]

【Route Table】
[ROUTE: parent] → default: key | condition: behavior

【Backlink Candidates】
address | linkable topic | confidence

【Index Audit】
Total addresses:
Uncovered important concepts (if any):
Naming conflicts (if any):
Ambiguity warnings (if any):

═══ DOCUMENT CONTENT ═══
[paste document here]
```

---

## 10. Global Registry

### Level 1 — Domain Registry (globally unique)

| Domain | Scope |
|--------|-------|
| `ai` | Artificial intelligence general concepts |
| `agent` | AI agent architecture and implementation |
| `equipment` | Physical equipment and hardware |
| `medicine` | Medical and health sciences |
| `law` | Legal and regulatory content |
| `finance` | Financial and economic content |
| `science` | Natural sciences and research |
| `engineering` | Engineering principles and practice |

### Level 2 — Subdomain Registry (shared definitions)

| Subdomain | Canonical meaning |
|-----------|-------------------|
| `definition` | Concept definitions and descriptions |
| `architecture` | System structure and component design |
| `workflow` | Sequential processes and procedures |
| `component` | Constituent parts of a system |
| `capability` | Performance characteristics and limits |
| `method` | Techniques and approaches |
| `metric` | Quantitative measures and KPIs |
| `validation` | Testing, verification, and evaluation |
| `challenge` | Problems, obstacles, and failure modes |
| `standard` | Specifications and compliance requirements |
| `case_study` | Real-world examples and deployments |
| `future` | Emerging trends and forward-looking content |
| `societal_impact` | Effects on society, economy, or people |
| `research` | Academic and investigative content |
| `application` | Practical use cases and tools |

### Proposing New Entries

To propose a new domain or subdomain:

1. Open a GitHub issue with the label `registry-proposal`
2. Provide: proposed word, canonical definition, example addresses, justification for why existing entries do not cover the need
3. Community review period: 7 days
4. Merge requires approval from 2 maintainers

---

## 11. MCP Interface

Sigil exposes its index via the Model Context Protocol (MCP), allowing any MCP-compatible AI product to query it directly.

### Server Configuration

```yaml
# sigil.config.yaml — MCP server section
mcp:
  enabled: true
  port: 3000
  tools:
    - name: sigil_query
      description: "Query the Sigil symbolic address index"
    - name: sigil_list
      description: "List all addresses under a prefix"
    - name: sigil_backlinks
      description: "Get all backlinks for an address"
    - name: sigil_skill_cards
      description: "List all document Skill Cards in the index"
```

### Tool Definitions

**sigil_query**
```json
{
  "name": "sigil_query",
  "description": "Retrieve knowledge node(s) by symbolic address. Supports exact match, prefix match, and anchor search.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "address": { "type": "string", "description": "Full or partial symbolic address" },
      "version": { "type": "string", "description": "Optional version pin (e.g. '1.0')" },
      "expand_route": { "type": "boolean", "description": "If true, expand route table on prefix match" }
    },
    "required": ["address"]
  }
}
```

**sigil_list**
```json
{
  "name": "sigil_list",
  "description": "List all symbolic addresses under a given prefix.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "prefix": { "type": "string", "description": "Address prefix (e.g. 'ai.definition')" }
    },
    "required": ["prefix"]
  }
}
```

**sigil_backlinks**
```json
{
  "name": "sigil_backlinks",
  "description": "Get all backlinks pointing to or from a given address.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "address": { "type": "string" },
      "direction": { "type": "string", "enum": ["incoming", "outgoing", "both"], "default": "both" },
      "min_confidence": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"], "default": "MEDIUM" }
    },
    "required": ["address"]
  }
}
```

---

## 12. Configuration

### Full Configuration Reference

```yaml
# sigil.config.yaml

llm:
  provider: anthropic          # anthropic | openai | ollama | custom
  model: claude-sonnet-4-6     # any instruction-following model
  api_key: ${SIGIL_LLM_KEY}   # environment variable
  base_url: ~                  # optional: for local or proxy endpoints

indexing:
  key_depth_min: 3             # minimum address levels (do not set below 3)
  key_depth_max: 4             # maximum address levels (do not set above 4)
  language: auto               # auto | zh | en | ja | ...
  anchor_min_chars: 7
  anchor_max_chars: 15
  confidence_threshold: 0.8    # minimum confidence to include a backlink
  auto_backlink: true          # automatically register reverse backlinks

storage:
  backend: sqlite              # sqlite | postgres | neo4j
  path: ./sigil.db             # for sqlite
  connection_string: ~         # for postgres / neo4j

namespace:
  workspace_id: default        # logical namespace for multi-tenant use
  registry_path: ./registry/namespace.yaml

interface:
  mcp:
    enabled: true
    port: 3000
  rest_api:
    enabled: true
    port: 3001

logging:
  level: info
  audit_trail: true            # log all queries for auditability
```

---

## Appendix A — Worked Example

### Input Document (excerpt)

> 约翰·麦卡锡于1955年对人工智能的定义是"制造智能机器的科学与工程"。

### Generated Address

```
ai.definition.mccarthy.what → [§2.s2 | anchor:"制造智能机器的科学与工程"]
```

### Query

```
GET sigil_query(address="ai.definition.mccarthy.what")
```

### Response

```json
{
  "address": "ai.definition.mccarthy.what",
  "location": { "structural": "§2.s2", "anchor": "制造智能机器的科学与工程" },
  "content": "约翰·麦卡锡于1955年对人工智能的定义是"制造智能机器的科学与工程"",
  "source": { "doc_id": "DOC-2024-001", "version": "1.0" },
  "tokens_used": 42
}
```

### Token Comparison

```
RAG (same query):    ~1,800 tokens (full chunk retrieval)
Sigil (same query):     42 tokens (targeted fragment)
Reduction:           97.7%
```

---

## Appendix B — Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial specification |

---

*Sigil is an open specification. Contributions welcome via GitHub.*
*Every answer has an address.*
