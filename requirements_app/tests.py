"""Stateless mimari icin testler."""

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
    def test_analyze_requirement_returns_all_outputs(self):
        payload = analyze_requirement("Kullanici urun aramasi yapabilmelidir.")
        self.assertIn("bdd_output", payload)
        self.assertIn("gherkin_output", payload)
        self.assertIn("qa_result", payload)
        self.assertIn("story_point", payload)

    def test_story_points_integer(self):
        self.assertIsInstance(estimate_story_points("A" * 300), int)


class SessionFlowTests(TestCase):
    def test_create_analysis_stored_in_session(self):
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

    def test_detail_404_when_missing(self):
        response = self.client.get(reverse("requirement_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)
