// Presentation only: operational permissions stay with the existing page handlers.
export function resolveStudioPhase({ job, workflow, transfer, busy, loading } = {}) {
  if (loading) return 'unknown';
  const status = String(job?.status || workflow?.status || '').toLowerCase();
  const stage = String(job?.stage || workflow?.current_stage || '').toUpperCase();
  if (status === 'completed') return job?.output_url || job?.output_video_path ? 'result' : 'missing_result';
  if (['failed', 'interrupted'].includes(status)) return 'error';
  if (status === 'cancelled') return 'cancelled';
  if (status === 'copyright_hold' || stage === 'COPYRIGHT_HOLD') return 'hold';
  if (['needs_review', 'segment_editing'].includes(status)) return 'review';
  if (status === 'paused') return 'paused';
  if (busy || transfer?.status === 'running') return 'progress';
  if (['checking', 'downloading', 'language_detected', 'translated', 'created', 'queued', 'pending', 'extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering', 'processing', 'running'].includes(status)) return 'progress';
  if ((!job && !workflow) || (!job && status === 'not_started')) return 'setup';
  return 'unknown';
}

export function sectionForPhase(phase) {
  return ['setup', 'review', 'result'].includes(phase) ? phase : 'progress';
}
