-- Tekrarlanan karar kayıtlarını temizle (düşük id'li olanı koru), sonra benzersizlik.
DELETE FROM legal_constraints a USING legal_constraints b
 WHERE a.karar_no = b.karar_no AND a.id > b.id;
ALTER TABLE legal_constraints ALTER COLUMN konum_guveni TYPE VARCHAR(64);
CREATE UNIQUE INDEX IF NOT EXISTS idx_legal_karar_no ON legal_constraints(karar_no);
