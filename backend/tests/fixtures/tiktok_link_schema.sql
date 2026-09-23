-- Frozen from 1ebccbb: published 20260915_add_tiktok_accounts.py.
CREATE TABLE tiktok_accounts (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 open_id VARCHAR(128) NOT NULL,
 display_name VARCHAR(200) DEFAULT 'TikTok' NOT NULL,
 avatar_url VARCHAR(500),
 credentials_json TEXT NOT NULL,
 is_active BOOLEAN DEFAULT 1 NOT NULL,
 created_at DATETIME,
 updated_at DATETIME
);
CREATE UNIQUE INDEX ix_tiktok_accounts_open_id ON tiktok_accounts (open_id);
