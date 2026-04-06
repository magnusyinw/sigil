"""
Sigil Data Models
Shared dataclasses used across all modules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class KnowledgeNode:
    """A single indexed knowledge fragment with its symbolic address."""
    address: str                    # e.g. equipment.pump.fault.seal_leak.symptom
    structural_location: str        # e.g. §3.1.s1
    anchor_phrase: str              # e.g. "vibration at shaft coupling"
    content: str                    # the actual text fragment
    doc_id: str
    doc_title: str
    doc_version: str
    backlinks: list = field(default_factory=list)
    created_at: str = field(default_factory=_now)


@dataclass
class Document:
    """Metadata for an indexed document."""
    doc_id: str
    title: str
    filepath: str
    version_hash: str
    domain: str
    subdomain_claims: list
    subdomain_shared: list
    skill_card: dict
    indexed_at: str = field(default_factory=_now)


@dataclass
class SkillCard:
    """What a document can and cannot answer."""
    purpose: str
    strengths: list
    weaknesses: list


@dataclass
class QueryResult:
    """Result from a Sigil query."""
    tier: int                       # 1=exact, 2=prefix, 3=fuzzy
    tier_name: str
    query: str
    results: list
    count: int
    note: Optional[str] = None


@dataclass
class ConflictFlag:
    """Two nodes at the same address with contradictory content."""
    address: str
    doc_id_a: str
    doc_id_b: str
    content_a: str
    content_b: str
    flagged_at: str
    status: str = "PENDING_HUMAN_REVIEW"


# Valid dimension suffixes — enforced by the indexing prompt
VALID_DIMENSIONS = {".what", ".why", ".how", ".symptom", ".effect", ".limit", ".ref"}

# Global domain registry
DOMAIN_REGISTRY = {
    "ai":          "Artificial intelligence general concepts",
    "agent":       "AI agent architecture and implementation",
    "equipment":   "Physical equipment and hardware systems",
    "medicine":    "Medical and health sciences",
    "law":         "Legal and regulatory content",
    "finance":     "Financial and economic content",
    "science":     "Natural sciences and research",
    "engineering": "Engineering principles and practice",
}

# Global subdomain registry
SUBDOMAIN_REGISTRY = {
    "definition":      "Concept definitions and descriptions",
    "architecture":    "System structure and component design",
    "workflow":        "Sequential processes and procedures",
    "component":       "Constituent parts of a system",
    "capability":      "Performance characteristics and limits",
    "method":          "Techniques and approaches",
    "metric":          "Quantitative measures and KPIs",
    "validation":      "Testing, verification, and evaluation",
    "challenge":       "Problems, obstacles, and failure modes",
    "standard":        "Specifications and compliance requirements",
    "case_study":      "Real-world examples and deployments",
    "future":          "Emerging trends and forward-looking content",
    "societal_impact": "Effects on society, economy, or people",
    "research":        "Academic and investigative content",
    "application":     "Practical use cases and tools",
    "fault":           "Equipment fault diagnosis and symptoms",
    "maintenance":     "Maintenance procedures and schedules",
    "deviation":       "Process deviations and non-conformances",
    "capa":            "Corrective and preventive actions",
}
