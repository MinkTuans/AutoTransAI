-- Literal pre-width VideoThumbnail table from the historical ORM.
CREATE TABLE projects (id VARCHAR(36) NOT NULL PRIMARY KEY);
CREATE TABLE video_translation_jobs (id VARCHAR(36) NOT NULL PRIMARY KEY);
CREATE TABLE video_assets (id VARCHAR(36) NOT NULL PRIMARY KEY);
CREATE TABLE video_thumbnails (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 project_id VARCHAR(36),
 job_id VARCHAR(36),
 asset_id VARCHAR(36),
 source_title VARCHAR(255) NOT NULL,
 source_description TEXT,
 selected_style VARCHAR(50) NOT NULL,
 custom_instruction TEXT,
 ai_analysis_json TEXT,
 generated_prompt TEXT,
 provider VARCHAR(50) NOT NULL,
 model VARCHAR(100) NOT NULL,
 r2_key VARCHAR(500),
 thumbnail_url TEXT,
 width INTEGER NOT NULL,
 height INTEGER NOT NULL,
 aspect_ratio VARCHAR(20) NOT NULL,
 status VARCHAR(30) NOT NULL,
 error_message TEXT,
 is_active BOOLEAN NOT NULL,
 created_at DATETIME NOT NULL,
 updated_at DATETIME NOT NULL,
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
 FOREIGN KEY(job_id) REFERENCES video_translation_jobs(id) ON DELETE CASCADE,
 FOREIGN KEY(asset_id) REFERENCES video_assets(id) ON DELETE CASCADE
);
CREATE INDEX ix_video_thumbnails_project_id ON video_thumbnails(project_id);
CREATE INDEX ix_video_thumbnails_job_id ON video_thumbnails(job_id);
CREATE INDEX ix_video_thumbnails_asset_id ON video_thumbnails(asset_id);
