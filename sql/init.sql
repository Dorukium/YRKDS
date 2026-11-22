-- YRKDS PostGIS şeması. Tüm geometriler EPSG:4326.
CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS parcel_queries CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS grid_cells CASCADE;

CREATE TABLE grid_cells (
    id SERIAL PRIMARY KEY,
    ilce VARCHAR(50),
    mahalle VARCHAR(100),
    geom GEOMETRY(Polygon, 4326),
    dem_elevasyon FLOAT,
    dem_egim FLOAT,
    dem_twi FLOAT,
    dem_hand FLOAT,
    soil_clay_pct FLOAT,
    soil_silt_pct FLOAT,
    soil_sand_pct FLOAT,
    soil_ph FLOAT,
    soil_soc FLOAT,
    insar_velocity_mm_yr FLOAT,
    pga_gem_arastirma FLOAT,
    kiyi_2m BOOLEAN,
    kiyi_5m BOOLEAN,
    vs30 FLOAT,
    zemin_sinifi VARCHAR(10),
    pga_g FLOAT,
    ss_g FLOAT,
    s1_g FLOAT,
    fay_mesafe_km FLOAT,
    yass_m FLOAT,
    akarsu_mesafe_m FLOAT,
    taskin_100y BOOLEAN,
    taskin_500y BOOLEAN,
    taskin_yapi_yasagi BOOLEAN,
    falez_cekme_mesafesi BOOLEAN,
    fay_sakinim_bandi BOOLEAN,
    afete_maruz_bolge BOOLEAN,
    karst_alan BOOLEAN,
    gecmis_taskin_sayisi INT,
    bina_sayisi INT,
    nufus INT,
    veri_tamligi_pct FLOAT,
    kaynak_dem TEXT,
    kaynak_toprak TEXT
);
CREATE INDEX idx_grid_geom ON grid_cells USING GIST(geom);
CREATE INDEX idx_grid_ilce ON grid_cells(ilce);

CREATE TABLE parcel_queries (
    id SERIAL PRIMARY KEY,
    query_time TIMESTAMP DEFAULT NOW(),
    geom GEOMETRY(Polygon, 4326),
    parsel_id VARCHAR(40),
    skor FLOAT,
    bant VARCHAR(20),
    karar TEXT,
    zb_puan FLOAT, l_puan FLOAT, s_puan FLOAT, h_puan FLOAT, f_puan FLOAT,
    veto BOOLEAN,
    veto_neden VARCHAR(200),
    guven_skoru FLOAT,
    sonuc_json JSONB
);
CREATE INDEX idx_parcel_geom ON parcel_queries USING GIST(geom);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    olay_turu VARCHAR(50),
    tarih DATE,
    ilce VARCHAR(50),
    mahalle VARCHAR(100),
    lat FLOAT,
    lon FLOAT,
    buyukluk FLOAT,
    etki VARCHAR(500),
    kaynak_url TEXT,
    konum_guveni FLOAT,
    dogrulama_etiketi BOOLEAN DEFAULT FALSE,
    geom GEOMETRY(Point, 4326)
);
CREATE INDEX idx_events_geom ON events USING GIST(geom);
CREATE INDEX idx_events_tur ON events(olay_turu);

-- Faz B: Resmî Gazete kaynaklı yasal kısıtlar
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
