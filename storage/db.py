"""
Sigil Storage Layer
SQLite-backed knowledge node store with conflict detection.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timezone

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
from typing import Optional

from core.models import KnowledgeNode, Document


class SigilStorage:
    """
    SQLite-backed storage for Sigil knowledge nodes and documents.

    Usage:
        storage = SigilStorage("./sigil.db")
        storage.save_node(node)
        nodes = storage.query_exact("equipment.pump.fault.seal_leak.symptom")
    """

    def __init__(self, db_path: str = "./sigil.db"):
        self.db_path = db_path
        self.conn    = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id           TEXT PRIMARY KEY,
                title            TEXT,
                filepath         TEXT,
                version_hash     TEXT,
                domain           TEXT,
                subdomain_claims TEXT,
                subdomain_shared TEXT,
                skill_card       TEXT,
                indexed_at       TEXT
            );

            CREATE TABLE IF NOT EXISTS knowledge_nodes (
                address              TEXT,
                structural_location  TEXT,
                anchor_phrase        TEXT,
                content              TEXT,
                doc_id               TEXT,
                doc_title            TEXT,
                doc_version          TEXT,
                backlinks            TEXT DEFAULT '[]',
                created_at           TEXT,
                PRIMARY KEY (address, doc_id)
            );

            CREATE TABLE IF NOT EXISTS transitions (
                from_address TEXT,
                to_address   TEXT,
                count        INTEGER DEFAULT 1,
                PRIMARY KEY (from_address, to_address)
            );

            CREATE TABLE IF NOT EXISTS conflict_flags (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                address    TEXT,
                doc_id_a   TEXT,
                doc_id_b   TEXT,
                content_a  TEXT,
                content_b  TEXT,
                flagged_at TEXT,
                status     TEXT DEFAULT 'PENDING_HUMAN_REVIEW'
            );

            CREATE INDEX IF NOT EXISTS idx_nodes_address
                ON knowledge_nodes(address);
            CREATE INDEX IF NOT EXISTS idx_nodes_doc
                ON knowledge_nodes(doc_id);
            CREATE INDEX IF NOT EXISTS idx_nodes_anchor
                ON knowledge_nodes(anchor_phrase);
        """)
        self.conn.commit()

    # ── Document CRUD ─────────────────────────────────────────────────

    def save_document(self, doc: Document):
        self.conn.execute(
            "INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?,?,?,?)",
            (
                doc.doc_id, doc.title, doc.filepath, doc.version_hash,
                doc.domain,
                json.dumps(doc.subdomain_claims, ensure_ascii=False),
                json.dumps(doc.subdomain_shared, ensure_ascii=False),
                json.dumps(doc.skill_card,       ensure_ascii=False),
                doc.indexed_at,
            ),
        )
        self.conn.commit()

    def get_all_documents(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM documents ORDER BY indexed_at DESC"
        ).fetchall()
        return [self._doc_row(r) for r in rows]

    def get_skill_cards(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT doc_id, title, skill_card FROM documents"
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["skill_card"] = json.loads(d["skill_card"])
            result.append(d)
        return result

    # ── Node CRUD ─────────────────────────────────────────────────────

    def save_node(self, node: KnowledgeNode):
        # Detect conflict with existing node from a different document
        existing = self.conn.execute(
            "SELECT * FROM knowledge_nodes WHERE address=? AND doc_id!=?",
            (node.address, node.doc_id),
        ).fetchone()

        if existing:
            self._check_conflict(node, dict(existing))

        self.conn.execute(
            "INSERT OR REPLACE INTO knowledge_nodes VALUES (?,?,?,?,?,?,?,?,?)",
            (
                node.address, node.structural_location, node.anchor_phrase,
                node.content, node.doc_id, node.doc_title, node.doc_version,
                json.dumps(node.backlinks, ensure_ascii=False),
                node.created_at,
            ),
        )
        self.conn.commit()

    def _check_conflict(self, new: KnowledgeNode, existing: dict):
        """Flag as conflict when content overlap is low (< 30%)."""
        a_words = set(existing["content"].lower().split())
        b_words = set(new.content.lower().split())
        union   = a_words | b_words
        if not union:
            return
        overlap = len(a_words & b_words) / len(union)
        if overlap < 0.3:
            self.conn.execute(
                """INSERT INTO conflict_flags
                   (address, doc_id_a, doc_id_b, content_a, content_b, flagged_at)
                   VALUES (?,?,?,?,?,?)""",
                (
                    new.address,
                    existing["doc_id"], new.doc_id,
                    existing["content"], new.content,
                    _now(),
                ),
            )

    # ── Query ─────────────────────────────────────────────────────────

    def query_exact(self, address: str) -> list[dict]:
        """Tier 1: exact address match — deterministic."""
        rows = self.conn.execute(
            "SELECT * FROM knowledge_nodes WHERE address=?", (address,)
        ).fetchall()
        return [self._node_row(r) for r in rows]

    def query_prefix(self, prefix: str, limit: int = 50) -> list[dict]:
        """Tier 2: prefix match — returns all children."""
        rows = self.conn.execute(
            "SELECT * FROM knowledge_nodes WHERE address LIKE ? ORDER BY address LIMIT ?",
            (f"{prefix}%", limit),
        ).fetchall()
        return [self._node_row(r) for r in rows]

    def query_anchor(self, text: str, limit: int = 5) -> list[dict]:
        """Tier 3: anchor phrase and content search."""
        rows = self.conn.execute(
            """SELECT * FROM knowledge_nodes
               WHERE anchor_phrase LIKE ? OR content LIKE ?
               LIMIT ?""",
            (f"%{text}%", f"%{text}%", limit),
        ).fetchall()
        return [self._node_row(r) for r in rows]

    def list_addresses(self, prefix: str = "", limit: int = 200) -> list[str]:
        if prefix:
            rows = self.conn.execute(
                "SELECT DISTINCT address FROM knowledge_nodes WHERE address LIKE ? ORDER BY address LIMIT ?",
                (f"{prefix}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT DISTINCT address FROM knowledge_nodes ORDER BY address LIMIT ?",
                (limit,),
            ).fetchall()
        return [r[0] for r in rows]

    def get_backlinks(self, address: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM knowledge_nodes WHERE backlinks LIKE ?",
            (f"%{address}%",),
        ).fetchall()
        return [self._node_row(r) for r in rows]

    def get_conflicts(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM conflict_flags WHERE status='PENDING_HUMAN_REVIEW' ORDER BY flagged_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        total_nodes = self.conn.execute(
            "SELECT COUNT(*) FROM knowledge_nodes"
        ).fetchone()[0]
        total_docs = self.conn.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]
        total_conflicts = self.conn.execute(
            "SELECT COUNT(*) FROM conflict_flags WHERE status='PENDING_HUMAN_REVIEW'"
        ).fetchone()[0]
        domains = self.conn.execute(
            "SELECT DISTINCT domain FROM documents"
        ).fetchall()
        return {
            "total_nodes":     total_nodes,
            "total_documents": total_docs,
            "pending_conflicts": total_conflicts,
            "domains":         [r[0] for r in domains],
            "db_path":         self.db_path,
        }

    # ── Predictive layer ──────────────────────────────────────────────

    def record_transition(self, from_addr: str, to_addr: str):
        self.conn.execute(
            """INSERT INTO transitions (from_address, to_address, count) VALUES (?,?,1)
               ON CONFLICT(from_address, to_address) DO UPDATE SET count = count + 1""",
            (from_addr, to_addr),
        )
        self.conn.commit()

    def get_top_transitions(self, from_addr: str, limit: int = 3) -> list[dict]:
        rows = self.conn.execute(
            """SELECT to_address, count FROM transitions
               WHERE from_address=? ORDER BY count DESC LIMIT ?""",
            (from_addr, limit),
        ).fetchall()
        return [{"to_address": r[0], "count": r[1]} for r in rows]

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def file_hash(filepath: str) -> str:
        try:
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                h.update(f.read())
            return h.hexdigest()[:16]
        except Exception:
            return "unknown"

    @staticmethod
    def _node_row(row) -> dict:
        d = dict(row)
        if "backlinks" in d:
            d["backlinks"] = json.loads(d["backlinks"])
        return d

    @staticmethod
    def _doc_row(row) -> dict:
        d = dict(row)
        for key in ("subdomain_claims", "subdomain_shared", "skill_card"):
            if key in d:
                d[key] = json.loads(d[key])
        return d

    def close(self):
        self.conn.close()

    def __repr__(self) -> str:
        return f"SigilStorage(db={self.db_path!r})"
