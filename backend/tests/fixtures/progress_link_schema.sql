-- Frozen from eec0ef5 (ead6ad9 parent), backend/app/models/video_editor.py
-- and workflow_engine.py. Mapped non-Optional fields are NOT NULL.
-- Python defaults are not SQL defaults. No current application imports.
CREATE TABLE youtube_channels (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 channel_name VARCHAR(200) NOT NULL,
 channel_id VARCHAR(100),
 credentials_json TEXT NOT NULL,
 is_active BOOLEAN NOT NULL,
 created_at DATETIME NOT NULL
);
CREATE TABLE youtube_publications (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 job_id VARCHAR(36),
 channel_id VARCHAR(36) NOT NULL,
 title VARCHAR(100) NOT NULL,
 description TEXT NOT NULL,
 tags_json TEXT,
 category_id VARCHAR(20) NOT NULL,
 thumbnail_path VARCHAR(500),
 privacy_status VARCHAR(20) NOT NULL,
 scheduled_publish_time DATETIME,
 youtube_video_id VARCHAR(100),
 youtube_url TEXT,
 status VARCHAR(20) NOT NULL,
 error_message TEXT,
 created_at DATETIME NOT NULL,
 updated_at DATETIME NOT NULL,
 FOREIGN KEY(channel_id) REFERENCES youtube_channels(id) ON DELETE CASCADE
);
CREATE INDEX ix_youtube_publications_job_id ON youtube_publications(job_id);
CREATE TABLE workflow_executions (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 project_id VARCHAR(36) NOT NULL,
 workflow_type VARCHAR(50) NOT NULL,
 status VARCHAR(30) NOT NULL,
 current_stage VARCHAR(50),
 current_step VARCHAR(50),
 context_data JSON,
 error_message TEXT,
 started_at DATETIME,
 updated_at DATETIME NOT NULL,
 completed_at DATETIME,
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_workflow_executions_project_id ON workflow_executions(project_id);
CREATE TABLE workflow_stage_executions (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 workflow_execution_id VARCHAR(36) NOT NULL,
 stage_name VARCHAR(50) NOT NULL,
 status VARCHAR(30) NOT NULL,
 error TEXT,
 qc_report JSON,
 retry_count INTEGER NOT NULL,
 started_at DATETIME,
 completed_at DATETIME,
 created_at DATETIME NOT NULL,
 FOREIGN KEY(workflow_execution_id) REFERENCES workflow_executions(id) ON DELETE CASCADE
);
CREATE INDEX ix_workflow_stage_executions_workflow_execution_id ON workflow_stage_executions(workflow_execution_id);
