"""Tests for SigilRouter."""

import pytest
from core.models import KnowledgeNode
from core.router import SigilRouter
from storage.db import SigilStorage


@pytest.fixture
def router(tmp_path):
    storage = SigilStorage(str(tmp_path / "test.db"))
    # Seed with test nodes
    nodes = [
        ("equipment.pump.fault.seal_leak.symptom", "vibration at shaft", "Vibration at shaft coupling, liquid dripping."),
        ("equipment.pump.fault.seal_leak.how",     "replace mechanical",  "Replace mechanical seal per Drawing PM-021."),
        ("equipment.pump.fault.overheating.symptom","temperature exceeds", "Body temperature exceeding 70°C."),
        ("ai.definition.mccarthy.what",            "制造智能机器",          "制造智能机器的科学与工程。"),
    ]
    for addr, anchor, content in nodes:
        storage.save_node(KnowledgeNode(
            address=addr, structural_location="§1.s1",
            anchor_phrase=anchor, content=content,
            doc_id="test", doc_title="Test Doc", doc_version="v1",
        ))
    r = SigilRouter(storage)
    yield r
    storage.close()


class TestSigilRouter:

    def test_tier1_exact_match(self, router):
        result = router.query("equipment.pump.fault.seal_leak.symptom")
        assert result["tier"] == 1
        assert result["tier_name"] == "exact_match"
        assert result["count"] == 1
        assert result["results"][0]["address"] == "equipment.pump.fault.seal_leak.symptom"

    def test_tier2_prefix_match(self, router):
        result = router.query("equipment.pump")
        assert result["tier"] == 2
        assert result["tier_name"] == "prefix_match"
        assert result["count"] >= 2

    def test_tier2_single_domain(self, router):
        result = router.query("ai")
        assert result["tier"] == 2
        assert result["count"] >= 1

    def test_tier3_fuzzy_anchor(self, router):
        # Anchor search matches on partial anchor phrase text
        result = router.query("vibration at shaft")
        assert result["tier"] == 3
        assert result["count"] >= 1

    def test_tier3_no_result(self, router):
        result = router.query("completely unrelated query xyz123")
        assert result["tier"] == 3
        assert result["count"] == 0

    def test_list_all_addresses(self, router):
        result = router.list_addresses()
        assert result["count"] == 4
        assert "equipment.pump.fault.seal_leak.symptom" in result["addresses"]

    def test_list_with_prefix(self, router):
        result = router.list_addresses(prefix="equipment.pump")
        assert result["count"] == 3
        for addr in result["addresses"]:
            assert addr.startswith("equipment.pump")

    def test_skill_cards_empty(self, router):
        result = router.get_skill_cards()
        assert result["count"] == 0  # no documents in this fixture

    def test_stats(self, router):
        s = router.get_stats()
        assert s["total_nodes"] == 4

    def test_empty_query(self, router):
        result = router.query("")
        assert result["tier"] == 0
        assert result["count"] == 0
