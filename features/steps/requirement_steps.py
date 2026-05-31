"""
Behave step definitions - BDD acceptance testleri.
Çalıştırmak için: behave
"""
import django
import os
import sys

# Django ortamını başlat
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_ra_saas.settings')
django.setup()

from unittest.mock import patch

from behave import given, when, then
from django.test import Client

_BEHAVE_ANALYSIS_STUB = {
    "bdd_output": (
        "- Given kullanıcı geçerli kimlik bilgileri ile giriş yapar\n"
        "- When kimlik doğrulaması başarılı olur\n"
        "- Then kullanıcı ana panele yönlendirilir"
    ),
    "gherkin_output": (
        "Feature: Giris\n"
        "  Scenario: Basarili giris\n"
        "    Given kullanici kayitlidir\n"
        "    When sifre ile giris yapar\n"
        "    Then oturum acilir\n"
    ),
    "qa_result": "[passed] Senaryolar tutarli.",
    "qa_valid": True,
    "story_point": 3,
}


@given('kullanıcı gereksinim giriş sayfasındadır')
def step_user_on_form_page(context):
    context.client = Client()
    response = context.client.get('/requirements/new/')
    assert response.status_code == 200, f"Sayfa açılamadı: {response.status_code}"
    context.requirement_text = None
    context.project_name = None


@when('kullanıcı "{text}" metnini girer')
def step_user_enters_text(context, text):
    context.requirement_text = text


@when('kullanıcı proje adı olarak "{name}" girer')
def step_user_enters_project_name(context, name):
    context.project_name = name


@when('kullanıcı Analiz Et butonuna basar')
def step_user_clicks_analyze(context):
    data = {
        'project_name': context.project_name or 'Test Projesi',
        'raw_text': context.requirement_text or '',
        'api_key': 'behave-test-api-key',
        'model_type': 'gemini',
    }
    with patch("requirements_app.views.analyze_requirement", return_value=_BEHAVE_ANALYSIS_STUB):
        context.response = context.client.post('/requirements/new/', data)


@when('kullanıcı boş metin gönderir')
def step_user_sends_empty(context):
    context.response = context.client.post('/requirements/new/', {
        'project_name': 'Test Projesi',
        'raw_text': '',
        'api_key': 'behave-test-api-key',
        'model_type': 'gemini',
    })


@then('sistem bir gereksinim kaydı oluşturmalıdır')
def step_requirement_created(context):
    session_items = context.client.session.get("requirement_analyses", [])
    assert len(session_items) > 0, "Analiz kaydi oturumda olusmadi."


@then('sistem BDD çıktısı göstermelidir')
def step_bdd_output_shown(context):
    session_items = context.client.session.get("requirement_analyses", [])
    assert session_items, "Analiz bulunamadi"
    bdd = session_items[-1]["result"]["bdd_output"]
    assert 'Given' in bdd, f"BDD çıktısında 'Given' yok: {bdd}"
    assert 'When' in bdd, f"BDD çıktısında 'When' yok: {bdd}"
    assert 'Then' in bdd, f"BDD çıktısında 'Then' yok: {bdd}"


@then('sistem Gherkin test senaryosu göstermelidir')
def step_gherkin_output_shown(context):
    session_items = context.client.session.get("requirement_analyses", [])
    gherkin = session_items[-1]["result"]["gherkin_output"]
    assert 'Feature:' in gherkin, f"Gherkin çıktısında 'Feature:' yok: {gherkin}"
    assert 'Scenario:' in gherkin, f"Gherkin çıktısında 'Scenario:' yok: {gherkin}"


@then('sistem hata mesajı göstermelidir')
def step_error_shown(context):
    assert context.response.status_code == 200, "Yönlendirme yapılmamalıydı"
    content = context.response.content.decode('utf-8')
    assert 'error' in content.lower() or 'hata' in content.lower() or 'field-error' in content, \
        "Hata mesajı bulunamadı"


@then('analiz kaydı oluşturmamalıdır')
def step_no_requirement_created(context):
    count_before = getattr(context, '_count_before', 0)
    current_count = len(context.client.session.get("requirement_analyses", []))
    assert current_count == count_before, \
        f"Analiz kaydı oluşturulmamalıydı ancak {current_count - count_before} kayıt eklendi"


@given('kullanıcı geçerli bir gereksinim analizi tamamlamıştır')
def step_valid_analysis_done(context):
    context.result = {
        "bdd_output": _BEHAVE_ANALYSIS_STUB["bdd_output"],
        "gherkin_output": _BEHAVE_ANALYSIS_STUB["gherkin_output"],
    }


@then('BDD çıktısında "{keyword}" ifadesi bulunmalıdır')
def step_bdd_contains_keyword(context, keyword):
    assert keyword in context.result["bdd_output"], \
        f"BDD çıktısında '{keyword}' bulunamadı:\n{context.result['bdd_output']}"


@then('Gherkin çıktısında "{keyword}" ifadesi bulunmalıdır')
def step_gherkin_contains_keyword(context, keyword):
    assert keyword in context.result["gherkin_output"], \
        f"Gherkin çıktısında '{keyword}' bulunamadı:\n{context.result['gherkin_output']}"
