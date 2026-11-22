"""GET /api/report/{query_id}.pdf — WeasyPrint ile PDF rapor."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.config import TEMPLATES_DIR
from app.db import get_conn
from app.models.schemas import AnalyzeResponse

router = APIRouter()
_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)


@router.get("/api/query/{query_id}")
def query_json(query_id: int) -> dict[str, object]:
    """F5: sonuc JSON'unu derin bağlantı için döndürür."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT sonuc_json FROM parcel_queries WHERE id = %s", (query_id,))
        satir = cur.fetchone()
    if satir is None:
        raise HTTPException(404, "Sorgu bulunamadı")
    return AnalyzeResponse.model_validate(satir[0]).model_dump(mode="json")


@router.get("/api/report/{query_id}.pdf")
def report(query_id: int) -> Response:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT sonuc_json FROM parcel_queries WHERE id = %s", (query_id,))
        satir = cur.fetchone()
    if satir is None:
        raise HTTPException(404, "Sorgu bulunamadı")
    # JSONB psycopg tarafindan zaten dict olarak donusturulur.
    sonuc = AnalyzeResponse.model_validate(satir[0])
    html = _env.get_template("report_pdf.html").render(sonuc=sonuc)
    pdf = HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf()
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{sonuc.parsel_id}.pdf"'},
    )
