import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { aiApi } from '../../api';
import FunctionRouting from './FunctionRouting';

vi.mock('../../api', () => ({ aiApi: {
  listFunctions: vi.fn(), updateFunction: vi.fn(), listProviders: vi.fn(),
  listModels: vi.fn(), getModel: vi.fn(),
} }));

const speech = {
  function_id: 'stt', function_name: 'Speech to Text', capability: 'STT',
  primary_provider_id: 'openai', model_id: 'old-model', configuration_error: null,
  default_status: 'ready', selectable: true, updated_at: '2026-09-23T10:00:00',
};
const providers = [
  { id: 'openai', name: 'OpenAI', provider_type: 'llm', enabled: true, supported: true,
    model_count: 3, active_model_count: 3, enabled_key_count: 1, status: 'ready' },
  { id: 'edge_tts', name: 'Edge Voices', provider_type: 'audio', enabled: true, supported: true,
    model_count: 1, active_model_count: 1, enabled_key_count: 0, status: 'ready' },
];
const model = {
  id: 'new-model', provider_id: 'openai', provider_name: 'OpenAI',
  remote_model_id: 'speech-v2', display_name: 'Speech V2', source: 'discovered',
  status: 'active', enabled: true, retired_at: null, last_seen: '2026-09-23T10:00:00',
  available_key_count: 1, access_scope: 'listing_unverified', selectable: true,
  default_for: ['translation'],
  capability: { status: 'KNOWN', capabilities: ['STT'], incompatible_capabilities: [], unknown_capabilities: [] },
};
const page = (items, number = 1, total = items.length) => ({ success: true, data: {
  items, page: number, limit: 25, total,
} });

beforeEach(() => {
  aiApi.listFunctions.mockReset().mockResolvedValue({ success: true, data: [speech] });
  aiApi.updateFunction.mockReset().mockResolvedValue({ success: true, data: {
    ...speech, model_id: 'new-model', default_status: 'ready', selectable: true,
  } });
  aiApi.listProviders.mockReset().mockResolvedValue({ success: true, data: providers });
  aiApi.listModels.mockReset().mockResolvedValue(page([model]));
  aiApi.getModel.mockReset().mockResolvedValue({ success: true, data: {
    ...model, metadata: { created: 1700000000, api_key: 'synthetic-secret-never-show' },
  } });
});
afterEach(cleanup);

