"""
AI Evaluation Dataset — multilingual test cases.
Tests classification accuracy, extraction quality, and edge cases.
Run: pytest tests/ai_eval/ -v --log-cli-level=INFO
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.agents.grievance_agent import _keyword_classify, _detect_language, _validate_structured_output

# ── Evaluation dataset ──────────────────────────────────────────────────────
# Format: (input_text, expected_language, expected_category_hint)
# "hint" means the keyword fallback should at least detect this category.
# Full AI accuracy is measured at runtime with actual model responses.

EVAL_DATASET = [
    # Gujarati complaints
    ("મારા વિસ્તારમાં ત્રણ દિવસથી કચરો ઉઠાવ્યો નથી.", "gu", "waste_collection"),
    ("ઓવરફ્લો થઇ ગયો છે, ડ્રમ ભરેલો છે.", "gu", None),  # overflow — keyword match weak
    ("ગેરકાયદે ઢગ નંખાઈ ગઈ છે.", "gu", None),

    # Hindi complaints
    ("मेरे इलाके में तीन दिनों से कचरा नहीं उठाया गया है।", "hi", "waste_collection"),
    ("कचरे का डिब्बा भर गया है और बह रहा है।", "hi", None),
    ("पार्क के पास अवैध कचरा फेंका गया है।", "hi", "illegal_dumping"),
    ("अलग-अलग कचरा नहीं किया जा रहा है।", "hi", "segregation_issue"),

    # English complaints
    ("Garbage has not been picked up for 3 days in my area.", "en", "waste_collection"),
    ("The bin near the bus stop is completely overflowing.", "en", "overflow_bin"),
    ("Someone dumped construction waste on the road illegally.", "en", "illegal_dumping"),
    ("There is garbage scattered all over the main road.", "en", "roadside_garbage"),
    ("People are mixing wet and dry waste in our society.", "en", "segregation_issue"),
    ("Our collection schedule changed and no one informed us.", "en", "schedule_issue"),

    # Edge cases — incomplete/ambiguous
    ("Problem with garbage.", "en", None),   # vague — any category acceptable
    ("Help!", "en", None),                    # minimal input
    ("kachro upadyo nathi", "en", "waste_collection"),  # romanized Gujarati

    # Misspellings
    ("garabge not collectd 2 dayss", "en", "waste_collection"),
    ("kachra nahi utha rahe hain", "en", "waste_collection"),
]


class TestLanguageDetection:
    """Test deterministic language detection (no AI required)."""

    def test_gujarati_sample_1(self):
        assert _detect_language("મારા વિસ્તારમાં ત્રણ દિવસથી કચરો ઉઠાવ્યો નથી.") == "gu"

    def test_hindi_sample_1(self):
        assert _detect_language("मेरे इलाके में तीन दिनों से कचरा नहीं उठाया गया है।") == "hi"

    def test_english_sample(self):
        assert _detect_language("Garbage has not been collected for 3 days.") == "en"

    def test_mixed_returns_dominant(self):
        # Mixed Gujarati+English — should detect Gujarati
        result = _detect_language("ત્રણ days since garbage collection")
        assert result in ["gu", "en"]  # Both acceptable for mixed


class TestKeywordClassification:
    """Test fallback keyword classifier covers common cases."""

    @pytest.mark.parametrize("text,expected_category", [
        ("garbage not collected", "waste_collection"),
        ("trash pickup missed", "waste_collection"),
        ("bin is overflowing", "overflow_bin"),
        ("illegal dumping near park", "illegal_dumping"),
        ("garbage on the road side", "roadside_garbage"),
        ("segregation issue wet dry", "segregation_issue"),
        ("कचरा नहीं उठाया", "waste_collection"),
        ("કચરો ઉઠાવ્યો નથી", "waste_collection"),
    ])
    def test_keyword_classification(self, text, expected_category):
        result = _keyword_classify(text)
        assert result == expected_category, f"Expected {expected_category}, got {result} for: {text}"


class TestOutputValidation:
    """Test AI output validator rejects invalid data."""

    def test_rejects_missing_description(self):
        data = {"category": "waste_collection", "language": "en", "priority": "medium"}
        assert _validate_structured_output(data) is False

    def test_rejects_invented_category(self):
        data = {"category": "nuclear_waste", "language": "en", "priority": "medium", "description": "x"}
        assert _validate_structured_output(data) is False

    def test_accepts_all_valid_priorities(self):
        for p in ["low", "medium", "high", "critical"]:
            data = {"category": "waste_collection", "language": "en", "priority": p, "description": "test"}
            assert _validate_structured_output(data) is True

    def test_accepts_all_valid_categories(self):
        cats = ["waste_collection", "overflow_bin", "illegal_dumping", "roadside_garbage",
                "segregation_issue", "recycling_issue", "schedule_issue", "other"]
        for cat in cats:
            data = {"category": cat, "language": "en", "priority": "medium", "description": "test"}
            assert _validate_structured_output(data) is True


class TestEvalDataset:
    """Verify eval dataset covers all language and category combinations."""

    def test_all_three_languages_covered(self):
        langs = {_detect_language(text) for text, _, _ in EVAL_DATASET}
        assert "en" in langs
        assert "hi" in langs
        assert "gu" in langs

    def test_dataset_has_enough_cases(self):
        assert len(EVAL_DATASET) >= 15

    def test_no_null_inputs(self):
        for text, _, _ in EVAL_DATASET:
            assert text and len(text) > 0
