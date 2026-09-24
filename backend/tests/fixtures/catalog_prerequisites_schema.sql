-- Literal pre-catalog provider/settings subset from 08ea050^.
CREATE TABLE providers (
 id VARCHAR(50) NOT NULL PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 provider_type VARCHAR(20) NOT NULL,
 quota_type VARCHAR(50) NOT NULL,
 quota_limit INTEGER,
 quota_used_local INTEGER NOT NULL,
 configured BOOLEAN NOT NULL,
 api_key_set BOOLEAN NOT NULL,
 last_verified DATETIME,
 capabilities TEXT,
 supported BOOLEAN NOT NULL,
 is_custom BOOLEAN NOT NULL,
 enabled BOOLEAN NOT NULL,
 website_url VARCHAR(255),
 doc_url VARCHAR(255),
 base_url VARCHAR(255)
);
CREATE TABLE ai_function_configs (
 function_id VARCHAR(50) NOT NULL PRIMARY KEY,
 function_name VARCHAR(100) NOT NULL,
 capability VARCHAR(50) NOT NULL,
 primary_provider_id VARCHAR(50) NOT NULL,
 model_id VARCHAR(100) NOT NULL,
 fallback_enabled BOOLEAN NOT NULL,
 fallback_provider_id VARCHAR(50),
 updated_at DATETIME NOT NULL
);
CREATE TABLE ai_models (
 id VARCHAR(100) NOT NULL PRIMARY KEY,
 provider_id VARCHAR(50) NOT NULL,
 model_name VARCHAR(100) NOT NULL,
 capabilities TEXT NOT NULL,
 is_default BOOLEAN NOT NULL,
 is_custom BOOLEAN NOT NULL,
 enabled BOOLEAN NOT NULL,
 description TEXT,
 created_at DATETIME NOT NULL
);
