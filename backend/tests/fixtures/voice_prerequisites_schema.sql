-- Frozen independently from 8ae030a^ SpeakerVoiceMapping/VideoTranslationSegment.
-- mapped_column defaults/onupdate are Python-only, never SQL defaults.
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
 FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_speaker_voice_mappings_project_id ON speaker_voice_mappings(project_id);
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
 FOREIGN KEY(job_id) REFERENCES video_translation_jobs(id) ON DELETE CASCADE
);
CREATE INDEX ix_video_translation_segments_job_id ON video_translation_segments(job_id);
