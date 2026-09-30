// @vitest-environment jsdom
import React from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import VideoTranslator from './VideoTranslator';
import { videoTranslatorApi, providersApi, projectsApi, thumbnailApi } from '../api';
vi.mock('../api', () => ({
  videoTranslatorApi: { getStudioState: vi.fn(), getJob: vi.fn(), getWorkflowStatus: vi.fn(), listCharacterProfiles: vi.fn(), getGlossary: vi.fn(), updateSegments: vi.fn(), preflightWorkflow: vi.fn(), startWorkflow: vi.fn() },
  providersApi: { list: vi.fn(), listVoices: vi.fn() },
  projectsApi: { list: vi.fn(), getSettings: vi.fn(), saveSettings: vi.fn() },
  thumbnailApi: { listLibrary: vi.fn() }, aiApi: {}, videoEditorApi: {},
}));
const segment = { id: 's1', number: 1, start_time: 0, end_time: 2, original_text: 'Hello', translated_text: 'Xin chào', gender: 'female', voice_provider: 'edge_tts', voice_id: 'vi-VN-HoaiMyNeural' };
let currentJob, workflow, streams;
const ok = data => ({ success: true, data });
beforeEach(() => {
  vi.resetAllMocks();
  currentJob = { id: 'j1', project_id: 'p1', status: 'translating', stage: 'TRANSLATING', segments: [segment] };
  workflow = { status: 'not_started', stages: [] };
  streams = [];
  vi.stubGlobal('EventSource', class { constructor() { streams.push(this); } close() {} });
  videoTranslatorApi.getStudioState.mockImplementation(async () => ok({ job: currentJob, asset: { title: 'Video' }, segments: currentJob.segments, settings_snapshot: {} }));
  videoTranslatorApi.getJob.mockImplementation(async () => ok(currentJob));
  videoTranslatorApi.getWorkflowStatus.mockImplementation(async () => ok(workflow));
  videoTranslatorApi.getGlossary.mockResolvedValue(ok([]));
  videoTranslatorApi.listCharacterProfiles.mockResolvedValue(ok([]));
  videoTranslatorApi.updateSegments.mockResolvedValue(ok({}));
  providersApi.list.mockResolvedValue({ data: { audio: [{ id: 'edge_tts', name: 'Edge TTS', configured: true }] } });
  providersApi.listVoices.mockResolvedValue(ok([{ id: 'vi-VN-HoaiMyNeural', name: 'Hoài My', gender: 'female', language: 'vi-VN' }]));
  projectsApi.list.mockResolvedValue(ok([{ id: 'p1', title: 'Dự án một' }, { id: 'p2', title: 'Dự án hai' }]));
  projectsApi.getSettings.mockResolvedValue(ok({ video_url: '', target_language: 'vi' }));
  thumbnailApi.listLibrary.mockResolvedValue(ok([]));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
const heading = name => screen.getByRole('button', { name: new RegExp(`^${name}`), hidden: true });
const opened = name => heading(name).getAttribute('aria-expanded');
async function pollJob() { await act(async () => { await new Promise(resolve => setTimeout(resolve, 1600)); }); }
it('starts with a single preflight action and closed advanced configuration and support', async () => {
  render(<VideoTranslator initialProjectId="p1" />);
  await waitFor(() => expect(heading('Bắt đầu dịch').disabled).toBe(false));
  expect(screen.getAllByRole('button', { name: /^Bắt đầu dịch$/ })).toHaveLength(1);
  expect(opened('Nhập & cấu hình')).toBe('true');
  expect(screen.queryByText('Worker Heartbeat:')).toBeNull();
  videoTranslatorApi.preflightWorkflow.mockResolvedValue(ok({ can_start: false, checks: [{ passed: false, description: 'Thiếu video', category: 'required' }] }));
  fireEvent.click(heading('Bắt đầu dịch'));
  expect(await screen.findByText('Thiếu video')).toBeTruthy();
  expect(screen.queryByRole('button', { name: /Bắt đầu Workflow ngay/ })).toBeNull();
});
it('opens review and result on phase transitions while preserving focused drafts and manual collapse', async () => {
  render(<VideoTranslator initialJobId="j1" initialProjectId="p1" />);
  await waitFor(() => expect(opened('Tiến độ')).toBe('true'));
  expect(opened('Duyệt bản dịch & giọng')).toBe('false');
  currentJob = { ...currentJob, status: 'segment_editing' };
  await pollJob();
  expect(opened('Duyệt bản dịch & giọng')).toBe('true');
  const editor = screen.getByDisplayValue('Xin chào');
  fireEvent.change(editor, { target: { value: 'Bản sửa của tôi' } });
  editor.focus();
  await pollJob();
  expect(screen.getByDisplayValue('Bản sửa của tôi')).toBe(editor);
  expect(document.activeElement).toBe(editor);
  fireEvent.click(heading('Tiến độ'));
  const manual = opened('Tiến độ');
  await pollJob();
  expect(opened('Tiến độ')).toBe(manual);
  currentJob = { ...currentJob, status: 'completed', output_url: '/media/a.mp4' };
  await pollJob();
  expect(opened('Kết quả')).toBe('true');
  expect(opened('Duyệt bản dịch & giọng')).toBe('true');
  expect(document.activeElement).toBe(editor);
  expect(screen.getByText(/Video Lồng Tiếng Đã Hoàn Thành/)).toBeTruthy();
}, 15000);
it('retains last known state on a connection failure and prevents duplicate start', async () => {
  render(<VideoTranslator initialJobId="j1" initialProjectId="p1" />);
  await waitFor(() => expect(opened('Tiến độ')).toBe('true'));
  await act(async () => streams.at(-1).onerror(new Error('offline')));
  expect(screen.getByText(/Mất kết nối/)).toBeTruthy();
  expect(heading('Bắt đầu dịch').disabled).toBe(true);
  expect(opened('Tiến độ')).toBe('true');
});
it.each([['copyright_hold', 'Rủi ro bản quyền CAO'], ['completed', 'Chưa có file kết quả'], ['cancelled', 'Đã hủy'], ['interrupted', 'Tác vụ bị gián đoạn'], ['mystery', 'Đang xác định trạng thái']])('presents %s safely', async (status, message) => {
  currentJob = { ...currentJob, status, segments: [] };
  render(<VideoTranslator initialJobId="j1" initialProjectId="p1" />);
  expect((await screen.findAllByText(new RegExp(message))).length).toBeGreaterThan(0);
  expect(heading('Bắt đầu dịch').disabled).toBe(true);
  expect(document.querySelector('video')).toBeNull();
});
it('guards edited segments and clears old data on confirmed project switch', async () => {
  currentJob = { ...currentJob, status: 'segment_editing' };
  render(<VideoTranslator initialJobId="j1" initialProjectId="p1" />);
  const editor = await screen.findByDisplayValue('Xin chào');
  fireEvent.change(editor, { target: { value: 'Bản sửa chưa lưu' } });
  fireEvent.change(screen.getByRole('combobox', { name: 'Dự án' }), { target: { value: 'p2' } });
  expect(await screen.findByText(/Có thay đổi.*chưa lưu/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: /Bỏ qua thay đổi & Chuyển dự án/ }));
  await waitFor(() => expect(screen.queryByDisplayValue('Bản sửa chưa lưu')).toBeNull());
  expect(screen.queryByText('Hello')).toBeNull();
});
