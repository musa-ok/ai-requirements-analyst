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

from behave import given, when, then
from django.test import Client
from django.urls import reverse
from requirements_app.models import Requirement, AnalysisResult, Project
from requirements_app.services import generate_bdd_output, generate_gherkin_output


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
    }
    context.response = context.client.post('/requirements/new/', data)


@when('kullanıcı boş metin gönderir')
def step_user_sends_empty(context):
    context.response = context.client.post('/requirements/new/', {
        'project_name': 'Test Projesi',
        'raw_text': '',
    })


@then('sistem bir gereksinim kaydı oluşturmalıdır')
def step_requirement_created(context):
    assert Requirement.objects.count() > 0, "Gereksinim kaydı oluşturulmadı!"


@then('sistem BDD çıktısı göstermelidir')
def step_bdd_output_shown(context):
    req = Requirement.objects.order_by('-created_at').first()
    assert req is not None, "Gereksinim bulunamadı"
    assert hasattr(req, 'result'), "AnalysisResult ilişkisi yok"
    bdd = req.result.bdd_output
    assert 'Given' in bdd, f"BDD çıktısında 'Given' yok: {bdd}"
    assert 'When' in bdd, f"BDD çıktısında 'When' yok: {bdd}"
    assert 'Then' in bdd, f"BDD çıktısında 'Then' yok: {bdd}"


@then('sistem Gherkin test senaryosu göstermelidir')
def step_gherkin_output_shown(context):
    req = Requirement.objects.order_by('-created_at').first()
    gherkin = req.result.gherkin_output
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
    current_count = Requirement.objects.count()
    assert current_count == count_before, \
        f"Analiz kaydı oluşturulmamalıydı ancak {current_count - count_before} kayıt eklendi"


@given('kullanıcı geçerli bir gereksinim analizi tamamlamıştır')
def step_valid_analysis_done(context):
    project = Project.objects.create(name="BDD Test Projesi")
    req = Requirement.objects.create(
        project=project,
        raw_text="Kullanıcı sisteme e-posta ve şifre ile giriş yapabilmelidir.",
        status='analyzed',
    )
    bdd = generate_bdd_output(req.raw_text)
    gherkin = generate_gherkin_output(req.raw_text)
    context.result = AnalysisResult.objects.create(
        requirement=req,
        bdd_output=bdd,
        gherkin_output=gherkin,
        qa_result="Gereksinim geçerlidir.",
        story_point=3,
    )


@then('BDD çıktısında "{keyword}" ifadesi bulunmalıdır')
def step_bdd_contains_keyword(context, keyword):
    assert keyword in context.result.bdd_output, \
        f"BDD çıktısında '{keyword}' bulunamadı:\n{context.result.bdd_output}"


@then('Gherkin çıktısında "{keyword}" ifadesi bulunmalıdır')
def step_gherkin_contains_keyword(context, keyword):
    assert keyword in context.result.gherkin_output, \
        f"Gherkin çıktısında '{keyword}' bulunamadı:\n{context.result.gherkin_output}"
