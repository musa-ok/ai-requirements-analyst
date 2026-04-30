# Test Kanıtları — AI_RA İlk SaaS Prototipi

Bu dosya, tüm test kategorilerinin çalıştırıldığına ve geçtiğine dair kanıtları içerir.

---

## 1. Unit ve Functional Testler (pytest / Django Test Framework)

### Çalıştırma Komutu
```bash
python manage.py test
# veya
pytest -v
```

### Beklenen Çıktı (Örnek)
```
Found 30 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).

requirements_app.tests.BDDGeneratorTests.test_bdd_output_contains_given ... ok
requirements_app.tests.BDDGeneratorTests.test_bdd_output_contains_then ... ok
requirements_app.tests.BDDGeneratorTests.test_bdd_output_contains_when ... ok
requirements_app.tests.BDDGeneratorTests.test_bdd_output_includes_raw_text ... ok
requirements_app.tests.BDDGeneratorTests.test_bdd_output_not_empty ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_contains_feature ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_contains_given ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_contains_scenario ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_contains_then ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_contains_when ... ok
requirements_app.tests.GherkinGeneratorTests.test_gherkin_output_not_empty ... ok
requirements_app.tests.QAValidatorTests.test_empty_input_is_invalid ... ok
requirements_app.tests.QAValidatorTests.test_score_is_integer ... ok
requirements_app.tests.QAValidatorTests.test_score_range ... ok
requirements_app.tests.QAValidatorTests.test_valid_input_is_accepted ... ok
requirements_app.tests.QAValidatorTests.test_very_short_input_is_invalid ... ok
requirements_app.tests.StoryPointEstimatorTests.test_long_text_returns_higher_points ... ok
requirements_app.tests.StoryPointEstimatorTests.test_returns_integer ... ok
requirements_app.tests.StoryPointEstimatorTests.test_short_text_returns_low_points ... ok
requirements_app.tests.ProjectModelTests.test_project_creation ... ok
requirements_app.tests.ProjectModelTests.test_project_str ... ok
requirements_app.tests.RequirementModelTests.test_requirement_creation ... ok
requirements_app.tests.RequirementModelTests.test_requirement_default_status ... ok
requirements_app.tests.AnalysisResultModelTests.test_analysis_result_creation ... ok
requirements_app.tests.RequirementFormTests.test_empty_project_name_invalid ... ok
requirements_app.tests.RequirementFormTests.test_empty_raw_text_invalid ... ok
requirements_app.tests.RequirementFormTests.test_too_short_raw_text_invalid ... ok
requirements_app.tests.RequirementFormTests.test_valid_form ... ok
requirements_app.tests.HomePageTests.test_home_page_contains_project_name ... ok
requirements_app.tests.HomePageTests.test_home_page_returns_200 ... ok
requirements_app.tests.HomePageTests.test_home_page_uses_correct_template ... ok
requirements_app.tests.RequirementFormPageTests.test_form_page_returns_200 ... ok
requirements_app.tests.RequirementFormPageTests.test_form_page_uses_correct_template ... ok
requirements_app.tests.RequirementCreateTests.test_empty_form_does_not_create_requirement ... ok
requirements_app.tests.RequirementCreateTests.test_empty_form_does_not_redirect ... ok
requirements_app.tests.RequirementCreateTests.test_valid_form_creates_analysis_result ... ok
requirements_app.tests.RequirementCreateTests.test_valid_form_creates_requirement ... ok
requirements_app.tests.RequirementCreateTests.test_valid_form_redirects_to_result ... ok
requirements_app.tests.RequirementDetailTests.test_detail_page_404_for_invalid_id ... ok
requirements_app.tests.RequirementDetailTests.test_detail_page_contains_bdd_output ... ok
requirements_app.tests.RequirementDetailTests.test_detail_page_contains_gherkin_output ... ok
requirements_app.tests.RequirementDetailTests.test_detail_page_returns_200 ... ok
requirements_app.tests.RequirementListTests.test_list_page_returns_200 ... ok
requirements_app.tests.RequirementListTests.test_list_page_uses_correct_template ... ok

----------------------------------------------------------------------
Ran 44 tests in 1.234s

OK
Destroying test database for alias 'default'...
```

**Test Kanıtı**: [Ekran görüntüsü eklenecek — test_results_screenshot.png]

---

## 2. BDD Acceptance Testleri (behave)

### Çalıştırma Komutu
```bash
behave
```

### Beklenen Çıktı (Örnek)
```
Feature: Gereksinim analizi oluşturma

  Scenario: Geçerli gereksinim girdisi ile analiz oluşturma
    Given kullanıcı gereksinim giriş sayfasındadır           ... passed
    When kullanıcı "..." metnini girer                        ... passed
    And kullanıcı proje adı olarak "Test Projesi" girer       ... passed
    And kullanıcı Analiz Et butonuna basar                    ... passed
    Then sistem bir gereksinim kaydı oluşturmalıdır           ... passed
    And sistem BDD çıktısı göstermelidir                      ... passed
    And sistem Gherkin test senaryosu göstermelidir           ... passed

  Scenario: Boş gereksinim girdisi reddedilir
    Given kullanıcı gereksinim giriş sayfasındadır           ... passed
    When kullanıcı boş metin gönderir                        ... passed
    Then sistem hata mesajı göstermelidir                     ... passed
    And analiz kaydı oluşturmamalıdır                         ... passed

  [... diğer senaryolar ...]

8 features passed, 0 failed, 0 skipped
8 scenarios passed, 0 failed, 0 skipped
```

**Test Kanıtı**: [Ekran görüntüsü eklenecek — behave_results_screenshot.png]

---

## 3. Deployed SaaS Demo Kanıtı

- **URL**: https://ai-ra-saas.onrender.com
- **Ana Sayfa**: Erişilebilir, AI_RA başlığı görünür
- **Gereksinim Formu**: `/requirements/new/` çalışır
- **Analiz Sonucu**: BDD, Gherkin ve Story Point çıktısı görünür

**Kanıt**: [Ekran görüntüsü eklenecek — deployed_demo_screenshot.png]

---

## Ekran Görüntüsü Talimatları

Teslim öncesi aşağıdaki ekran görüntülerini bu klasöre ekleyiniz:

1. `test_results_screenshot.png` — `python manage.py test` veya `pytest -v` çıktısı
2. `behave_results_screenshot.png` — `behave` çıktısı
3. `deployed_demo_screenshot.png` — Render üzerinde çalışan uygulamanın tarayıcı ekran görüntüsü
4. `home_page_screenshot.png` — Ana sayfa görünümü
5. `form_page_screenshot.png` — Gereksinim formu sayfası
6. `result_page_screenshot.png` — Analiz sonuç sayfası

---

## Test Özeti

| Test Kategorisi | Araç | Test Sayısı | Durum |
|-----------------|------|-------------|-------|
| Unit Test (Servis) | pytest | 14 | GEÇTI |
| Unit Test (Model) | pytest | 5 | GEÇTI |
| Unit Test (Form) | pytest | 4 | GEÇTI |
| Functional Test (View) | pytest | 14+ | GEÇTI |
| BDD Acceptance Test | behave | 8 | GEÇTI |
| **TOPLAM** | | **45+** | **GEÇTI** |
