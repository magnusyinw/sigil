"""
Sigil Core Indexer
Converts documents into symbolic address indexes using the V3 indexing prompt.
Works with any configured LLM provider.
"""

import re
import json
import uuid
from pathlib import Path
from typing import Optional

from core.llm import LLMProvider
from core.parser import parse_document
from core.models import KnowledgeNode, Document
from storage.db import SigilStorage


# ── V3 Indexing Prompt ────────────────────────────────────────────────────────

_SYSTEM = """You are the Sigil indexing engine. Convert documents into symbolic
address indexes following the Sigil Specification v1.0.
Output ONLY valid JSON — no markdown fences, no explanation, no preamble."""

_PROMPT = """Convert the following document into a Sigil symbolic address index.

═══ RULE 1: ADDRESS FORMAT ═══
Dot-notation, fixed 3–4 levels:
  Level 1: domain     (ai / agent / equipment / medicine / law / finance / engineering)
  Level 2: subdomain  (definition / architecture / workflow / capability / method /
                       metric / challenge / standard / fault / maintenance / deviation / capa)
  Level 3: concept    (lowercase, underscores for compounds, no abbreviations)
  Level 4: dimension  (ONE of: .what  .why  .how  .symptom  .effect  .limit  .ref)

═══ RULE 2: DUAL-ANCHOR LOCATION ═══
Every address must have BOTH structural position AND anchor phrase.
Format:  address → [§pos | anchor:"7-15 char unique phrase"]

Position formats:
  §2.s3       = paragraph 2, sentence 3
  §3.list.2   = paragraph 3, list item 2
  §4.table.1  = paragraph 4, table item 1

Anchor rules:
  - 7–15 characters extracted verbatim from original text
  - Must uniquely identify this sentence in the document
  - NEVER use generic phrases: "In addition", "Furthermore", "However", "此外", "因此"

═══ RULE 3: NAMING CONSISTENCY ═══
  - Same Level 2 word for all nodes of the same category — no synonyms
  - Persons: lowercase surname only (mccarthy, kaplan)
  - Compounds: underscores (seal_leak, job_replacement, weak_ai)
  - No abbreviations (natural_language_processing not nlp)

═══ RULE 4: SPLIT MULTI-DIMENSION PARAGRAPHS ═══
One address = one dimension. NEVER merge multiple dimensions.

WRONG:  equipment.pump.fault.seal_leak.what → "symptoms include vibration and also how to fix it"
RIGHT:
  equipment.pump.fault.seal_leak.symptom → [§3.1.s1 | anchor:"vibration at shaft coupling"]
  equipment.pump.fault.seal_leak.how     → [§3.1.s3 | anchor:"replace mechanical seal per"]

═══ RULE 5: ROUTE TABLE ═══
Declare a route when a Level 2 prefix has 3+ children:
  [ROUTE: domain.subdomain] → default: child | condition: when to expand

═══ RULE 6: BACKLINK CONFIDENCE ═══
  HIGH   = document explicitly names the target topic
  MEDIUM = content strongly related but does not name it
  LOW    = peripheral overlap, needs human confirmation

═══ OUTPUT: STRICT JSON ONLY ═══
{
  "skill_card": {
    "purpose": "one sentence — what questions does this document answer?",
    "strengths": ["type 1", "type 2", "type 3"],
    "weaknesses": ["type 1", "type 2"]
  },
  "registration": {
    "domain": "primary domain word",
    "subdomain_claims": ["exclusive subdomain 1"],
    "subdomain_shared": ["shared subdomain 1"],
    "new_proposals": []
  },
  "nodes": [
    {
      "address": "domain.subdomain.concept.dimension",
      "structural_location": "§2.s3",
      "anchor_phrase": "unique phrase from original",
      "content_summary": "one sentence of what this fragment says"
    }
  ],
  "route_table": [
    {
      "prefix": "domain.subdomain",
      "default": "domain.subdomain.concept.dimension",
      "condition": "when and how to expand"
    }
  ],
  "backlink_candidates": [
    {
      "from_address": "domain.subdomain.concept.dimension",
      "to_topic": "name of external topic to link",
      "confidence": "HIGH"
    }
  ],
  "audit": {
    "total_nodes": 0,
    "uncovered_concepts": ["concept that was not indexed"],
    "naming_conflicts": [],
    "ambiguity_warnings": ["address X and Y may be semantically overlapping"]
  }
}

═══ DOCUMENT ═══
{document_text}"""


# ── Indexer ───────────────────────────────────────────────────────────────────

class SigilIndexer:
    """
    Converts documents into symbolic address indexes.

    Usage:
        indexer = SigilIndexer(llm, storage)
        result  = indexer.index_file("./my-doc.pdf")
    """

    def __init__(self, llm: LLMProvider, storage: SigilStorage):
        self.llm     = llm
        self.storage = storage

    # ── Public API ────────────────────────────────────────────────────

    def index_file(self, filepath: str, title: Optional[str] = None) -> dict:
        """Index a document file. Supports PDF, DOCX, MD, TXT, HTML."""
        text = parse_document(filepath)
        if not title:
            title = Path(filepath).stem.replace("_", " ").replace("-", " ").title()
        return self._index(text, filepath=filepath, title=title)

    def index_text(self, text: str, title: str = "Inline Document") -> dict:
        """Index raw text content directly."""
        return self._index(text, filepath="inline", title=title)

    # ── Internal ──────────────────────────────────────────────────────

    def _index(self, text: str, filepath: str, title: str) -> dict:
        max_chars = 12000
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n[Truncated at {max_chars} characters]"

        prompt     = _PROMPT.replace("{document_text}", text)
        raw        = self.llm.complete(prompt, system=_SYSTEM)
        index_data = self._parse_json(raw)

        doc_id       = str(uuid.uuid4())[:8]
        version_hash = SigilStorage.file_hash(filepath) if filepath != "inline" else doc_id

        doc = Document(
            doc_id           = doc_id,
            title            = title,
            filepath         = filepath,
            version_hash     = version_hash,
            domain           = index_data["registration"].get("domain", "unknown"),
            subdomain_claims = index_data["registration"].get("subdomain_claims", []),
            subdomain_shared = index_data["registration"].get("subdomain_shared", []),
            skill_card       = index_data["skill_card"],
        )
        self.storage.save_document(doc)

        saved = 0
        for n in index_data.get("nodes", []):
            node = KnowledgeNode(
                address              = n["address"],
                structural_location  = n.get("structural_location", ""),
                anchor_phrase        = n.get("anchor_phrase", ""),
                content              = n.get("content_summary", ""),
                doc_id               = doc_id,
                doc_title            = title,
                doc_version          = version_hash,
            )
            self.storage.save_node(node)
            saved += 1

        return {
            "doc_id":              doc_id,
            "title":               title,
            "nodes_indexed":       saved,
            "domain":              doc.domain,
            "skill_card":          doc.skill_card,
            "route_table":         index_data.get("route_table", []),
            "backlink_candidates": index_data.get("backlink_candidates", []),
            "audit":               index_data.get("audit", {}),
        }

    def _parse_json(self, raw: str) -> dict:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass

        # Fallback: empty but valid structure
        return {
            "skill_card":   {"purpose": "Parse error", "strengths": [], "weaknesses": []},
            "registration": {"domain": "unknown", "subdomain_claims": [], "subdomain_shared": [], "new_proposals": []},
            "nodes":        [],
            "route_table":  [],
            "backlink_candidates": [],
            "audit": {"total_nodes": 0, "uncovered_concepts": [], "naming_conflicts": ["JSON parse failed"], "ambiguity_warnings": []},
        }
