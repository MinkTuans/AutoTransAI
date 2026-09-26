import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

import App from './App';

vi.mock('./pages/Dashboard', () => ({ default: () => <div>Dashboard page</div> }));
vi.mock('./pages/ProjectDetail', () => ({ default: () => <div>Project detail page</div> }));
vi.mock('./pages/Settings', () => ({ default: () => <div>Settings page</div> }));
vi.mock('./pages/VideoTranslator', () => ({ default: () => <div>Studio translation page</div> }));
vi.mock('./pages/VideoMerger', () => ({ default: () => <div>Video merger page</div> }));

beforeEach(() => {
  localStorage.clear();
  window.history.replaceState({}, '', '/?page=live_audio');
});
afterEach(() => {
  cleanup();
  window.history.replaceState({}, '', '/');
});

it('sends an old Live bookmark to Studio and removes the Live navigation button', () => {
  render(<App />);
  expect(screen.getByText('Studio translation page')).toBeTruthy();
  expect(screen.queryByRole('button', { name: 'Dịch Audio trực tiếp' })).toBeNull();
  expect(window.location.search).toBe('?page=translator');
});
