-- Frozen four-table subset of 2728d1a:backend/app/models/{project,segment,video_translator}.py.
-- ORM Python defaults are deliberately not SQL server defaults.
CREATE TABLE projects (
 id VARCHAR(36) NOT NULL PRIMARY KEY, title VARCHAR(200) NOT NULL,
 script_raw TEXT NOT NULL, workflow_mode VARCHAR(20) NOT NULL,
 workflow_status VARCHAR(30) NOT NULL, audio_provider_id VARCHAR(50),
 video_provider_id VARCHAR(50), voice_id VARCHAR(100), voice_name VARCHAR(100),
 sync_strategy VARCHAR(30) NOT NULL, error_message TEXT,
 created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL
);
CREATE TABLE video_assets (
 id VARCHAR(36) NOT NULL PRIMARY KEY, source_type VARCHAR(20) NOT NULL,
 source_url TEXT, source_domain VARCHAR(100), title VARCHAR(255) NOT NULL,
 original_filename VARCHAR(255), file_path VARCHAR(500) NOT NULL,
 mime_type VARCHAR(50), file_size INTEGER, duration FLOAT, width INTEGER,
 height INTEGER, audio_available BOOLEAN NOT NULL, status VARCHAR(30) NOT NULL,
 error_message TEXT, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL
);
CREATE TABLE segments (
 id INTEGER NOT NULL PRIMARY KEY, project_id VARCHAR(36) NOT NULL,
 segment_number INTEGER NOT NULL, text_content TEXT NOT NULL, char_count INTEGER NOT NULL,
 audio_status VARCHAR(20) NOT NULL, audio_duration FLOAT, audio_file_path VARCHAR(500),
 audio_error_message TEXT, video_status VARCHAR(20) NOT NULL, video_duration FLOAT,
 video_file_path VARCHAR(500), video_error_message TEXT, video_error_details TEXT,
 target_duration FLOAT, sync_strategy_used VARCHAR(30), merged_file_path VARCHAR(500),
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_segments_project_id ON segments(project_id);
CREATE TABLE video_translation_jobs (
 id VARCHAR(36) NOT NULL PRIMARY KEY, asset_id VARCHAR(36) NOT NULL,
 source_language VARCHAR(20) NOT NULL, detected_language VARCHAR(20),
 target_language VARCHAR(20) NOT NULL, audio_provider_id VARCHAR(50),
 voice_id VARCHAR(100), voice_name VARCHAR(100), original_audio_mode VARCHAR(20) NOT NULL,
 status VARCHAR(30) NOT NULL, progress_pct FLOAT NOT NULL, current_step VARCHAR(100) NOT NULL,
 output_video_path VARCHAR(500), error_message TEXT,
 created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL,
 FOREIGN KEY(asset_id) REFERENCES video_assets(id) ON DELETE CASCADE
);
CREATE INDEX ix_video_translation_jobs_asset_id ON video_translation_jobs(asset_id);
