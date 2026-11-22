-- Faz: kimlik doğrulama ve denetim (idempotent)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst' CHECK (role IN ('analyst','admin')),
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ DEFAULT NOW(),
    username VARCHAR(80),
    action VARCHAR(60) NOT NULL,
    ip VARCHAR(64),
    detail JSONB DEFAULT '{}'::jsonb
);
ALTER TABLE parcel_queries ADD COLUMN IF NOT EXISTS username VARCHAR(80);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts DESC);
