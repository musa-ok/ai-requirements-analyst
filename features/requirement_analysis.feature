Feature: Gereksinim analizi olusturma
  Bir iş analisti olarak yazılım fikrimi sisteme girmek istiyorum;
  böylece sistem bu fikri BDD formatında yapılandırılmış gereksinime dönüştürsün.

  Scenario: Geçerli gereksinim girdisi ile analiz oluşturma
    Given kullanıcı gereksinim giriş sayfasındadır
    When kullanıcı "Kullanıcılar e-posta ve şifre ile sisteme giriş yapabilmelidir" metnini girer
    And kullanıcı proje adı olarak "Test Projesi" girer
    And kullanıcı Analiz Et butonuna basar
    Then sistem bir gereksinim kaydı oluşturmalıdır
    And sistem BDD çıktısı göstermelidir
    And sistem Gherkin test senaryosu göstermelidir

  Scenario: Boş gereksinim girdisi reddedilir
    Given kullanıcı gereksinim giriş sayfasındadır
    When kullanıcı boş metin gönderir
    Then sistem hata mesajı göstermelidir
    And analiz kaydı oluşturmamalıdır

  Scenario: Çok kısa gereksinim girdisi reddedilir
    Given kullanıcı gereksinim giriş sayfasındadır
    When kullanıcı "Ekle" metnini girer
    And kullanıcı proje adı olarak "Test" girer
    And kullanıcı Analiz Et butonuna basar
    Then sistem hata mesajı göstermelidir
    And analiz kaydı oluşturmamalıdır

  Scenario: Analiz sonucunda BDD çıktısı Given içerir
    Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
    Then BDD çıktısında "Given" ifadesi bulunmalıdır

  Scenario: Analiz sonucunda BDD çıktısı When içerir
    Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
    Then BDD çıktısında "When" ifadesi bulunmalıdır

  Scenario: Analiz sonucunda BDD çıktısı Then içerir
    Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
    Then BDD çıktısında "Then" ifadesi bulunmalıdır

  Scenario: Analiz sonucunda Gherkin Feature satırı bulunur
    Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
    Then Gherkin çıktısında "Feature:" ifadesi bulunmalıdır

  Scenario: Analiz sonucunda Gherkin Scenario satırı bulunur
    Given kullanıcı geçerli bir gereksinim analizi tamamlamıştır
    Then Gherkin çıktısında "Scenario:" ifadesi bulunmalıdır
