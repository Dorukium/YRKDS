"""V5 FAZ 5 — Zenodo DOI yayını ve CITATION.cff üretimi (ADR-0023).

Kullanım:
    uv run python -m app.data_pipeline.publish --citation     # token'suz, sadece CITATION.cff
    ZENODO_TOKEN=... uv run python -m app.data_pipeline.publish  # gerçek yayın

Dürüstlük (K3): token yoksa DOI ÜRETİLMEZ, "kimlik_yok" döner; README'ye
sahte DOI yazılmaz. Zenodo sandboxesı ZENODO_SANDBOX=true ile seçilir.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
API = "https://sandbox.zenodo.org/api" if os.getenv("ZENODO_SANDBOX", "").lower() == "true" \
    else "https://zenodo.org/api"

CITATION_TEMPLATE = """cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "YRKDS — Antalya Yatırım Riski Karar Destek Sistemi"
abstract: >-
  Antalya'nın üç merkez ilçesinde parsel bazlı afet riski skorlaması için
  deterministik, kanıtlı karar destek sistemi. TÜBİTAK 2204-A kapsamında
  geliştirilmiştir.
authors:
  - family-names: YRKDS Araştırma Ekibi
    name-particle: ""
version: 5.0.0
date-released: {tarih}
license: MIT
repository-code: https://github.com/YRKDS/YRKDS
keywords:
  - disaster risk
  - Antalya
  - deterministic scoring
  - GIS
  - InSAR
doi: {doi}
"""


def citation_yaz(doi: str = "10.5281/zenodo.PENDING") -> Path:
    """CITATION.cff üretir. DOI henüz yoksa PENDING olarak bırakılır (uydurma yok)."""
    hedef = ROOT / "CITATION.cff"
    hedef.write_text(
        CITATION_TEMPLATE.format(tarih=date.today().isoformat(), doi=doi),
        encoding="utf-8",
    )
    return hedef


def _guncelle(dosya: Path, doi: str) -> None:
    if not dosya.exists():
        return
    metin = dosya.read_text(encoding="utf-8")
    satir = f"**Zenodo DOI:** [{doi}](https://doi.org/{doi})\n"
    if doi in metin:
        return
    if "**Zenodo DOI:**" in metin:
        satirlar = [
            (satir if s.startswith("**Zenodo DOI:**") else s)
            for s in metin.splitlines()
        ]
        metin = "\n".join(satirlar) + "\n"
    else:
        metin = metin.rstrip() + "\n\n" + satir
    dosya.write_text(metin, encoding="utf-8")


def publish(dry_run: bool = False) -> dict[str, Any]:
    token = os.getenv("ZENODO_TOKEN", "").strip()
    if not token:
        citation_yaz()
        return {
            "durum": "kimlik_yok",
            "not": "ZENODO_TOKEN .env'de yok. CITATION.cff PENDING ile üretildi; sahte DOI yazılmadı.",
            "komut": "https://zenodo.org/account/settings/applications/tokens/new/",
        }

    basliklar = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(
            f"{API}/deposit/depositions",
            params={"access_token": token},
            json={},
            headers=basliklar,
            timeout=60,
        )
        r.raise_for_status()
        dep = r.json()
        dep_id = dep["id"]
        bucket = dep["links"]["bucket"]

        dosyalar = [ROOT / "docs" / "sbom.json", ROOT / "CHANGELOG.md"]
        for dosya in dosyalar:
            if dosya.exists():
                with dosya.open("rb") as fh:
                    requests.put(
                        f"{bucket}/{dosya.name}", data=fh,
                        params={"access_token": token}, timeout=120,
                    ).raise_for_status()

        meta = {
            "metadata": {
                "title": "YRKDS — Antalya Yatırım Riski Karar Destek Sistemi",
                "upload_type": "software",
                "creators": [{"name": "YRKDS Araştırma Ekibi"}],
                "description": "TÜBİTAK 2204-A kapsamında geliştirilen deterministik parsel bazlı afet riski karar destek sistemi.",
                "version": "5.0.0",
                "license": "mit",
                "keywords": ["disaster risk", "Antalya", "GIS", "InSAR"],
            }
        }
        requests.put(
            f"{API}/deposit/depositions/{dep_id}",
            params={"access_token": token}, json=meta, headers=basliklar, timeout=60,
        ).raise_for_status()

        if dry_run:
            return {"durum": "sandbox_taslak", "deposition": dep_id,
                    "not": "Yayınlanmadı; DOI alınmadı."}

        pub = requests.post(
            f"{API}/deposit/depositions/{dep_id}/actions/publish",
            params={"access_token": token}, headers=basliklar, timeout=120,
        )
        pub.raise_for_status()
        doi = str(pub.json().get("doi", ""))
        if not doi:
            return {"durum": "doi_yok", "not": "Zenodo yayın yanıtında DOI bulunamadı."}

        citation_yaz(doi)
        _guncelle(ROOT / "README.md", doi)
        _guncelle(ROOT / "docs" / "tubitak_rapor" / "01_ozet.md", doi)
        return {"durum": "ok", "doi": doi, "deposition": dep_id,
                "url": f"https://doi.org/{doi}", "api": API}
    except Exception as exc:
        return {"durum": "hata", "hata": type(exc).__name__, "not": str(exc)[:300]}


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--citation", action="store_true", help="Sadece CITATION.cff üret")
    parser.add_argument("--dry-run", action="store_true", help="Sandbox'ta taslak oluştur, yayınlama")
    args = parser.parse_args()
    if args.citation:
        print(json.dumps({"durum": "ok", "dosya": str(citation_yaz())}, ensure_ascii=False))
    else:
        print(json.dumps(publish(args.dry_run), ensure_ascii=False, indent=2))
        sys.exit(0)
