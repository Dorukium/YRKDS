"""0001 — yasal kısıt tablosu (idempotent).

İlk şema sql/init.sql ile oluşturulur; bu revision mevcut veritabanlarına
yasal kısıt tablosunu güvenli biçimde ekler (Faz B/F).
"""
from __future__ import annotations

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS legal_constraints (
            id SERIAL PRIMARY KEY,
            karar_no VARCHAR(50),
            karar_tarihi DATE,
            tur VARCHAR(50),
            ilce VARCHAR(50),
            mahalle VARCHAR(200),
            geom GEOMETRY(Polygon, 4326),
            kaynak_url TEXT,
            konum_guveni VARCHAR(20),
            aciklama TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_legal_geom ON legal_constraints USING GIST(geom);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS legal_constraints")
