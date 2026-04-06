# Changelog

All notable changes to Sigil are documented here.
Format: [Semantic Versioning](https://semver.org)

---

## [1.0.0] — 2025

### Added

**Core**
- Symbolic address indexing engine with V3 LLM prompt
- Three-tier query router (exact / prefix / fuzzy)
- Dual-anchor localization system (structural + anchor phrase)
- Conflict detection between nodes from different documents
- Transition tracking for predictive layer foundation

**Storage**
- SQLite storage backend
- Knowledge node CRUD with conflict detection
- Document registry with Skill Card storage
- Query log and transition matrix tables

**LLM Support**
- Anthropic Claude (all models)
- OpenAI GPT (all models)
- Ollama (local models, offline use)
- Any OpenAI-compatible API endpoint

**Document Parsing**
- PDF via pdfplumber
- DOCX via python-docx
- Markdown, TXT, HTML

**Interfaces**
- CLI: init, index, query, list, serve, skill-cards, conflicts, stats
- MCP server (tool discovery + execution, SSE endpoint)
- REST API with interactive Swagger docs
- Python API

**Specification**
- SPEC.md v1.0 — complete open protocol
- WHITEPAPER.md v2.0 — theoretical foundation
- Global domain and subdomain registry

**Tests**
- test_db.py — storage layer
- test_router.py — three-tier routing
- test_indexer.py — indexing with mock LLM

---

## [Unreleased]

See [ROADMAP.md](ROADMAP.md) for planned features.
