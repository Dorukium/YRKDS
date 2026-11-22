-- A1: ARIA S1 GUNW hızı ve proxy geçerlilik maskesi
ALTER TABLE grid_cells ADD COLUMN IF NOT EXISTS insar_proxy BOOLEAN;