describe('FunctionRouting', () => {
  it('shows every configured default and its canonical status without fallback controls', async () => {
    aiApi.listFunctions.mockResolvedValue({ success: true, data: [
      speech,
      { ...speech, function_id: 'translation', function_name: 'Translation', model_id: 'legacy-id',
        default_status: 'legacy_unmigrated', selectable: false },
      { ...speech, function_id: 'visual_gender', function_name: 'Visual Gender', model_id: 'gone-id',
        default_status: 'missing', selectable: false, configuration_error: 'configuration_error' },
    ] });
    render(<FunctionRouting />);
    expect(await screen.findByText('Speech to Text')).toBeTruthy();
    expect(screen.getByText('old-model')).toBeTruthy();
    expect(screen.getByText('legacy-id')).toBeTruthy();
    expect(screen.getByText('legacy_unmigrated')).toBeTruthy();
    expect(screen.getByText(/Configuration issue: configuration_error/)).toBeTruthy();
    expect(screen.queryByRole('combobox')).toBeNull();
    expect(screen.queryByText(/Fallback Provider|Fallback Enabled|Nhập model ID/)).toBeNull();
  });

  it('shows the readable model name when the Function view contains one', async () => {
    aiApi.listFunctions.mockResolvedValue({ success: true, data: [
      { ...speech, model_id: 'catalog-uuid', model_display_name: 'Gemini Audio' },
    ] });
    render(<FunctionRouting />);
    expect(await screen.findByText('Gemini Audio')).toBeTruthy();
    expect(screen.getByText('Default model')).toBeTruthy();
    expect(screen.queryByText('catalog-uuid')).toBeNull();
  });

  it('opens capability-filtered picker and searches, filters, and pages on the server', async () => {
    aiApi.listModels.mockImplementation(async ({ provider_id, q, page: number }) => {
      if (q === 'speech') return page([{ ...model, id: 'search-model', display_name: 'Speech Search' }]);
      if (provider_id === 'openai' && number === 2) return page([{ ...model, id: 'page-two', display_name: 'Page Two' }], 2, 60);
      return page([model], 1, 60);
    });
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech to Text' }));
    const picker = await screen.findByRole('dialog', { name: /Choose STT model/ });
    expect(aiApi.listModels).toHaveBeenCalledWith({ capability: 'STT', provider_id: undefined,
      q: undefined, page: 1, limit: 25 });
    fireEvent.change(within(picker).getByRole('searchbox', { name: 'Search models' }),
      { target: { value: 'speech' } });
    fireEvent.click(within(picker).getByRole('button', { name: 'Search' }));
    expect(await within(picker).findByText('Speech Search')).toBeTruthy();
    fireEvent.click(within(picker).getByRole('button', { name: /OpenAI/ }));
    expect(await within(picker).findByText('Speech V2')).toBeTruthy();
    fireEvent.click(within(picker).getByRole('button', { name: 'Next page' }));
    expect(await within(picker).findByText('Page Two')).toBeTruthy();
    expect(within(picker).getByText(/Page 2 of 3/)).toBeTruthy();
    expect(aiApi.listModels).toHaveBeenCalledWith({ capability: 'STT', provider_id: 'openai',
      q: undefined, page: 2, limit: 25 });
  });

  it('uses capability-specific eligibility for inactive, incompatible, no-key and keyless entries', async () => {
    aiApi.listModels.mockResolvedValue(page([
      { ...model, id: 'retired', display_name: 'Retired', status: 'retired', selectable: false },
      { ...model, id: 'disabled', display_name: 'Disabled', status: 'disabled', selectable: false },
      { ...model, id: 'incompatible', display_name: 'Incompatible', capability: {
        status: 'KNOWN', capabilities: [], incompatible_capabilities: ['STT'], unknown_capabilities: [] }, selectable: false },
      { ...model, id: 'no-key', display_name: 'No Key', available_key_count: 0,
        access_scope: 'none', selectable: false },
      { ...model, id: 'unknown', display_name: 'Unknown', capability: {
        status: 'FULL_UNKNOWN', capabilities: [], incompatible_capabilities: [], unknown_capabilities: ['STT'] } },
      { ...model, id: 'public', display_name: 'Public Candidate', access_scope: 'catalog_unverified' },
      { ...model, id: 'keyless', display_name: 'Keyless Candidate', access_scope: 'keyless',
        available_key_count: 0, selectable: false, capability: {
          status: 'FULL_UNKNOWN', capabilities: [], incompatible_capabilities: [], unknown_capabilities: ['STT'] } },
    ]));
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech to Text' }));
    const picker = await screen.findByRole('dialog');
    for (const name of ['Retired', 'Disabled', 'Incompatible', 'No Key', 'Keyless Candidate']) {
      expect(within(picker).getByRole('button', { name: `Select ${name}` }).disabled).toBe(true);
    }
    for (const name of ['Unknown', 'Public Candidate']) {
      expect(within(picker).getByRole('button', { name: `Select ${name}` }).disabled).toBe(false);
    }
    expect(within(picker).getAllByText('Capabilities unknown').length).toBeGreaterThan(0);
    expect(within(picker).getByText(/entitlement unverified/i)).toBeTruthy();
  });

  it('allows backend-eligible keyless TTS and image candidates', async () => {
    aiApi.listFunctions.mockResolvedValue({ success: true, data: [
      { ...speech, function_id: 'tts', function_name: 'Speech Output', capability: 'TTS' },
      { ...speech, function_id: 'image_generation', function_name: 'Image', capability: 'IMAGE_GENERATION' },
    ] });
    aiApi.listModels.mockImplementation(async ({ capability }) => page([{ ...model,
      id: capability === 'TTS' ? 'edge' : 'pollinations',
      display_name: capability === 'TTS' ? 'Edge Voice' : 'Pollinations Image',
      access_scope: 'keyless', available_key_count: 0, selectable: true,
      capability: { status: 'FULL_UNKNOWN', capabilities: [], incompatible_capabilities: [], unknown_capabilities: [capability] },
    }]));
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech Output' }));
    expect((await screen.findByRole('button', { name: 'Select Edge Voice' })).disabled).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Close model picker' }));
    fireEvent.click(screen.getByRole('button', { name: 'Choose model for Image' }));
    expect((await screen.findByRole('button', { name: 'Select Pollinations Image' })).disabled).toBe(false);
  });

  it('sets exact catalog ID and updates the visible default only after successful PUT', async () => {
    aiApi.updateFunction.mockResolvedValue({ success: true, data: {
      ...speech, model_id: 'new-model', model_display_name: 'Speech V2',
    } });
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech to Text' }));
    const picker = await screen.findByRole('dialog');
    fireEvent.click(await within(picker).findByRole('button', { name: 'Select Speech V2' }));
    await waitFor(() => expect(aiApi.updateFunction).toHaveBeenCalledWith('stt', { model_id: 'new-model' }));
    expect(await screen.findByText('Speech V2')).toBeTruthy();
    expect(screen.queryByText('new-model')).toBeNull();
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('preserves previous default and shows fixed actionable error on failed PUT', async () => {
    aiApi.updateFunction.mockRejectedValue(new Error('synthetic-secret-private'));
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech to Text' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Select Speech V2' }));
    expect(await screen.findByText(/Model unavailable; refresh the list and choose another/)).toBeTruthy();
    expect(screen.getByText('old-model')).toBeTruthy();
    expect(screen.queryByText('synthetic-secret-private')).toBeNull();
  });

  it('shows safe detail metadata and recoverable list errors', async () => {
    render(<FunctionRouting />);
    fireEvent.click(await screen.findByRole('button', { name: 'Choose model for Speech to Text' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Details for Speech V2' }));
    const detail = await screen.findByRole('dialog', { name: /Model details: Speech V2/ });
    expect(within(detail).getByText('1700000000')).toBeTruthy();
    expect(detail.textContent).not.toContain('synthetic-secret-never-show');
    fireEvent.click(within(detail).getByRole('button', { name: 'Close details' }));
    aiApi.listModels.mockRejectedValueOnce(new Error('synthetic-secret-private'));
    fireEvent.click(screen.getByRole('button', { name: /OpenAI/ }));
    expect(await screen.findByText('Could not load models.')).toBeTruthy();
    expect(screen.queryByText('synthetic-secret-private')).toBeNull();
  });

  it('recovers from a failed Function list without exposing its exception', async () => {
    aiApi.listFunctions.mockRejectedValueOnce(new Error('synthetic-secret-private'));
    render(<FunctionRouting />);
    expect(await screen.findByText('Could not load AI functions.')).toBeTruthy();
    expect(screen.queryByText('synthetic-secret-private')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'Retry functions' }));
    expect(await screen.findByText('Speech to Text')).toBeTruthy();
  });
});
