# User Stories — AI_RA İlk SaaS Prototipi

---

## User Story 1 — Gereksinim Girişi

**Başlık**: Yazılım fikri girme

**Kart**:
> Bir **iş analisti** olarak, yazılım fikrimi sisteme girmek istiyorum;
> böylece sistem bu fikri yapılandırılmış gereksinime dönüştürebilsin.

**Acceptance Criteria**:
- [ ] Kullanıcı proje adı girebilmelidir.
- [ ] Kullanıcı boş olmayan bir gereksinim metni girebilmelidir (en az 10 karakter).
- [ ] Sistem formu POST ile almalı ve girdiyi veritabanına kaydetmelidir.
- [ ] Sistem kullanıcıyı analiz sonuç sayfasına yönlendirmelidir.

**Bağlı Gereksinim**: FR-ST-02 (Metin Girişi), FR-ST-04 (Gereksinim Analizi)

---

## User Story 2 — BDD Çıktısı Görüntüleme

**Başlık**: BDD formatında gereksinim çıktısı

**Kart**:
> Bir **kullanıcı** olarak, sistemin BDD formatında çıktı üretmesini istiyorum;
> böylece gereksinimi Given-When-Then yapısıyla görebileyim.

**Acceptance Criteria**:
- [ ] Sonuç sayfasında **Given** bölümü görünmelidir.
- [ ] Sonuç sayfasında **When** bölümü görünmelidir.
- [ ] Sonuç sayfasında **Then** bölümü görünmelidir.
- [ ] BDD çıktısı kullanıcının girdiği metni yansıtmalıdır.

**Bağlı Gereksinim**: FR-ST-05 (BDD Çıktısı Üretimi)

---

## User Story 3 — Gherkin Senaryosu

**Başlık**: Test otomasyonu için Gherkin çıktısı

**Kart**:
> Bir **test uzmanı** olarak, sistemin Gherkin senaryosu üretmesini istiyorum;
> böylece çıktı test otomasyonuna temel oluşturabilsin.

**Acceptance Criteria**:
- [ ] Çıktıda `Feature:` satırı bulunmalıdır.
- [ ] Çıktıda `Scenario:` satırı bulunmalıdır.
- [ ] Çıktıda `Given`, `When`, `Then` ifadeleri bulunmalıdır.
- [ ] Gherkin çıktısı `<pre>` bloğunda okunabilir şekilde gösterilmelidir.

**Bağlı Gereksinim**: FR-ST-06 (Gherkin Test Senaryosu Üretimi)

---

## User Story 4 — Girdi Doğrulama ve Uyarı

**Başlık**: Eksik veya kısa girdi uyarısı

**Kart**:
> Bir **kullanıcı** olarak, eksik veya çok kısa girdi verdiğimde sistemin beni uyarmasını istiyorum;
> böylece daha anlamlı gereksinim girebileyim.

**Acceptance Criteria**:
- [ ] Boş girdi kabul edilmemelidir.
- [ ] 10 karakterden kısa girdi için açıklayıcı hata mesajı gösterilmelidir.
- [ ] Hata mesajı sayfa yenilemeden aynı formda görünmelidir.
- [ ] Geçerli girdi analiz edilerek sonuç sayfasına yönlendirilmelidir.

**Bağlı Gereksinim**: FR-ST-09 (Ek Bilgi Talebi), NFR-ST-01 (Kullanılabilirlik)

---

## User Story 5 — Geçmiş Analizleri Görüntüleme

**Başlık**: Geçmiş gereksinim listesi

**Kart**:
> Bir **kullanıcı** olarak, önceki gereksinim analizlerimi listelemek istiyorum;
> böylece geçmiş çalışmalarıma hızla ulaşabileyim.

**Acceptance Criteria**:
- [ ] `/requirements/` URL'si tüm kayıtlı gereksinimleri listelemelidir.
- [ ] Liste; proje adı, durum, tarih ve story point bilgisini içermelidir.
- [ ] Her satırda "Görüntüle" linki ile detay sayfasına gidilebilmelidir.
- [ ] Hiç kayıt yoksa anlamlı bir boş durum mesajı gösterilmelidir.

**Bağlı Gereksinim**: FR-ST-11 (Gereksinim Kaydı)

---

## User Story 6 — Story Point Tahmini

**Başlık**: Otomatik story point tahmini

**Kart**:
> Bir **ürün yöneticisi** olarak, her gereksinim için otomatik story point tahmini görmek istiyorum;
> böylece sprint planlamasına hızlı girdi elde edebileyim.

**Acceptance Criteria**:
- [ ] Analiz sonuç sayfasında bir story point değeri görünmelidir.
- [ ] Story point değeri pozitif bir tam sayı olmalıdır.
- [ ] Kısa gereksinimler düşük SP, uzun gereksinimler yüksek SP almalıdır.

**Bağlı Gereksinim**: FR-ST-04 (Gereksinim Analizi)
