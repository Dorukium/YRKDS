-- V2 katmanları: SoilGrids WCS soc, GEM araştırma PGA, kıyı zonları
ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS soil_soc FLOAT;
ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS pga_gem_arastirma FLOAT;
ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS kiyi_2m BOOLEAN;
ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS kiyi_5m BOOLEAN;
