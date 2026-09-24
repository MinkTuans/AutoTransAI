-- Frozen independently from 93200e6^ workflow_engine.py, before the glossary revision.
-- ORM defaults and onupdate are Python-only with no SQL defaults.
CREATE TABLE project_glossaries (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 project_id VARCHAR(36) NOT NULL,
 source_term VARCHAR(255) NOT NULL,
 translated_term VARCHAR(255) NOT NULL,
 term_type VARCHAR(50) NOT NULL,
 confidence FLOAT NOT NULL,
 source_context TEXT,
 approved BOOLEAN NOT NULL,
 created_at DATETIME NOT NULL,
 updated_at DATETIME NOT NULL,
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_project_glossaries_project_id ON project_glossaries(project_id);
CREATE TABLE project_terminology_memory (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 project_id VARCHAR(36) NOT NULL,
 source_term VARCHAR(255) NOT NULL,
 suggested_term VARCHAR(255) NOT NULL,
 term_type VARCHAR(50) NOT NULL,
 confidence FLOAT NOT NULL,
 needs_review BOOLEAN NOT NULL,
 source_context TEXT,
 created_at DATETIME NOT NULL,
 updated_at DATETIME NOT NULL,
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_project_terminology_memory_project_id ON project_terminology_memory(project_id);
