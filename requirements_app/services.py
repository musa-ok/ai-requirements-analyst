"""
Gereksinim analizi servis katmanı.
Canlı AI API bağlantısı olmadan deterministik/mock analiz üretir.
"""


def generate_bdd_output(raw_text: str) -> str:
    """Kullanıcı girdisinden BDD formatında çıktı üretir."""
    text = raw_text.strip()
    return (
        f"**Given** kullanıcı sisteme giriş yapmış ve ilgili modüle erişim yetkisine sahip\n"
        f"**When** kullanıcı şu isteği iletir: \"{text}\"\n"
        f"**Then** sistem isteği işleyerek kullanıcıya yapılandırılmış gereksinim çıktısı sunar\n"
        f"**And** sistem bu gereksinimi veritabanına kaydeder"
    )


def generate_gherkin_output(raw_text: str) -> str:
    """Kullanıcı girdisinden Gherkin formatında test senaryosu üretir."""
    text = raw_text.strip()
    short = text[:60] + "..." if len(text) > 60 else text
    return (
        f"Feature: {short}\n\n"
        f"  Scenario: Başarılı gereksinim analizi\n"
        f"    Given kullanıcı gereksinim giriş sayfasındadır\n"
        f"    When kullanıcı \"{short}\" metnini girer\n"
        f"    And kullanıcı \"Analiz Et\" butonuna basar\n"
        f"    Then sistem bir gereksinim kaydı oluşturur\n"
        f"    And BDD formatında çıktı görüntülenir\n"
        f"    And Gherkin test senaryosu görüntülenir\n\n"
        f"  Scenario: Eksik girdi uyarısı\n"
        f"    Given kullanıcı gereksinim giriş sayfasındadır\n"
        f"    When kullanıcı boş veya çok kısa metin girer\n"
        f"    Then sistem uyarı mesajı gösterir\n"
        f"    And analiz kaydı oluşturulmaz"
    )


def run_qa_validation(raw_text: str) -> dict:
    """
    Gereksinim metnini QA kurallarına göre doğrular.
    Döndürür: {'valid': bool, 'message': str, 'score': int}
    """
    text = raw_text.strip()

    if len(text) < 10:
        return {
            'valid': False,
            'message': 'Gereksinim metni çok kısa. Lütfen daha ayrıntılı bir açıklama giriniz.',
            'score': 0,
        }

    score = 50
    warnings = []

    if len(text) >= 30:
        score += 20
    if len(text) >= 80:
        score += 10

    question_words = ['ne', 'neden', 'nasıl', 'kim', 'hangi', 'nerede']
    if any(w in text.lower() for w in question_words):
        score += 10

    actor_words = ['kullanıcı', 'sistem', 'yönetici', 'müşteri', 'analist']
    if any(w in text.lower() for w in actor_words):
        score += 10
    else:
        warnings.append('Aktör belirtilmemiş (kullanıcı, sistem vb.)')

    score = min(score, 100)

    if warnings:
        message = f"Gereksinim kabul edildi ancak iyileştirme önerileri var: {'; '.join(warnings)}"
    else:
        message = "Gereksinim açık, anlaşılır ve test edilebilir niteliktedir."

    return {'valid': True, 'message': message, 'score': score}


def estimate_story_points(raw_text: str) -> int:
    """Gereksinim karmaşıklığına göre story point tahmini yapar."""
    text = raw_text.strip()
    length = len(text)

    if length < 50:
        return 1
    elif length < 120:
        return 2
    elif length < 250:
        return 3
    elif length < 500:
        return 5
    else:
        return 8


def analyze_requirement(raw_text: str) -> dict:
    """Ana analiz fonksiyonu. Tüm servis çıktılarını birleştirir."""
    qa = run_qa_validation(raw_text)
    return {
        'bdd_output': generate_bdd_output(raw_text),
        'gherkin_output': generate_gherkin_output(raw_text),
        'qa_result': qa['message'],
        'qa_valid': qa['valid'],
        'story_point': estimate_story_points(raw_text),
    }
