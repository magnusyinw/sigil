# Contributing to Sigil

Thank you for your interest in Sigil. Contributions are welcome across four areas.

---

## Ways to Contribute

### 1. Core Engine

Bug fixes, performance improvements, new storage backends, parser improvements.

```bash
git clone https://github.com/sigil-index/sigil.git
cd sigil
pip install -r requirements.txt
pip install pytest

# Run tests
pytest tests/ -v

# Run a specific test
pytest tests/test_router.py -v
```

### 2. Registry Proposals

Propose new domains or subdomains to the Global Registry.

Open a GitHub issue with label `registry-proposal` and include:
- Proposed word (lowercase, no hyphens)
- Canonical definition (one sentence)
- 3 example addresses that use it
- Why existing registry entries don't cover this need

Review period: 7 days. Merge requires 2 maintainer approvals.

### 3. Domain Templates

Pre-built indexing configurations for specific industries.

Create a folder under `templates/` with:
- `README.md` — what this template covers
- `config.yaml` — domain-specific indexing settings
- `examples/` — 2-3 sample documents with expected index output

Good first templates: pharmaceutical GMP, legal contracts, engineering manuals.

### 4. Examples and Documentation

Real-world indexing cases, tutorials, and translations of documentation.

---

## Pull Request Guidelines

- One PR per feature or fix
- Include tests for new functionality
- Update relevant documentation
- Follow existing code style (no linter yet, use common sense)
- Write clear commit messages: `feat: add postgres backend` / `fix: handle empty anchor phrases`

---

## Code of Conduct

Be direct, be respectful, focus on the work. No harassment, no gatekeeping.

---

## Questions

Open a GitHub Discussion. Issues are for bugs and feature requests only.
