# Sigil Roadmap

> Every answer has an address.

---

## v1.0.0 — Specification Release ✓ Current

- [x] Symbolic address specification (SPEC.md)
- [x] V3 indexing prompt (LLM-agnostic)
- [x] Multi-document namespace rules
- [x] Backlink protocol
- [x] White paper (WHITEPAPER.md)
- [x] CLI: index, query, list, serve, init
- [x] SQLite storage backend
- [x] MCP server (tool discovery + execution)
- [x] REST API with interactive docs
- [x] PDF, DOCX, Markdown, TXT, HTML parsing
- [x] Three-tier query router
- [x] Conflict detection and flagging
- [x] Test suite (db, router, indexer)

---

## v1.1.0 — Stability

- [ ] PostgreSQL storage backend
- [ ] Index quality dashboard (web UI)
- [ ] Batch indexing (`sigil index ./docs/`)
- [ ] Re-index on file change detection
- [ ] Address validation linter
- [ ] `sigil export` — export index as JSON/CSV
- [ ] Improved CLI `--help` with examples

---

## v1.2.0 — Ecosystem

- [ ] Neo4j graph backend (for large corpora)
- [ ] Community registry (GitHub-based domain proposals)
- [ ] Domain templates:
  - `pharmaceutical/` — GMP, CAPA, deviation, SOP
  - `legal/` — contracts, clauses, regulations
  - `engineering/` — equipment, calibration, maintenance
  - `academic/` — papers, citations, methods
- [ ] `sigil validate` — check address format compliance
- [ ] Webhook trigger on document update

---

## v1.3.0 — Intelligence

- [ ] Predictive prefetching (transition matrix)
- [ ] Error-driven backlink discovery
- [ ] Usage-weighted route table auto-optimization
- [ ] Session context awareness
- [ ] `sigil predict` — show predicted next queries

---

## v2.0.0 — Scale

- [ ] Distributed index (multi-node)
- [ ] Real-time document sync
- [ ] Multimodal evidence nodes (images, tables, diagrams)
- [ ] Address-specialized fine-tuned indexing model
- [ ] Sigil Cloud (hosted service)
- [ ] Team workspaces with role-based access
- [ ] Audit trail export for compliance reporting

---

## Research Directions

- KV cache pre-population from Sigil indexes
- Retrieval head activation study with symbolic addresses
- Symbolic address fine-tuning dataset and model

---

## Contributing to the Roadmap

Open a GitHub issue with label `roadmap-proposal` to suggest features.
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
