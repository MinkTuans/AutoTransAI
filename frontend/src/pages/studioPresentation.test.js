import { expect, it } from 'vitest';
import { resolveStudioPhase, sectionForPhase } from './studioPresentation';

it.each([
  [{}, 'setup'], [{ loading: true }, 'unknown'], [{ busy: true }, 'progress'],
  [{ transfer: { status: 'running' } }, 'progress'],
  ...['checking', 'downloading', 'language_detected', 'translated', 'created', 'queued', 'pending', 'extracting_audio', 'stt', 'translating', 'generating_tts', 'syncing_audio', 'rendering', 'processing', 'running'].map(status => [{ job: { status } }, 'progress']),
  ...['needs_review', 'segment_editing'].map(status => [{ job: { status }, workflow: { status: 'running' }, busy: true }, 'review']),
  [{ job: { status: 'copyright_hold' } }, 'hold'], [{ job: { status: 'running', stage: 'COPYRIGHT_HOLD' } }, 'hold'],
  [{ job: { status: 'paused' } }, 'paused'],
  ...['failed', 'interrupted'].map(status => [{ job: { status }, workflow: { status: 'running' } }, 'error']),
  [{ job: { status: 'cancelled' }, busy: true }, 'cancelled'],
  [{ job: { status: 'completed', output_url: '/media/a.mp4' }, workflow: { status: 'running', current_stage: 'PUBLISH' } }, 'result'],
  [{ job: { status: 'COMPLETED', output_video_path: 'a.mp4' } }, 'result'],
  [{ job: { status: 'completed' } }, 'missing_result'],
  [{ job: { status: 'mystery' } }, 'unknown'],
  [{ job: { status: 'translating', segments: [{ id: 's1' }] } }, 'progress'],
  [{ workflow: { status: 'not_started' } }, 'setup'], [{ workflow: { status: 'needs_review' } }, 'review'],
])('classifies %j as %s', (input, expected) => expect(resolveStudioPhase(input)).toBe(expected));
it.each([['setup', 'setup'], ['review', 'review'], ['result', 'result'], ['hold', 'progress'], ['unknown', 'progress'], ['missing_result', 'progress']])('opens %s in %s', (phase, section) => expect(sectionForPhase(phase)).toBe(section));
it('recognizes the existing cancel endpoint representation', () => {
  expect(resolveStudioPhase({ job: { status: 'failed', stage: 'CANCELLED' } })).toBe('cancelled');
});
