# Test Kanıtları — AI_RA

> **Güncelleme (2026):** Eski mock generator testleri kaldırıldı. Güncel test seti aşağıdadır.

## 1. Unit / Functional (Django + pytest)

### Komut
```bash
python manage.py test requirements_app
python -m pytest requirements_app/tests.py tests/test_health.py tests/test_integration.py
```

### Kapsam (özet)
| Dosya | Test sayısı | Açıklama |
|-------|-------------|----------|
| `requirements_app/tests.py` | 8 | Form, servis, export köprüsü, oturum akışı |
| `tests/test_health.py` | 2 | `/` ve `/health` |
| `tests/test_integration.py` | contract | PDF, Word, Jira, GitHub, register |

Entegrasyon (`@pytest.mark.integration`): gerçek Gemini/Chroma — `.env` anahtarı gerekir.

## 2. BDD (behave)

```bash
behave features/requirement_analysis.feature
```

Analiz adımları `analyze_requirement` mock’lanır; oturum ve BDD/Gherkin çıktı doğrulanır.

## 3. CI

GitHub Actions: `.github/workflows/ci.yml` — push/PR’da Django test + pytest + behave.
