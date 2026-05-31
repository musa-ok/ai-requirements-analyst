"""Analist JSON normalizasyon testleri."""

import pytest

from backend.main import _normalize_analyst_payload


def test_accepts_plain_string_criteria():
    data = {
        "acceptance_criteria": [
            "Given kullanici giris sayfasindadir",
            "When gecerli bilgileri girer",
            "Then sisteme erisir",
        ],
        "gherkin_scenarios": ["Feature: Giris\n  Scenario: Basarili\n    Given x"],
        "story_points": 3,
    }
    out = _normalize_analyst_payload(data)
    assert len(out["acceptance_criteria"]) == 3


def test_coerces_given_when_then_objects():
    data = {
        "acceptance_criteria": [
            {"given": "kullanici kayitlidir", "when": "sifre ile giris yapar", "then": "oturum acilir"},
            {"Given": "admin panelindedir", "When": "raporu acar", "Then": "veri gorulur"},
            "Given ek madde metin olarak",
        ],
        "gherkin_scenarios": ["Feature: F\n  Scenario: S\n    Given a"],
        "story_points": 5,
    }
    out = _normalize_analyst_payload(data)
    assert all(isinstance(x, str) and x for x in out["acceptance_criteria"])
    assert "Given" in out["acceptance_criteria"][0]


def test_rejects_too_few_after_coerce():
    with pytest.raises(ValueError, match="acceptance_criteria"):
        _normalize_analyst_payload(
            {
                "acceptance_criteria": [{"given": "", "when": "", "then": ""}],
                "gherkin_scenarios": ["Feature: X"],
                "story_points": 2,
            }
        )
