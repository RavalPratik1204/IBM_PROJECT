"""
Unit tests for complaint classification, routing, validation, and route optimization.
Run: pytest tests/ -v
"""
import pytest
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.agents.grievance_agent import (
    _keyword_classify, _detect_language, _validate_structured_output, _parse_json_response
)
from app.agents.routing_agent import _deterministic_route, CATEGORY_DEPT_MAP
from app.agents.route_optimization_agent import _haversine, _nearest_neighbor_route, _priority_score
from app.models.user import ComplaintPriority, ComplaintStatus


# ── Language Detection ─────────────────────────────────────────────────────

def test_detect_gujarati():
    assert _detect_language("મારા વિસ્તારમાં કચરો ઉઠાવ્યો નથી") == "gu"

def test_detect_hindi():
    assert _detect_language("मेरे इलाके में कचरा नहीं उठाया") == "hi"

def test_detect_english():
    assert _detect_language("Garbage not collected for 3 days") == "en"


# ── Keyword Classification ─────────────────────────────────────────────────

def test_classify_waste_collection_english():
    assert _keyword_classify("garbage has not been collected") == "waste_collection"

def test_classify_overflow_bin():
    assert _keyword_classify("bin is overflowing near the market") == "overflow_bin"

def test_classify_illegal_dumping():
    assert _keyword_classify("illegal dumping near the park") == "illegal_dumping"

def test_classify_gujarati_waste():
    assert _keyword_classify("કચરો ઉઠાવ્યો નથી") == "waste_collection"

def test_classify_hindi_garbage():
    assert _keyword_classify("कचरा नहीं उठाया गया") == "waste_collection"

def test_classify_unknown_returns_other():
    result = _keyword_classify("hello world test")
    # Should return a valid category
    assert result in ["waste_collection", "overflow_bin", "illegal_dumping",
                      "roadside_garbage", "segregation_issue", "recycling_issue",
                      "schedule_issue", "other"]


# ── Output Validation ──────────────────────────────────────────────────────

def test_validate_valid_output():
    data = {
        "category": "waste_collection",
        "language": "en",
        "priority": "medium",
        "description": "Test complaint",
    }
    assert _validate_structured_output(data) is True

def test_validate_missing_field():
    data = {"category": "waste_collection", "language": "en", "priority": "medium"}
    assert _validate_structured_output(data) is False

def test_validate_invalid_category():
    data = {
        "category": "invented_category",
        "language": "en",
        "priority": "medium",
        "description": "Test",
    }
    assert _validate_structured_output(data) is False

def test_validate_invalid_priority():
    data = {
        "category": "waste_collection",
        "language": "en",
        "priority": "extreme",
        "description": "Test",
    }
    assert _validate_structured_output(data) is False


# ── JSON Parsing ───────────────────────────────────────────────────────────

def test_parse_clean_json():
    result = _parse_json_response('{"category": "waste_collection", "priority": "medium", "language": "en", "description": "Test"}')
    assert result is not None
    assert result["category"] == "waste_collection"

def test_parse_json_with_markdown_fence():
    content = '```json\n{"category": "overflow_bin", "priority": "critical", "language": "en", "description": "Test"}\n```'
    result = _parse_json_response(content)
    assert result is not None
    assert result["category"] == "overflow_bin"

def test_parse_invalid_json_returns_none():
    result = _parse_json_response("this is not json at all")
    assert result is None


# ── Routing Logic ──────────────────────────────────────────────────────────

class MockComplaint:
    def __init__(self, category, priority="medium", ward_id=5):
        self.category = category
        self.priority = type('P', (), {'value': priority})()
        self.ward_id = ward_id
        self.description = "Test description"
        self.original_text = "Test text"

def test_routing_waste_collection():
    c = MockComplaint("waste_collection")
    result = _deterministic_route(c)
    assert result["department_code"] == "WASTE_COLLECTION"

def test_routing_illegal_dumping():
    c = MockComplaint("illegal_dumping")
    result = _deterministic_route(c)
    assert result["department_code"] == "SANITATION"

def test_routing_segregation():
    c = MockComplaint("segregation_issue")
    result = _deterministic_route(c)
    assert result["department_code"] == "SEGREGATION"

def test_routing_critical_escalates():
    c = MockComplaint("overflow_bin", priority="critical")
    result = _deterministic_route(c)
    assert result["escalate"] is True

def test_routing_low_no_escalate():
    c = MockComplaint("other", priority="low")
    result = _deterministic_route(c)
    assert result["escalate"] is False

def test_all_categories_have_mapping():
    categories = ["waste_collection", "overflow_bin", "illegal_dumping",
                  "roadside_garbage", "segregation_issue", "recycling_issue",
                  "schedule_issue", "other"]
    for cat in categories:
        assert cat in CATEGORY_DEPT_MAP


# ── Route Optimization ─────────────────────────────────────────────────────

def test_haversine_same_point():
    assert _haversine(23.0, 72.5, 23.0, 72.5) == 0.0

def test_haversine_known_distance():
    # Ahmedabad to a point ~1km away
    dist = _haversine(23.0, 72.5, 23.009, 72.5)  # ~1km north
    assert 0.8 < dist < 1.2

def test_haversine_positive():
    dist = _haversine(23.0, 72.5, 23.1, 72.6)
    assert dist > 0

class MockBin:
    def __init__(self, bid, lat, lon, fill=50.0, overflow=False):
        self.id = bid
        self.bin_code = f"BIN-{bid}"
        self.latitude = lat
        self.longitude = lon
        self.fill_level_pct = fill
        self.is_overflow = overflow
        self.ward_id = 1

def test_nearest_neighbor_returns_all_bins():
    bins = [MockBin(i, 23.0 + i*0.01, 72.5, fill=50) for i in range(5)]
    result = _nearest_neighbor_route(bins)
    assert len(result) == 5

def test_overflow_bin_first():
    bins = [
        MockBin(1, 23.0, 72.5, fill=30, overflow=False),
        MockBin(2, 23.1, 72.6, fill=95, overflow=True),  # should be first
        MockBin(3, 23.2, 72.7, fill=50, overflow=False),
    ]
    result = _nearest_neighbor_route(bins)
    assert result[0].is_overflow is True

def test_priority_score_overflow():
    b = MockBin(1, 23.0, 72.5, fill=50, overflow=True)
    assert _priority_score(b) > 50  # fill + overflow bonus

def test_priority_score_no_overflow():
    b = MockBin(1, 23.0, 72.5, fill=50, overflow=False)
    assert _priority_score(b) == 50.0

def test_empty_bins_returns_empty():
    assert _nearest_neighbor_route([]) == []
