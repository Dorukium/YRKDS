"""TÜBİTAK rapor bölümlerini tek PDF'e birleştirir (K1 kanıt çıktısı).

Komut: uv run python scripts/build_report.py
Çıktı: docs/tubitak_rapor/YRKDS_TUBITAK_RAPORU.pdf
"""
from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
BOLUMLER = [
    "01_ozet.md", "02_giris.md", "03_yontem.md",
    "04_bulgular.md", "05_sonuc.md", "06_kaynakca.md",
]
CIKTİ = ROOT / "docs" / "tubitak_rapor" / "YRKDS_TUBITAK_RAPORU.pdf"

CSS = """
@page { size: A4; margin: 20mm 18mm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10.5pt; line-height: 1.5; color: #16202e; }
h1 { font-size: 18pt; color: #0F766E; border-bottom: 2px solid #0F766E; padding-bottom: 6px; }
h2 { font-size: 14pt; color: #0F766E; margin-top: 18px; }
h3 { font-size: 11.5pt; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
th, td { border: 1px solid #cbd5e1; padding: 5px 7px; text-align: left; }
th { background: #f1f5f9; }
code { background: #f1f5f9; padding: 1px 3px; font-size: 9pt; }
.bolum { page-break-before: always; }
.kapak { text-align: center; page-break-after: always; margin-top: 55mm; }
.kapak h1 { font-size: 26pt; border: 0; }
.kapak p { font-size: 13pt; color: #475569; }
"""


def main() -> None:
    md = MarkdownIt("commonmark").enable("table")
    klasor = ROOT / "docs" / "tubitak_rapor"
    parcalar = [
        "<div class='kapak'><h1>YRKDS</h1>"
        "<p>Antalya Yatırım Riski Karar Destek Sistemi</p>"
        "<p>TÜBİTAK 2204-A — Araştırma Raporu, v5.0.0</p>"
        "<p>DOI: <a href='https://doi.org/10.5281/zenodo.24449066'>"
        "10.5281/zenodo.24449066</a></p>"
        "<p>Kasım 2026</p></div>"
    ]
    for ad in BOLUMLER:
        icerik = (klasor / ad).read_text(encoding="utf-8")
        parcalar.append(f"<div class='bolum'>{md.render(icerik)}</div>")
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(parcalar)}</body></html>"
    HTML(string=html, base_url=str(klasor)).write_pdf(str(CIKTİ))
    print(f"PDF: {CIKTİ} ({CIKTİ.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
