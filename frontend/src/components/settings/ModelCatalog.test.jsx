import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { aiApi } from '../../api';
import ModelCatalog from './ModelCatalog';

vi.mock('../../api', () => ({
  aiApi: { listProviders: vi.fn(), listModels: vi.fn(), getModel: vi.fn() },
}));

const providers = [
  { id: 'fal', name: 'Fal Studio', provider_type: 'video', enabled: true, model_count: 2,
    active_model_count: 1, enabled_key_count: 1, status: 'ready' },
  { id: 'edge_tts', name: 'Edge Voices', provider_type: 'audio', enabled: true, model_count: 1,
    active_model_count: 1, enabled_key_count: 0, status: 'ready' },
];

const falModel = {
  id: 'catalog-1', provider_id: 'fal', provider_name: 'Fal Studio', remote_model_id: 'fal/film',
  display_name: 'Film Maker', source: 'discovered', status: 'active', enabled: true,
  retired_at: null, last_seen: '2026-09-23T10:00:00', available_key_count: 1,
  access_scope: 'catalog_unverified', default_for: ['video_generation'],
  capability: { status: 'PARTIAL', capabilities: ['VIDEO_GENERATION'],
    incompatible_capabilities: ['IMAGE_GENERATION'], unknown_capabilities: ['STT'] },
};

const edgeModel = {
  ...falModel, id: 'catalog-edge', provider_id: 'edge_tts', provider_name: 'Edge Voices',
  remote_model_id: 'edge-tts', display_name: null, source: 'system', access_scope: 'keyless',
  available_key_count: 0, default_for: [], capability: { status: 'KNOWN', capabilities: ['TTS'],
    incompatible_capabilities: [], unknown_capabilities: [] },
};

const page = (items, number = 1, total = items.length) => ({ success: true, data: {
  items, page: number, limit: 25, total,
} });

beforeEach(() => {
  aiApi.listProviders.mockReset().mockResolvedValue({ success: true, data: providers });
  aiApi.listModels.mockReset().mockResolvedValue(page([falModel, edgeModel]));
  aiApi.getModel.mockReset().mockResolvedValue({ success: true, data: { ...falModel,
    metadata: { category: 'text-to-video', api_key: 'synthetic-secret-never-show' } } });
});

afterEach(cleanup);

describe('ModelCatalog', () => {
  it('shows dynamic provider groups, capability evidence, defaults and key scopes', async () => {
    render(<ModelCatalog />);
    expect(await screen.findByRole('button', { name: /Fal Studio/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /Edge Voices/ })).toBeTruthy();
    expect(screen.queryByRole('button', { name: /OpenAI/ })).toBeNull();
    expect(screen.getByText('Film Maker')).toBeTruthy();
    expect(screen.getByText('VIDEO_GENERATION')).toBeTruthy();
    expect(screen.getByText('video_generation')).toBeTruthy();
    expect(screen.getByText('Public catalog')).toBeTruthy();
    expect(screen.getByText('Keyless')).toBeTruthy();
    expect(screen.queryByText(/synthetic-secret/)).toBeNull();
  });

  it('submits search and filters to server, then pages through hundreds of models', async () => {
    aiApi.listModels.mockImplementation(async ({ provider_id, q, page: number }) => {
      if (q === 'speech') return page([{ ...falModel, id: 'speech-id', display_name: 'Speech Search' }]);
      if (provider_id === 'fal' && number === 2) return page([{ ...falModel, id: 'second-id', display_name: 'Second Page' }], 2, 60);
      if (provider_id === 'fal') return page([falModel], 1, 60);
      return page([falModel, edgeModel], 1, 60);
    });
    render(<ModelCatalog />);
    await screen.findByText('Film Maker');
    fireEvent.change(screen.getByRole('searchbox', { name: /Search models/ }), { target: { value: 'speech' } });
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));
    expect(await screen.findByText('Speech Search')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: /Fal Studio/ }));
    expect(await screen.findByText('Film Maker')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Next page' }));
    expect(await screen.findByText('Second Page')).toBeTruthy();
    expect(screen.getByText(/Page 2 of 3/)).toBeTruthy();
    expect(aiApi.listModels).toHaveBeenCalledWith({ provider_id: 'fal', q: undefined, page: 2, limit: 25 });
  });

  it('opens a detail dialog with allowlisted metadata and last seen', async () => {
    render(<ModelCatalog />);
    await screen.findByText('Film Maker');
    fireEvent.click(screen.getByRole('button', { name: 'Details for Film Maker' }));
    const dialog = await screen.findByRole('dialog', { name: /Film Maker/ });
    expect(within(dialog).getByText('text-to-video')).toBeTruthy();
    expect(within(dialog).getByText(/Last seen/)).toBeTruthy();
    expect(dialog.textContent).not.toContain('synthetic-secret-never-show');
    fireEvent.click(within(dialog).getByRole('button', { name: 'Close details' }));
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('distinguishes unknown, retired, disabled, no-key, and keyless rows without edit controls', async () => {
    aiApi.listModels.mockResolvedValue(page([
      { ...falModel, id: 'unknown', display_name: 'Unknown Model', capability: {
        status: 'FULL_UNKNOWN', capabilities: [], incompatible_capabilities: [], unknown_capabilities: ['STT'] } },
      { ...falModel, id: 'retired', display_name: 'Retired Model', status: 'retired',
        available_key_count: 0, access_scope: 'none' },
      { ...falModel, id: 'disabled', display_name: 'Disabled Model', status: 'disabled',
        available_key_count: 0, access_scope: 'none' },
      { ...falModel, id: 'no-key', display_name: 'No Key Model', available_key_count: 0, access_scope: 'none' },
      edgeModel,
    ]));
    render(<ModelCatalog />);
    await screen.findByText('Unknown Model');
    expect(screen.getByText('Capabilities unknown')).toBeTruthy();
    expect(screen.getByText('retired')).toBeTruthy();
    expect(screen.getByText('disabled')).toBeTruthy();
    expect(screen.getAllByText('No key').length).toBeGreaterThan(0);
    expect(screen.getByText('Keyless')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /Add Custom Model|Edit|Delete/ })).toBeNull();
  });

  it('shows loading, empty provider, and recoverable error states', async () => {
    let finish;
    aiApi.listModels.mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
    render(<ModelCatalog />);
    expect(screen.getByText('Loading models…')).toBeTruthy();
    finish(page([]));
    expect(await screen.findByText('No models found for this view.')).toBeTruthy();
    aiApi.listModels.mockRejectedValueOnce(new Error('synthetic-secret-private'));
    fireEvent.click(screen.getByRole('button', { name: /Fal Studio/ }));
    expect(await screen.findByText('Could not load models.')).toBeTruthy();
    expect(screen.queryByText('synthetic-secret-private')).toBeNull();
    aiApi.listModels.mockResolvedValueOnce(page([]));
    fireEvent.click(screen.getByRole('button', { name: 'Retry models' }));
    expect(await screen.findByText('No models found for this view.')).toBeTruthy();
    expect(screen.getByText('Fal Studio has no catalog models yet.')).toBeTruthy();
  });
});
