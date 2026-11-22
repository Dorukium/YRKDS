# ADR-0016 — USGS Vs30 sayısal erişimi (A6)

- Tarih: 2026-11-22
- Durum: Kabul

USGS `eq/vs30_mosaic/MapServer/export` uç noktası `format=tiff` istemesine
rağmen PNG görüntüsü döndürdü (280×180, SHA256
`7a40b57fe24af5502b17336cbd1d3b7388c006ea7f5ee679be99e968bf2cdbe4`).
Görüntüden sayısal Vs30 çıkarılması güvenilir değildir. Bu nedenle sayısal
çapraz kontrol yapılmaz; GEM/Proje sapma raporu (ADR-0008) korunur, PNG yalnızca
görsel referans olarak `data/raw/usgs_vs30_export.png` içinde saklanır.
