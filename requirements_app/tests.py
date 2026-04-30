"""
Unit testler ve functional testler.
Çalıştırmak için: python manage.py test  veya  pytest
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import Project, Requirement, AnalysisResult
from .services import (
    generate_bdd_output,
    generate_gherkin_output,
    run_qa_validation,
    estimate_story_points,
    analyze_requirement,
)
from .forms import RequirementForm


# ---------------------------------------------------------------------------
# Unit Testler - Servis Katmanı
# ---------------------------------------------------------------------------

class BDDGeneratorTests(TestCase):

    def test_bdd_output_not_empty(self):
        result = generate_bdd_output("Kullanıcı sisteme giriş yapabilmelidir.")
        self.assertTrue(len(result) > 0)

    def test_bdd_output_contains_given(self):
        result = generate_bdd_output("Kullanıcı arama yapabilmelidir.")
        self.assertIn("Given", result)

    def test_bdd_output_contains_when(self):
        result = generate_bdd_output("Kullanıcı arama yapabilmelidir.")
        self.assertIn("When", result)

    def test_bdd_output_contains_then(self):
        result = generate_bdd_output("Kullanıcı arama yapabilmelidir.")
        self.assertIn("Then", result)

    def test_bdd_output_includes_raw_text(self):
        raw = "Kullanıcı profil sayfasını güncelleyebilmelidir."
        result = generate_bdd_output(raw)
        self.assertIn(raw, result)


class GherkinGeneratorTests(TestCase):

    def test_gherkin_output_not_empty(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertTrue(len(result) > 0)

    def test_gherkin_output_contains_feature(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertIn("Feature:", result)

    def test_gherkin_output_contains_scenario(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertIn("Scenario:", result)

    def test_gherkin_output_contains_given(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertIn("Given", result)

    def test_gherkin_output_contains_when(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertIn("When", result)

    def test_gherkin_output_contains_then(self):
        result = generate_gherkin_output("Kullanıcı kayıt olabilmelidir.")
        self.assertIn("Then", result)


class QAValidatorTests(TestCase):

    def test_empty_input_is_invalid(self):
        result = run_qa_validation("")
        self.assertFalse(result['valid'])

    def test_very_short_input_is_invalid(self):
        result = run_qa_validation("Ekle")
        self.assertFalse(result['valid'])

    def test_valid_input_is_accepted(self):
        result = run_qa_validation("Kullanıcı sisteme e-posta ve şifre ile giriş yapabilmelidir.")
        self.assertTrue(result['valid'])

    def test_score_is_integer(self):
        result = run_qa_validation("Kullanıcı raporları PDF olarak indirebilmelidir.")
        self.assertIsInstance(result['score'], int)

    def test_score_range(self):
        result = run_qa_validation("Kullanıcı raporları PDF olarak indirebilmelidir.")
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)


class StoryPointEstimatorTests(TestCase):

    def test_short_text_returns_low_points(self):
        points = estimate_story_points("Giriş yap.")
        self.assertLessEqual(points, 2)

    def test_long_text_returns_higher_points(self):
        long_text = "Kullanıcı " * 60
        points = estimate_story_points(long_text)
        self.assertGreaterEqual(points, 5)

    def test_returns_integer(self):
        points = estimate_story_points("Test metni.")
        self.assertIsInstance(points, int)


# ---------------------------------------------------------------------------
# Unit Testler - Model Katmanı
# ---------------------------------------------------------------------------

class ProjectModelTests(TestCase):

    def test_project_creation(self):
        project = Project.objects.create(name="Test Projesi", description="Açıklama")
        self.assertEqual(project.name, "Test Projesi")
        self.assertIsNotNone(project.pk)

    def test_project_str(self):
        project = Project.objects.create(name="Proje A")
        self.assertEqual(str(project), "Proje A")


class RequirementModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name="Test Projesi")

    def test_requirement_creation(self):
        req = Requirement.objects.create(
            project=self.project,
            raw_text="Kullanıcı giriş yapabilmelidir.",
        )
        self.assertIsNotNone(req.pk)
        self.assertEqual(req.status, 'pending')

    def test_requirement_default_status(self):
        req = Requirement.objects.create(project=self.project, raw_text="Test metni yeterince uzun.")
        self.assertEqual(req.status, 'pending')


class AnalysisResultModelTests(TestCase):

    def setUp(self):
        project = Project.objects.create(name="Proje")
        self.requirement = Requirement.objects.create(project=project, raw_text="Uzun bir gereksinim metni.")

    def test_analysis_result_creation(self):
        result = AnalysisResult.objects.create(
            requirement=self.requirement,
            bdd_output="Given ... When ... Then ...",
            gherkin_output="Feature: ...\n  Scenario: ...",
            qa_result="Geçerli",
            story_point=3,
        )
        self.assertIsNotNone(result.pk)
        self.assertEqual(result.story_point, 3)


# ---------------------------------------------------------------------------
# Unit Testler - Form Katmanı
# ---------------------------------------------------------------------------

class RequirementFormTests(TestCase):

    def test_valid_form(self):
        form = RequirementForm(data={
            'project_name': 'Test Projesi',
            'raw_text': 'Kullanıcı sisteme giriş yapabilmelidir ve şifremi unuttum akışı bulunmalıdır.',
        })
        self.assertTrue(form.is_valid())

    def test_empty_raw_text_invalid(self):
        form = RequirementForm(data={'project_name': 'Test', 'raw_text': ''})
        self.assertFalse(form.is_valid())

    def test_too_short_raw_text_invalid(self):
        form = RequirementForm(data={'project_name': 'Test', 'raw_text': 'Kısa'})
        self.assertFalse(form.is_valid())

    def test_empty_project_name_invalid(self):
        form = RequirementForm(data={'project_name': '', 'raw_text': 'Geçerli uzun bir gereksinim metni.'})
        self.assertFalse(form.is_valid())


# ---------------------------------------------------------------------------
# Functional Testler - View Katmanı
# ---------------------------------------------------------------------------

class HomePageTests(TestCase):

    def test_home_page_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'requirements_app/home.html')

    def test_home_page_contains_project_name(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'AI_RA')


class RequirementFormPageTests(TestCase):

    def test_form_page_returns_200(self):
        response = self.client.get(reverse('requirement_new'))
        self.assertEqual(response.status_code, 200)

    def test_form_page_uses_correct_template(self):
        response = self.client.get(reverse('requirement_new'))
        self.assertTemplateUsed(response, 'requirements_app/requirement_form.html')


class RequirementCreateTests(TestCase):

    def _post_valid_form(self):
        return self.client.post(reverse('requirement_new'), {
            'project_name': 'Test Projesi',
            'raw_text': 'Kullanıcı e-posta ve şifre ile sisteme giriş yapabilmeli, hatalı girişte uyarı almalıdır.',
        })

    def test_valid_form_redirects_to_result(self):
        response = self._post_valid_form()
        self.assertEqual(response.status_code, 302)

    def test_valid_form_creates_requirement(self):
        self._post_valid_form()
        self.assertEqual(Requirement.objects.count(), 1)

    def test_valid_form_creates_analysis_result(self):
        self._post_valid_form()
        self.assertEqual(AnalysisResult.objects.count(), 1)

    def test_empty_form_does_not_redirect(self):
        response = self.client.post(reverse('requirement_new'), {
            'project_name': 'Test',
            'raw_text': '',
        })
        self.assertEqual(response.status_code, 200)

    def test_empty_form_does_not_create_requirement(self):
        self.client.post(reverse('requirement_new'), {
            'project_name': 'Test',
            'raw_text': '',
        })
        self.assertEqual(Requirement.objects.count(), 0)


class RequirementDetailTests(TestCase):

    def setUp(self):
        project = Project.objects.create(name="Demo Proje")
        self.requirement = Requirement.objects.create(
            project=project,
            raw_text="Kullanıcı profil bilgilerini güncelleyebilmelidir.",
            status='analyzed',
        )
        self.result = AnalysisResult.objects.create(
            requirement=self.requirement,
            bdd_output="Given kullanıcı giriş yapmış\nWhen profil günceller\nThen değişiklik kaydedilir",
            gherkin_output="Feature: Profil Güncelleme\n  Scenario: Başarılı güncelleme",
            qa_result="Gereksinim geçerlidir.",
            story_point=2,
        )

    def test_detail_page_returns_200(self):
        response = self.client.get(reverse('requirement_detail', kwargs={'pk': self.requirement.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_contains_bdd_output(self):
        response = self.client.get(reverse('requirement_detail', kwargs={'pk': self.requirement.pk}))
        self.assertContains(response, 'Given')
        self.assertContains(response, 'When')
        self.assertContains(response, 'Then')

    def test_detail_page_contains_gherkin_output(self):
        response = self.client.get(reverse('requirement_detail', kwargs={'pk': self.requirement.pk}))
        self.assertContains(response, 'Feature')
        self.assertContains(response, 'Scenario')

    def test_detail_page_404_for_invalid_id(self):
        response = self.client.get(reverse('requirement_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class RequirementListTests(TestCase):

    def test_list_page_returns_200(self):
        response = self.client.get(reverse('requirement_list'))
        self.assertEqual(response.status_code, 200)

    def test_list_page_uses_correct_template(self):
        response = self.client.get(reverse('requirement_list'))
        self.assertTemplateUsed(response, 'requirements_app/requirement_list.html')
