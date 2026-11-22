-- Idempotent migration: mevcut veritabanina yasal kisit tablosunu ekler.
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
