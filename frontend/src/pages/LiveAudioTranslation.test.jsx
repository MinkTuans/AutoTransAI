import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

import LiveAudioTranslation from './LiveAudioTranslation';
import Navbar from '../components/Navbar';

const api = vi.hoisted(() => ({
  start: vi.fn(), status: vi.fn(), cancel: vi.fn(), audioUrl: vi.fn(), videoUrl: vi.fn(),
}));
vi.mock('../api', () => ({ liveAudioApi: api }));

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.removeItem('autotrans_live_audio_job_id');
  api.audioUrl.mockImplementation(id => `/api/live-audio-translations/${id}/audio`);
  api.videoUrl.mockImplementation(id => `/api/live-audio-translations/${id}/video`);
});
afterEach(cleanup);

it('adds a separate navigation link for audio translation', () => {
  const onNavigate = vi.fn();
  render(<Navbar activePage="translator" onNavigate={onNavigate} />);
  fireEvent.click(screen.getByRole('button', { name: /Dịch Audio trực tiếp/i }));
  expect(onNavigate).toHaveBeenCalledWith('live_audio');
});

it('uploads audio, shows session status, and plays downloadable translated audio', async () => {
  api.start.mockResolvedValue({ data: { id: 'job-123', status: 'queued' } });
  api.status.mockResolvedValue({ data: { id: 'job-123', status: 'completed',
    audio_url: '/api/live-audio-translations/job-123/audio' } });
  render(<LiveAudioTranslation />);
  expect(screen.getByLabelText('Source Language').value).toBe('auto');
  expect(screen.getByLabelText('Target Language').value).toBe('vi');
  const file = new File(['wave'], 'speech.wav', { type: 'audio/wav' });
  fireEvent.change(screen.getByLabelText('Upload Audio or Video'), { target: { files: [file] } });
  fireEvent.click(screen.getByRole('button', { name: 'Start Translation' }));
  await waitFor(() => expect(api.start).toHaveBeenCalledWith(file));
  await waitFor(() => expect(screen.getByRole('status').textContent).toContain('Hoàn tất'));
  expect(screen.getByLabelText('Âm thanh tiếng Việt').getAttribute('src')).toBe(
    '/api/live-audio-translations/job-123/audio');
  expect(screen.getByRole('link', { name: 'Download translated audio' }).getAttribute('href')).toBe(
    '/api/live-audio-translations/job-123/audio');
});

it('uploads MP4 and plays the translated video result', async () => {
  api.start.mockResolvedValue({ data: { id: 'video-123', status: 'queued', media_type: 'video' } });
  api.status.mockResolvedValue({ data: { id: 'video-123', status: 'completed', media_type: 'video',
    video_url: '/api/live-audio-translations/video-123/video' } });
  render(<LiveAudioTranslation />);
  const input = screen.getByLabelText('Upload Audio or Video');
  expect(input.getAttribute('accept')).toContain('.mp4');
  const file = new File(['video'], 'clip.mp4', { type: 'video/mp4' });
  fireEvent.change(input, { target: { files: [file] } });
  fireEvent.click(screen.getByRole('button', { name: 'Start Translation' }));
  await waitFor(() => expect(api.start).toHaveBeenCalledWith(file));
  expect(await screen.findByLabelText('Video tiếng Việt')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Download translated video' }).getAttribute('href')).toBe(
    '/api/live-audio-translations/video-123/video');
});

it('shows a Live API error without using the video translation flow', async () => {
  api.start.mockResolvedValue({ data: { id: 'job-404', status: 'queued' } });
  api.status.mockResolvedValue({ data: { id: 'job-404', status: 'failed', error_code: 'quota_or_rate_limit' } });
  render(<LiveAudioTranslation />);
  fireEvent.change(screen.getByLabelText('Upload Audio or Video'), { target: { files: [
    new File(['wave'], 'speech.wav', { type: 'audio/wav' }),
  ] } });
  fireEvent.click(screen.getByRole('button', { name: 'Start Translation' }));
  await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('hạn mức'));
  expect(screen.queryByLabelText('Âm thanh tiếng Việt')).toBeNull();
});

it('restores the last Live job after leaving and returning to the page', async () => {
  localStorage.setItem('autotrans_live_audio_job_id', 'job-123');
  api.status.mockResolvedValue({ data: { id: 'job-123', status: 'completed' } });
  render(<LiveAudioTranslation />);
  await waitFor(() => expect(api.status).toHaveBeenCalledWith('job-123'));
  expect(await screen.findByLabelText('Âm thanh tiếng Việt')).toBeTruthy();
});

it('keeps a started job when its first status request fails', async () => {
  api.start.mockResolvedValue({ data: { id: 'job-123', status: 'queued' } });
  api.status.mockRejectedValue(new Error('temporary status failure'));
  render(<LiveAudioTranslation />);
  fireEvent.change(screen.getByLabelText('Upload Audio or Video'), { target: { files: [
    new File(['wave'], 'speech.wav', { type: 'audio/wav' }),
  ] } });
  fireEvent.click(screen.getByRole('button', { name: 'Start Translation' }));
  await waitFor(() => expect(localStorage.getItem('autotrans_live_audio_job_id')).toBe('job-123'));
  expect(screen.getByRole('status').textContent).toContain('Đang chờ');
});

it('allows a new session if the backend has lost an active job', async () => {
  api.start.mockResolvedValue({ data: { id: 'job-123', status: 'streaming' } });
  api.status.mockResolvedValueOnce({ data: { id: 'job-123', status: 'streaming' } });
  api.status.mockRejectedValue({ response: { status: 404 } });
  render(<LiveAudioTranslation />);
  fireEvent.change(screen.getByLabelText('Upload Audio or Video'), { target: { files: [
    new File(['wave'], 'speech.wav', { type: 'audio/wav' }),
  ] } });
  fireEvent.click(screen.getByRole('button', { name: 'Start Translation' }));
  await waitFor(() => expect(screen.getByRole('status').textContent).toContain('Đang dịch'));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Start Translation' }).disabled).toBe(false),
    { timeout: 3000 });
  expect(localStorage.getItem('autotrans_live_audio_job_id')).toBeNull();
});
