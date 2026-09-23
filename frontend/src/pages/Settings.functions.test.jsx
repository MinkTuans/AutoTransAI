import React from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { aiApi } from '../api';
import Settings from './Settings';

vi.mock('../api', () => ({
  providersApi: { list: vi.fn(), listKeys: vi.fn() },
  settingsApi: { getSettings: vi.fn(), getSocialAccounts: vi.fn(), getFunctions: vi.fn(), getModels: vi.fn() },
  youtubeApi: { listAccounts: vi.fn() },
  tiktokApi: { listAccounts: vi.fn() },
  systemApi: {},
  aiApi: { listFunctions: vi.fn(), listProviders: vi.fn(), listModels: vi.fn(), getModel: vi.fn(), updateFunction: vi.fn() },
}));

beforeEach(async () => {
  const { providersApi, settingsApi, youtubeApi, tiktokApi } = await import('../api');
  providersApi.list.mockResolvedValue({ success: true, data: { audio: [], video: [], llm: [] } });
  providersApi.listKeys.mockResolvedValue({ success: true, data: [] });
  settingsApi.getSettings.mockResolvedValue({ success: true, data: {} });
  settingsApi.getSocialAccounts.mockResolvedValue({ success: true, data: [] });
  settingsApi.getFunctions.mockResolvedValue({ success: true, data: [] });
  settingsApi.getModels.mockResolvedValue({ success: true, data: [] });
  youtubeApi.listAccounts.mockResolvedValue([]);
  tiktokApi.listAccounts.mockResolvedValue([]);
  aiApi.listFunctions.mockResolvedValue({ success: true, data: [{
    function_id: 'stt', function_name: 'Speech to Text', capability: 'STT',
    primary_provider_id: 'openai', model_id: 'catalog-id', configuration_error: null,
    default_status: 'ready', selectable: true, updated_at: '2026-09-23T10:00:00',
  }] });
});
afterEach(cleanup);

it('uses canonical Function routing in Settings without rendering legacy model or fallback inputs', async () => {
  render(<Settings />);
  fireEvent.click(await screen.findByRole('button', { name: 'Function' }));
  expect(await screen.findByRole('button', { name: 'Choose model for Speech to Text' })).toBeTruthy();
  expect(screen.getByText('catalog-id')).toBeTruthy();
  expect(screen.queryByRole('combobox')).toBeNull();
  expect(screen.queryByText(/Fallback Provider|Fallback Enabled|Nhập model ID/)).toBeNull();
});
