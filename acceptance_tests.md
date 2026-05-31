# Acceptance Tests — AI_RA İlk SaaS Prototipi

BDD acceptance testleri `features/requirement_analysis.feature` dosyasında tanımlanmış olup `behave` komutuyla çalıştırılır.

---

## AT-01 — Geçerli Gereksinim Analizi

**User Story**: US-1 (Gereksinim Girişi)

**Senaryo**:
```gherkin
Scenario: Geçerli gereksinim girdisi ile analiz oluşturma
  Given kullanıcı gereksinim giriş sayfasındadır
  When kullanıcı "Kullanıcılar e-posta ve şifre ile sisteme giriş yapabilmelidir" metnini girer
  And kullanıcı proje adı olarak "Test Projesi" girer
  And kullanıcı Analiz Et butonuna basar
  Then sistem bir gereksinim kaydı oluşturmalıdır
  And sistem BDD çıktısı göstermelidir
  And sistem Gherkin test senaryosu göstermelidir
```

**Beklenen Sonuç**: Oturumda analiz kaydı oluşur, sonuç sayfasına yönlendirilir (ORM/DB kaydı yok).

---

## AT-02 — Boş Girdi Reddi

**User Story**: US-4 (Girdi Doğrulama)

**Senaryo**:
```gherkin
Scenario: Boş gereksinim girdisi reddedilir
  Given kullanıcı gereksinim giriş sayfasındadır
  When kullanıcı boş metin gönderir
  Then sistem hata mesajı göstermelidir
  And analiz kaydı oluşturmamalıdır
```

**Beklenen Sonuç**: 200 OK döner (yönlendirme yok), form hata mesajı içerir, DB kaydı oluşmaz.

---

## AT-03 — Çok Kısa Girdi Reddi

**User Story**: US-4 (Girdi Doğrulama)

**Senaryo**:
```gherkin
Scenario: Çok kısa gereksinim girdisi reddedilir
  Given kullanıcı gereksinim giriş sayfasındadır
  When kullanıcı "Ekle" metnini girer
  And kullanıcı proje adı olarak "Test" girer
  And kullanıcı Analiz Et butonuna basar
  Then sistem hata mesajı göstermelidir
  And analiz kaydı oluşturmamalıdır
```

**Beklenen Sonuç**: Form doğrulama hatası, DB'de kayıt yok.

---

## AT-04 — BDD Given İçeriği

**User Story**: US-2 (BDD Çıktısı)

**Senaryo**:
```gherkin
Scenario: Analiz sonucunda BDD çıktısı Given içerir
  Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
  Then BDD çıktısında "Given" ifadesi bulunmalıdır
```

---

## AT-05 — BDD When İçeriği

**User Story**: US-2 (BDD Çıktısı)

**Senaryo**:
```gherkin
Scenario: Analiz sonucunda BDD çıktısı When içerir
  Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
  Then BDD çıktısında "When" ifadesi bulunmalıdır
```

---

## AT-06 — BDD Then İçeriği

**User Story**: US-2 (BDD Çıktısı)

**Senaryo**:
```gherkin
Scenario: Analiz sonucunda BDD çıktısı Then içerir
  Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
  Then BDD çıktısında "Then" ifadesi bulunmalıdır
```

---

## AT-07 — Gherkin Feature İçeriği

**User Story**: US-3 (Gherkin Senaryosu)

**Senaryo**:
```gherkin
Scenario: Analiz sonucunda Gherkin Feature satırı bulunur
  Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
  Then Gherkin çıktısında "Feature:" ifadesi bulunmalıdır
```

---

## AT-08 — Gherkin Scenario İçeriği

**User Story**: US-3 (Gherkin Senaryosu)

**Senaryo**:
```gherkin
Scenario: Analiz sonucunda Gherkin Scenario satırı bulunur
  Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
  Then Gherkin çıktısında "Scenario:" ifadesi bulunmalıdır
```

---

## Çalıştırma

```bash
behave
```

Tüm senaryolar geçmeli, başarısız senaryo olmamalıdır.

---

## Gereksinim İzlenebilirliği

| Acceptance Test | User Story | Fonksiyonel Gereksinim |
|----------------|-----------|----------------------|
| AT-01 | US-1 | FR-ST-02, FR-ST-04, FR-ST-11 |
| AT-02 | US-4 | FR-ST-09, NFR-ST-01 |
| AT-03 | US-4 | FR-ST-09 |
| AT-04 | US-2 | FR-ST-05 |
| AT-05 | US-2 | FR-ST-05 |
| AT-06 | US-2 | FR-ST-05 |
| AT-07 | US-3 | FR-ST-06 |
| AT-08 | US-3 | FR-ST-06 |
