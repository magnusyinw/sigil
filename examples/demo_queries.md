# Sigil Demo Queries

Example queries after indexing `pump_maintenance_sop.md`.

---

## CLI Queries

```bash
# Tier 1 — Exact address (deterministic, ~42 tokens)
sigil query "equipment.pump.fault.seal_leak.symptom"
sigil query "equipment.pump.fault.seal_leak.how"
sigil query "equipment.pump.maintenance.schedule.what"
sigil query "equipment.pump.safety.limit.limit"

# Tier 2 — Prefix (returns all children)
sigil query "equipment.pump.fault"
sigil query "equipment.pump"

# Tier 3 — Natural language (fuzzy search)
sigil query "vibration in the pump"
sigil query "pump overheating causes"
sigil query "when to replace seal"

# Browse the full index
sigil list
sigil list --prefix "equipment.pump.fault"

# Governance
sigil skill-cards
sigil conflicts
sigil stats
```

---

## REST API Queries

```bash
# Start the server first: sigil serve

# Tier 1
curl "http://localhost:3001/query?address=equipment.pump.fault.seal_leak.symptom"

# Tier 2
curl "http://localhost:3001/query?address=equipment.pump.fault"

# Tier 3 — natural language
curl "http://localhost:3001/query?address=pump%20vibration%20noise"

# List addresses
curl "http://localhost:3001/list"
curl "http://localhost:3001/list?prefix=equipment.pump"

# Skill Cards
curl "http://localhost:3001/skill-cards"

# Index a new document
curl -X POST "http://localhost:3001/index" \
  -F "file=@pump_maintenance_sop.md" \
  -F "title=Pump Maintenance SOP v3"

# Interactive API docs
open http://localhost:3001/docs
```

---

## MCP Integration (Claude Desktop)

Add to your Claude Desktop `config.json`:

```json
{
  "mcpServers": {
    "sigil": {
      "url": "http://localhost:3000/tools"
    }
  }
}
```

Then in Claude, you can ask:

> "What are the symptoms of a seal leak in a centrifugal pump?"
> Claude will call sigil_query("equipment.pump.fault.seal_leak.symptom")
> and return the exact evidence fragment with source citation.

---

## Python API

```python
import sys
sys.path.insert(0, "/path/to/sigil")

from core.config import load_config
from core.llm import LLMProvider
from core.indexer import SigilIndexer
from core.router import SigilRouter
from storage.db import SigilStorage

# Setup
cfg     = load_config()
storage = SigilStorage(cfg["storage"]["path"])
llm     = LLMProvider(cfg["llm"])
indexer = SigilIndexer(llm, storage)
router  = SigilRouter(storage)

# Index
result = indexer.index_file("./pump_maintenance_sop.md")
print(f"Indexed {result['nodes_indexed']} addresses")

# Query — Tier 1 (exact, deterministic)
result = router.query("equipment.pump.fault.seal_leak.symptom")
for node in result["results"]:
    print(f"Address : {node['address']}")
    print(f"Location: {node['structural_location']} | {node['anchor_phrase']}")
    print(f"Content : {node['content']}")
    print(f"Source  : {node['doc_title']} ({node['doc_id']})")

# Query — Tier 2 (prefix)
result = router.query("equipment.pump.fault")
print(f"Found {result['count']} nodes under equipment.pump.fault")

# List all addresses
result = router.list_addresses(prefix="equipment")
for addr in result["addresses"]:
    print(addr)
```
