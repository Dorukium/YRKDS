# ADR-0010 — Senaryo anahtarında S bileşeni

- Tarih: 2026-11-22
- Durum: Kabul

## Bağlam
F4, Bugün / 2050 SSP2-4.5 / 2050 SSP5-8.5 senaryolarında F ve S bileşenlerinin
etkilenmesini istiyor. 3.10'da yağış değişimi (-%15/-%22) ve sıcaklık artışı
(+2.5/+3.8 °C) var.

## Karar
F çarpanı doğrudan CMIP6 yağış değişiminden türetilir: 1 + |Δyağış|/100.
S için oturma/InSAR ölçümü olmadığından (D1/ADR-0009) bilimsel olarak
savunulabilir bir çarpan yoktur; S **nötr (1.0)** bırakılır ve kullanıcıya
"veri yok" uyarısı gösterilir. Bu, uydurma katsayı üretmekten kaçınmak içindir.

## Sonuçlar
Senaryo değişince skor değişir (F üzerinden); rozet "Tahmin" olarak gösterilir.
S için iklim etkisi iddia edilmez.
