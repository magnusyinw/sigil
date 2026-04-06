"""
Sigil Three-Tier Query Router

Tier 1 — Exact address match   → deterministic, zero LLM, microsecond latency
Tier 2 — Prefix match          → returns all children of an address prefix
Tier 3 — Anchor / text search  → fuzzy fallback, natural language input
"""

import re
from storage.db import SigilStorage


class SigilRouter:
    """
    Routes queries through three tiers from exact to fuzzy.

    Usage:
        router = SigilRouter(storage)
        result = router.query("equipment.pump.fault.seal_leak.symptom")
        result = router.query("equipment.pump")      # prefix → Tier 2
        result = router.query("vibration in pump")   # natural lang → Tier 3
    """

    _ADDRESS_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,3}$")
    _PREFIX_RE  = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){0,2}$")

    def __init__(self, storage: SigilStorage):
        self.storage      = storage
        self._last_address: str | None = None

    # ── Public API ────────────────────────────────────────────────────

    def query(self, query: str, session_id: str = "default") -> dict:
        """Route a query and return matched knowledge nodes."""
        q = query.strip()
        if not q:
            return self._empty(q)

        # Record transition for predictive layer
        if self._last_address and self._is_address(q):
            self.storage.record_transition(self._last_address, q)

        # Tier 1: exact address
        nodes = self.storage.query_exact(q)
        if nodes:
            self._last_address = q
            return self._result(1, "exact_match", q, nodes)

        # Tier 2: prefix
        if self._is_prefix(q):
            nodes = self.storage.query_prefix(q)
            if nodes:
                return self._result(2, "prefix_match", q, nodes)

        # Tier 3: anchor / content search
        nodes = self.storage.query_anchor(q, limit=5)
        note  = (
            "Results from anchor phrase and content search. "
            "Use 'sigil list' to find exact symbolic addresses for deterministic retrieval."
        )
        return self._result(3, "fuzzy_search", q, nodes, note=note)

    def list_addresses(self, prefix: str = "", limit: int = 200) -> dict:
        """List all indexed symbolic addresses, optionally filtered by prefix."""
        addresses = self.storage.list_addresses(prefix=prefix, limit=limit)
        return {"prefix": prefix or "(all)", "addresses": addresses, "count": len(addresses)}

    def get_backlinks(self, address: str) -> dict:
        """Return all nodes that link to the given address."""
        nodes = self.storage.get_backlinks(address)
        return {"address": address, "backlinks": nodes, "count": len(nodes)}

    def get_skill_cards(self) -> dict:
        """Return Skill Cards for all indexed documents."""
        cards = self.storage.get_skill_cards()
        return {"skill_cards": cards, "count": len(cards)}

    def get_conflicts(self) -> dict:
        """Return all pending conflict flags."""
        conflicts = self.storage.get_conflicts()
        return {"conflicts": conflicts, "count": len(conflicts)}

    def get_stats(self) -> dict:
        """Return index statistics."""
        return self.storage.get_stats()

    # ── Helpers ───────────────────────────────────────────────────────

    def _is_address(self, s: str) -> bool:
        return bool(self._ADDRESS_RE.match(s))

    def _is_prefix(self, s: str) -> bool:
        return bool(self._PREFIX_RE.match(s))

    @staticmethod
    def _result(tier: int, name: str, query: str, nodes: list,
                note: str | None = None) -> dict:
        r = {"tier": tier, "tier_name": name, "query": query,
             "results": nodes, "count": len(nodes)}
        if note:
            r["note"] = note
        return r

    @staticmethod
    def _empty(query: str) -> dict:
        return {"tier": 0, "tier_name": "empty", "query": query,
                "results": [], "count": 0}
