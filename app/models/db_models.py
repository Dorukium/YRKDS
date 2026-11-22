"""SQLAlchemy/GeoAlchemy2 modelleri (sql/init.sql ile aynı şema)."""
from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class GridCell(Base):
    __tablename__ = "grid_cells"
    id = Column(Integer, primary_key=True)
    ilce = Column(String(50))
    mahalle = Column(String(100))
    geom = Column(Geometry("Polygon", srid=4326))
    dem_elevasyon = Column(Float)
    dem_egim = Column(Float)
    dem_twi = Column(Float)
    dem_hand = Column(Float)
    soil_clay_pct = Column(Float)
    soil_silt_pct = Column(Float)
    soil_sand_pct = Column(Float)
    soil_ph = Column(Float)
    insar_velocity_mm_yr = Column(Float)
    vs30 = Column(Float)
    zemin_sinifi = Column(String(10))
    pga_g = Column(Float)
    ss_g = Column(Float)
    s1_g = Column(Float)
    fay_mesafe_km = Column(Float)
    yass_m = Column(Float)
    akarsu_mesafe_m = Column(Float)
    taskin_100y = Column(Boolean)
    taskin_500y = Column(Boolean)
    taskin_yapi_yasagi = Column(Boolean)
    falez_cekme_mesafesi = Column(Boolean)
    fay_sakinim_bandi = Column(Boolean)
    afete_maruz_bolge = Column(Boolean)
    karst_alan = Column(Boolean)
    gecmis_taskin_sayisi = Column(Integer)
    bina_sayisi = Column(Integer)
    nufus = Column(Integer)
    veri_tamligi_pct = Column(Float)
    kaynak_dem = Column(Text)
    kaynak_toprak = Column(Text)


class ParcelQuery(Base):
    __tablename__ = "parcel_queries"
    id = Column(Integer, primary_key=True)
    query_time = Column(DateTime, server_default=func.now())
    geom = Column(Geometry("Polygon", srid=4326))
    parsel_id = Column(String(40))
    skor = Column(Float)
    bant = Column(String(20))
    karar = Column(Text)
    zb_puan = Column(Float)
    l_puan = Column(Float)
    s_puan = Column(Float)
    h_puan = Column(Float)
    f_puan = Column(Float)
    veto = Column(Boolean)
    veto_neden = Column(String(200))
    guven_skoru = Column(Float)
    sonuc_json = Column(Text)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    olay_turu = Column(String(50))
    tarih = Column(String(20))
    ilce = Column(String(50))
    mahalle = Column(String(100))
    lat = Column(Float)
    lon = Column(Float)
    buyukluk = Column(Float)
    etki = Column(String(500))
    kaynak_url = Column(Text)
    konum_guveni = Column(Float)
    dogrulama_etiketi = Column(Boolean, default=False)
    geom = Column(Geometry("Point", srid=4326))
