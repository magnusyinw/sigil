"""Tests for SigilStorage."""

import os
import pytest
from core.models import KnowledgeNode, Document
from storage.db import SigilStorage


@pytest.fixture
def db(tmp_path):
    storage = SigilStorage(str(tmp_path / "test.db"))
    yield storage
    storage.close()


def _node(address="equipment.pump.fault.seal_leak.symptom", doc_id="doc-001"):
    return KnowledgeNode(
        address=address,
        structural_location="§3.1.s1",
        anchor_phrase="vibration at shaft coupling",
        content="Visible liquid dripping from shaft seal area.",
        doc_id=doc_id,
        doc_title="Pump SOP",
        doc_version="hash:abc123",
    )


def _doc(doc_id="doc-001"):
    return Document(
        doc_id=doc_id, title="Pump SOP", filepath="pump.md",
        version_hash="hash:abc123", domain="equipment",
        subdomain_claims=["fault", "maintenance"],
        subdomain_shared=["standard"],
        skill_card={"purpose": "Test", "strengths": [], "weaknesses": []},
    )


class TestSigilStorage:

    def test_save_and_query_exact(self, db):
        db.save_node(_node())
        results = db.query_exact("equipment.pump.fault.seal_leak.symptom")
        assert len(results) == 1
        assert results[0]["address"] == "equipment.pump.fault.seal_leak.symptom"
        assert results[0]["anchor_phrase"] == "vibration at shaft coupling"

    def test_query_prefix(self, db):
        db.save_node(_node("equipment.pump.fault.seal_leak.symptom"))
        db.save_node(_node("equipment.pump.fault.seal_leak.how"))
        results = db.query_prefix("equipment.pump")
        assert len(results) == 2

    def test_query_anchor(self, db):
        db.save_node(_node())
        results = db.query_anchor("vibration")
        assert len(results) >= 1

    def test_query_empty(self, db):
        results = db.query_exact("nonexistent.address.here.what")
        assert results == []

    def test_list_addresses(self, db):
        db.save_node(_node("equipment.pump.fault.seal_leak.symptom"))
        db.save_node(_node("equipment.pump.fault.overheating.symptom"))
        addresses = db.list_addresses()
        assert len(addresses) == 2
        assert "equipment.pump.fault.seal_leak.symptom" in addresses

    def test_list_addresses_prefix_filter(self, db):
        db.save_node(_node("equipment.pump.fault.seal_leak.symptom"))
        db.save_node(_node("ai.definition.mccarthy.what", doc_id="doc-002"))
        addresses = db.list_addresses(prefix="equipment")
        assert len(addresses) == 1

    def test_save_document(self, db):
        db.save_document(_doc())
        docs = db.get_all_documents()
        assert len(docs) == 1
        assert docs[0]["domain"] == "equipment"

    def test_skill_cards(self, db):
        db.save_document(_doc())
        cards = db.get_skill_cards()
        assert len(cards) == 1
        assert cards[0]["skill_card"]["purpose"] == "Test"

    def test_conflict_detection(self, db):
        db.save_node(_node(doc_id="doc-001"))
        # Insert node at same address with very different content
        conflicting = KnowledgeNode(
            address="equipment.pump.fault.seal_leak.symptom",
            structural_location="§1.s1",
            anchor_phrase="completely different phrase",
            content="This is completely unrelated content about something else entirely.",
            doc_id="doc-002",
            doc_title="Other Doc",
            doc_version="hash:xyz",
        )
        db.save_node(conflicting)
        conflicts = db.get_conflicts()
        assert len(conflicts) >= 1

    def test_record_transition(self, db):
        db.record_transition("equipment.pump.fault.seal_leak.symptom",
                             "equipment.pump.fault.seal_leak.how")
        transitions = db.get_top_transitions("equipment.pump.fault.seal_leak.symptom")
        assert len(transitions) == 1
        assert transitions[0]["count"] == 1

    def test_stats(self, db):
        db.save_document(_doc())
        db.save_node(_node())
        s = db.get_stats()
        assert s["total_nodes"] == 1
        assert s["total_documents"] == 1
        assert s["pending_conflicts"] == 0
