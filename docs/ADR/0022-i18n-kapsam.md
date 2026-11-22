# ADR-0022 — İngilizce arayüz kapsamı (D4)

- Tarih: 2026-11-22
- Durum: Kabul (kısmi)

TR/EN sözlükleri (`frontend/locales/*.json`), dil değiştirici ve `data-i18n`
mekanizması tüm sayfalarda çalışır. Statik menü/alt bilgi/sekme etiketleri
çevrilir. Dinamik API içerikleri (kanıt değerleri, öneri metinleri, ADR
açıklamaları) Türkçe üretilmeye devam eder; bunların çevrilmesi ayrı bir
i18n veri katmanı gerektirir. Kullanıcıya yanlış çevrilmiş kesinlik
sunmamak için dinamik metinler çevrilmemiş olarak bırakılmıştır.
