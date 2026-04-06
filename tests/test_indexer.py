"""
Tests for SigilIndexer.
Uses a mock LLM to test parsing and storage without real API calls.
"""

import pytest
import json
from unittest.mock import MagicMock

from core.indexer import SigilIndexer
from storage.db import SigilStorage


MOCK_INDEX_RESPONSE = json.dumps({
    "skill_card": {
        "purpose": "Explains centrifugal pump fault diagnosis and maintenance.",
        "strengths": ["Fault symptom queries", "Corrective action queries"],
        "weaknesses": ["General hydraulics theory"]
    },
    "registration": {
        "domain": "equipment",
        "subdomain_claims": ["fault", "maintenance"],
        "subdomain_shared": ["standard"],
        "new_proposals": []
    },
    "nodes": [
        {
            "address": "equipment.pump.fault.seal_leak.symptom",
            "structural_location": "§3.1.s1",
            "anchor_phrase": "vibration at shaft coupling",
            "content_summary": "Visible liquid dripping, increased vibration at shaft coupling."
        },
        {
            "address": "equipment.pump.fault.seal_leak.how",
            "structural_location": "§3.1.s3",
            "anchor_phrase": "replace mechanical seal per",
            "content_summary": "Stop pump, replace mechanical seal per Drawing PM-021."
        },
        {
            "address": "equipment.pump.maintenance.schedule.what",
            "structural_location": "§4.table.1",
            "anchor_phrase": "Weekly   Visual inspection",
            "content_summary": "Weekly visual inspection for leaks and vibration."
        }
    ],
    "route_table": [
        {
            "prefix": "equipment.pump.fault",
            "default": "equipment.pump.fault.seal_leak.symptom",
            "condition": "expand all when diagnosing faults"
        }
    ],
    "backlink_candidates": [
        {
            "from_address": "equipment.pump.fault.seal_leak.symptom",
            "to_topic": "GMP deviation reporting requirements",
            "confidence": "MEDIUM"
        }
    ],
    "audit": {
        "total_nodes": 3,
        "uncovered_concepts": [],
        "naming_conflicts": [],
        "ambiguity_warnings": []
    }
})


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.complete.return_value = MOCK_INDEX_RESPONSE
    return llm


@pytest.fixture
def indexer(tmp_path, mock_llm):
    storage = SigilStorage(str(tmp_path / "test.db"))
    idx = SigilIndexer(mock_llm, storage)
    yield idx, storage
    storage.close()


class TestSigilIndexer:

    def test_index_text_returns_result(self, indexer):
        idx, storage = indexer
        result = idx.index_text("Test document content", title="Test Doc")
        assert result["nodes_indexed"] == 3
        assert result["domain"] == "equipment"
        assert result["title"] == "Test Doc"
        assert "doc_id" in result

    def test_indexed_nodes_stored(self, indexer):
        idx, storage = indexer
        result = idx.index_text("Test content", title="Test Doc")
        nodes = storage.query_exact("equipment.pump.fault.seal_leak.symptom")
        assert len(nodes) == 1
        assert nodes[0]["anchor_phrase"] == "vibration at shaft coupling"

    def test_skill_card_stored(self, indexer):
        idx, storage = indexer
        result = idx.index_text("Test content", title="Test Doc")
        cards = storage.get_skill_cards()
        assert len(cards) == 1
        assert "Fault symptom queries" in cards[0]["skill_card"]["strengths"]

    def test_index_file_md(self, indexer, tmp_path):
        idx, storage = indexer
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nThis is a test document.")
        result = idx.index_file(str(md_file))
        assert result["nodes_indexed"] == 3

    def test_document_registered(self, indexer):
        idx, storage = indexer
        result = idx.index_text("Content", title="My Doc")
        docs = storage.get_all_documents()
        assert len(docs) == 1
        assert docs[0]["domain"] == "equipment"
        assert "fault" in docs[0]["subdomain_claims"]

    def test_malformed_json_fallback(self, indexer, mock_llm):
        idx, storage = indexer
        mock_llm.complete.return_value = "This is not JSON at all."
        result = idx.index_text("Content", title="Bad Response")
        # Should not crash, returns empty node list
        assert result["nodes_indexed"] == 0

    def test_json_with_markdown_fences(self, indexer, mock_llm):
        idx, storage = indexer
        mock_llm.complete.return_value = f"```json\n{MOCK_INDEX_RESPONSE}\n```"
        result = idx.index_text("Content", title="Fenced JSON")
        assert result["nodes_indexed"] == 3
