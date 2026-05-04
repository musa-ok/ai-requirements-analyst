"""Stateless mimari icin testler."""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import RequirementForm
from .services import analyze_requirement, estimate_story_points


class RequirementFormTests(TestCase):
    def test_valid_form(self):
        form = RequirementForm(
            data={
                "project_name": "Test Projesi",
                "raw_text": "Kullanici sisteme e-posta ve sifre ile giris yapabilmelidir.",
            }
        )
        self.assertTrue(form.is_valid())

    def test_short_text_invalid(self):
        form = RequirementForm(data={"project_name": "Test", "raw_text": "kisa"})
        self.assertFalse(form.is_valid())


class ServiceTests(TestCase):
    @patch("requirements_app.services._resolve_gemini_api_key", return_value="test-gemini-key")
    @patch("backend.main.analysis_workflow.invoke")
    def test_analyze_requirement_returns_all_outputs(self, mock_invoke, _mock_resolve_key):
        mock_invoke.return_value = {
            "acceptance_criteria": [
                "Given kullanici arama kutusuna yazar",
                "When sonuclar filtrelenir",
                "Then liste gosterilir",
            ],
            "gherkin_scenarios": [
                "Feature: Arama\n  Scenario: Sonuc\n    Given x\n    When y\n    Then z"
            ],
            "story_points": 3,
            "qa_status": "passed",
            "qa_feedback": "Tutarli.",
        }
        payload = analyze_requirement(
            "Kullanici urun aramasi yapabilmelidir.", project_name="Demo"
        )
        self.assertIn("bdd_output", payload)
        self.assertIn("gherkin_output", payload)
        self.assertIn("qa_result", payload)
        self.assertIn("story_point", payload)

    def test_story_points_integer(self):
        self.assertIsInstance(estimate_story_points("A" * 300), int)


@patch(
    "requirements_app.views.analyze_requirement",
    return_value={
        "bdd_output": "- Given kullanici profili acar\n- When kaydeder\n- Then mesaj gorulur",
        "gherkin_output": "Feature: Profil\n  Scenario: Kayit\n    Given kullanici giris yapmistir\n",
        "qa_result": "[passed] Tamam.",
        "qa_valid": True,
        "story_point": 3,
    },
)
class SessionFlowTests(TestCase):
    def test_create_analysis_stored_in_session(self, _mock_analyze):
        response = self.client.post(
            reverse("requirement_new"),
            {
                "project_name": "Demo",
                "raw_text": "Kullanici profilini guncelleyebilmeli ve degisiklikleri kaydedebilmelidir.",
            },
        )
        self.assertEqual(response.status_code, 302)
        session_items = self.client.session.get("requirement_analyses", [])
        self.assertEqual(len(session_items), 1)
        self.assertEqual(session_items[0]["status"], "analyzed")

    def test_detail_404_when_missing(self, _mock_analyze):
        response = self.client.get(reverse("requirement_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)
