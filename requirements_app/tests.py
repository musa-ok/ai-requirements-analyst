"""Stateless mimari icin testler."""

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import RequirementForm
from .services import analyze_requirement, estimate_story_points


class RequirementFormTests(TestCase):
    def test_valid_form(self):
        form = RequirementForm(
            data={
                "project_name": "Test Projesi",
                "raw_text": "Kullanici sisteme e-posta ve sifre ile giris yapabilmelidir.",
                "api_key": "test-api-key-value",
            }
        )
        self.assertTrue(form.is_valid())

    def test_short_text_invalid(self):
        form = RequirementForm(
            data={
                "project_name": "Test",
                "raw_text": "kisa",
                "api_key": "test-api-key-value",
            }
        )
        self.assertFalse(form.is_valid())


class ServiceTests(TestCase):
    @patch("backend.main.get_analysis_workflow")
    def test_analyze_requirement_returns_all_outputs(self, mock_get_wf):
        mock_wf = mock_get_wf.return_value
        mock_wf.invoke.return_value = {
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
            "Kullanici urun aramasi yapabilmelidir.",
            project_name="Demo",
            api_key="test-gemini-key",
        )
        self.assertIn("bdd_output", payload)
        self.assertIn("gherkin_output", payload)
        self.assertIn("qa_result", payload)
        self.assertIn("story_point", payload)
        self.assertIn("acceptance_criteria", payload)

    def test_story_points_integer(self):
        self.assertIsInstance(estimate_story_points("A" * 300), int)

    def test_format_llm_error_quota(self):
        from requirements_app.services import _format_llm_error

        class ResourceExhausted(Exception):
            pass

        msg = _format_llm_error(ResourceExhausted("429 quota exceeded"))
        self.assertIn("kotasi doldu", msg.lower())


class ExportBridgeTests(TestCase):
    def test_register_in_process_creates_export_record(self):
        import os
        from unittest.mock import patch

        from backend.main import session_store
        from requirements_app.export_bridge import register_analysis_for_export

        session_id = "test-bridge-session"
        with patch.dict(os.environ, {"FASTAPI_BASE_URL": "inprocess"}, clear=False):
            analysis_id = register_analysis_for_export(
            api_session_id=session_id,
            project_name="Bridge Test",
            requirement_text="User can login.",
            acceptance_criteria=["Given x", "When y", "Then z"],
            gherkin_scenarios=["Feature: F\n  Scenario: S\n    Given a"],
            story_points=2,
            qa_feedback="OK",
            qa_status="passed",
            )
        self.assertTrue(analysis_id)
        stored = session_store.get(session_id, {}).get(analysis_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored["project_name"], "Bridge Test")

    def test_format_analysis_for_display(self):
        from requirements_app.export_bridge import _format_analysis_for_display

        formatted = _format_analysis_for_display(
            {
                "acceptance_criteria": ["Given x", "When y", "Then z"],
                "gherkin_scenarios": ["Feature: F\n  Scenario: S\n    Given a"],
                "story_points": 5,
                "qa_status": "passed",
                "qa_feedback": "Tamam.",
            }
        )
        self.assertIn("Given x", formatted["bdd_output"])
        self.assertEqual(formatted["story_point"], 5)
        self.assertIn("[Onaylandi]", formatted["qa_result"])


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
@patch(
    "requirements_app.views.analyze_requirement",
    return_value={
        "bdd_output": "- Given kullanici profili acar\n- When kaydeder\n- Then mesaj gorulur",
        "gherkin_output": "Feature: Profil\n  Scenario: Kayit\n    Given kullanici giris yapmistir\n",
        "qa_result": "[passed] Tamam.",
        "qa_valid": True,
        "story_point": 3,
        "acceptance_criteria": ["Given a", "When b", "Then c"],
        "gherkin_scenarios": ["Feature: P\n  Scenario: S\n    Given x"],
        "story_points": 3,
        "qa_feedback": "Tamam.",
        "qa_status": "passed",
    },
)
class SessionFlowTests(TestCase):
    def test_create_analysis_stored_in_session(self, _mock_analyze):
        response = self.client.post(
            reverse("requirement_new"),
            {
                "project_name": "Demo",
                "raw_text": "Kullanici profilini guncelleyebilmeli ve degisiklikleri kaydedebilmelidir.",
                "api_key": "django-test-api-key",
                "model_type": "gemini",
            },
        )
        self.assertEqual(response.status_code, 302)
        session_items = self.client.session.get("requirement_analyses", [])
        self.assertEqual(len(session_items), 1)
        self.assertEqual(session_items[0]["status"], "analyzed")
        self.assertTrue(session_items[0].get("fastapi_analysis_id"))

    def test_detail_404_when_missing(self, _mock_analyze):
        response = self.client.get(reverse("requirement_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_clear_history_removes_session_items(self, _mock_analyze):
        self.client.post(
            reverse("requirement_new"),
            {
                "project_name": "Demo",
                "raw_text": "Kullanici profilini guncelleyebilmeli ve degisiklikleri kaydedebilmelidir.",
                "api_key": "django-test-api-key",
                "model_type": "gemini",
            },
        )
        self.assertEqual(len(self.client.session.get("requirement_analyses", [])), 1)
        response = self.client.post(reverse("requirement_clear_history"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("requirement_analyses", []), [])

    def test_multiple_large_analyses_persist_in_db_session(self, _mock_analyze):
        large_text = "Kullanici " + ("detayli gereksinim metni. " * 80)
        for index in range(3):
            response = self.client.post(
                reverse("requirement_new"),
                {
                    "project_name": f"Demo {index + 1}",
                    "raw_text": large_text,
                    "api_key": "django-test-api-key",
                    "model_type": "gemini",
                },
            )
            self.assertEqual(response.status_code, 302)
            detail_id = index + 1
            detail = self.client.get(reverse("requirement_detail", kwargs={"pk": detail_id}))
            self.assertEqual(detail.status_code, 200)
            self.assertContains(detail, "Analiz Sonucu")
            self.assertContains(detail, f"#{detail_id}")
            self.assertContains(detail, "BDD")
