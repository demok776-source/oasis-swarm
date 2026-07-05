-- Migration script: Create contacts table for OASIS App-Tier
-- Destination: PostgreSQL 15 (primary-db)

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Index for searching contacts by email
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
