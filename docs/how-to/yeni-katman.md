# Nasıl yapılır: Yeni katman ekleme

1. `app/data_pipeline/download_<ad>.py` ile ham veriyi indir; URL + erişim
   tarihi + SHA256'yı `data/raw/manifest.json` veya `research_manifest.json`'a ekle.
2. `process_grid.py` içinde 25 m grid'e türet; kaynak etiketini kanıt zincirine ekle.
3. `sql/init.sql` ve yeni `sql/migrations/00X_*.sql` ile şemayı güncelle.
4. Skor formülüne girdi ekliyorsan Python ve Rust'u birlikte değiştir
   (`tests/test_parity.py` zorunlu).
5. K3: eksik değerleri 0/ortalama ile doldurma; `NULL` bırak ve güven cezası uygula.
