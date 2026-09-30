// @vitest-environment jsdom
import React from 'react';
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, render, screen, within } from '@testing-library/react';
import WorkflowTimeline from './WorkflowTimeline';
afterEach(cleanup);
it('finishes video production without claiming optional publishing', () => {
  render(<WorkflowTimeline job={{ status: 'completed', stage: 'PRODUCE', output_url: '/media/a.mp4' }} />);
  expect(within(screen.getByRole('button', { name: /Xuất video/ })).getByText('Hoàn tất')).toBeTruthy();
  expect(within(screen.getByRole('button', { name: /Đăng video/ })).getByText('Chờ')).toBeTruthy();
});
it('shows publishing completion only from its own stage evidence', () => {
  render(<WorkflowTimeline job={{ status: 'completed' }} statusData={{ stages: [{ name: 'PUBLISH', status: 'passed' }] }} />);
  expect(within(screen.getByRole('button', { name: /Đăng video/ })).getByText('Hoàn tất')).toBeTruthy();
});
it('does not invent progress or offer a second start for idle Studio', () => {
  render(<WorkflowTimeline statusData={{ status: 'not_started', stages: [] }} onStart={vi.fn()} />);
  expect(screen.queryByText(/0%/)).toBeNull();
  expect(screen.queryByRole('button', { name: /Start|Bắt đầu/ })).toBeNull();
  expect(screen.queryByText('Đang xử lý')).toBeNull();
});
it('keeps diagnostics hidden by default and exposes logs and stage retry on request', () => {
  const props = { job: { status: 'running' }, onOpenLogs: vi.fn(), onRetryStage: vi.fn() };
  const { rerender } = render(<WorkflowTimeline {...props} />);
  expect(screen.queryByRole('region', { name: 'Chi tiết kỹ thuật' })).toBeNull();
  expect(screen.queryByRole('button', { name: 'Log' })).toBeNull();
  rerender(<WorkflowTimeline {...props} showDiagnostics />);
  expect(screen.getByText('Worker Heartbeat:')).toBeTruthy();
  expect(screen.getByRole('button', { name: 'Log' })).toBeTruthy();
  expect(screen.getByRole('button', { name: /Thử lại bước/ })).toBeTruthy();
});
it.each([['running', 'Tạm dừng'], ['paused', 'Tiếp tục'], ['failed', 'Thử lại']])('disables %s actions while sending a request', (status, label) => {
  render(<WorkflowTimeline job={{ status }} loadingAction="cancel" onPause={vi.fn()} onResume={vi.fn()} onCancel={vi.fn()} onRetryJob={vi.fn()} />);
  expect(screen.getAllByRole('button', { name: label }).every(button => button.disabled)).toBe(true);
});
it('does not mistake synthesized job workflow stages for publishing evidence', () => {
  render(<WorkflowTimeline job={{ id: 'j1', status: 'completed' }} statusData={{ context: { job_id: 'j1' }, stages: [{ name: 'PUBLISH', status: 'passed', steps: [] }] }} />);
  expect(within(screen.getByRole('button', { name: /Đăng video/ })).getByText('Chờ')).toBeTruthy();
});
it('does not fabricate a transfer percentage when only a message is available', () => {
  render(<WorkflowTimeline job={{ status: 'running' }} transferProgress={{ kind: 'download', status: 'running', message: 'Đang nhận video' }} />);
  expect(screen.queryByText(/0%/)).toBeNull();
  expect(screen.getByText('Đang nhận video')).toBeTruthy();
  expect(screen.queryByText(/0 B/)).toBeNull();
});
