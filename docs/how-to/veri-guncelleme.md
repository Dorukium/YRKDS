# Nasıl yapılır: Veriyi güncelleme

```bash
uv run python -m app.data_pipeline.download_dem
uv run python -m app.data_pipeline.download_soil
uv run python -m app.data_pipeline.download_osm
uv run python -m app.data_pipeline.process_grid
uv run python -m app.data_pipeline.load_postgis
```

Ardından `make gate-all` çalıştır. Eşik değiştirmek için: yalnızca kalibrasyon
setinde değiştir, commit'le dondur; doğrulama setinde eşik kaydırma yasaktır
(K4).
