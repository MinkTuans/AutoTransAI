-- Independently transcribed from published 8ae030a and its pre-timeline models.
CREATE TABLE speaker_voice_mappings (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 project_id VARCHAR(36) NOT NULL,
 speaker_id VARCHAR(100) NOT NULL,
 speaker_name VARCHAR(100),
 voice_provider VARCHAR(50) NOT NULL,
 voice_id VARCHAR(100) NOT NULL,
 voice_settings JSON,
 created_at DATETIME NOT NULL,
 updated_at DATETIME NOT NULL,
 character_id VARCHAR(36),
 confidence FLOAT NOT NULL DEFAULT '0',
 needs_review BOOLEAN NOT NULL DEFAULT 0,
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_speaker_voice_mappings_project_id ON speaker_voice_mappings(project_id);
CREATE INDEX ix_speaker_voice_mappings_character_id ON speaker_voice_mappings(character_id);
CREATE TABLE video_translation_segments (
 id INTEGER NOT NULL PRIMARY KEY,
 job_id VARCHAR(36) NOT NULL,
 segment_number INTEGER NOT NULL,
 start_time FLOAT NOT NULL,
 end_time FLOAT NOT NULL,
 original_text TEXT NOT NULL,
 translated_text TEXT NOT NULL,
 tts_audio_path VARCHAR(500),
 tts_audio_duration FLOAT,
 synced_audio_path VARCHAR(500),
 status VARCHAR(30) NOT NULL,
 speaker_id VARCHAR(100),
 character_id VARCHAR(36),
 voice_provider VARCHAR(50),
 voice_id VARCHAR(100),
 original_start FLOAT,
 original_end FLOAT,
 scheduled_start FLOAT,
 scheduled_end FLOAT,
 tts_duration FLOAT,
 overlap_with JSON,
 schedule_action VARCHAR(100),
 mapping_confidence FLOAT,
 FOREIGN KEY(job_id) REFERENCES video_translation_jobs(id) ON DELETE CASCADE
);
CREATE INDEX ix_video_translation_segments_job_id ON video_translation_segments(job_id);
CREATE INDEX ix_video_translation_segments_speaker_id ON video_translation_segments(speaker_id);
CREATE INDEX ix_video_translation_segments_character_id ON video_translation_segments(character_id);
CREATE TABLE character_voice_profiles (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 character_id VARCHAR(36) NOT NULL,
 project_id VARCHAR(36) NOT NULL,
 name VARCHAR(100) NOT NULL,
 gender VARCHAR(20) NOT NULL DEFAULT 'unknown',
 role VARCHAR(20) NOT NULL DEFAULT 'supporting',
 voice_provider VARCHAR(50),
 voice_id VARCHAR(100),
 mapping_confidence FLOAT NOT NULL DEFAULT '0',
 confirmed_by_user BOOLEAN NOT NULL DEFAULT 0,
 created_at DATETIME,
 updated_at DATETIME,
 CONSTRAINT uq_character_profile_project_character UNIQUE(project_id, character_id),
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_character_voice_profiles_project_id ON character_voice_profiles(project_id);
CREATE INDEX ix_character_voice_profiles_character_id ON character_voice_profiles(character_id);
CREATE TABLE voice_pool_entries (
 id VARCHAR(36) NOT NULL PRIMARY KEY,
 provider VARCHAR(50) NOT NULL,
 language VARCHAR(30) NOT NULL,
 gender VARCHAR(20),
 voice_id VARCHAR(100) NOT NULL,
 display_name VARCHAR(200) NOT NULL,
 enabled BOOLEAN NOT NULL DEFAULT 1,
 provider_metadata JSON,
 created_at DATETIME,
 updated_at DATETIME,
 CONSTRAINT uq_voice_pool_provider_voice UNIQUE(provider, voice_id)
);
CREATE INDEX ix_voice_pool_entries_provider ON voice_pool_entries(provider);
CREATE INDEX ix_voice_pool_entries_language ON voice_pool_entries(language);
