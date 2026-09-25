import React from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { aiApi } from '../../api';
import KeyPool from './KeyPool';

vi.mock('../../api', () => ({ aiApi: {
  listProviders: vi.fn(), createProvider: vi.fn(), listKeys: vi.fn(), addKey: vi.fn(), setKeyEnabled: vi.fn(),
  deleteKey: vi.fn(), refreshModels: vi.fn(),
} }));

const providers = [
  { id: 'acme', name: 'Acme Voice', provider_type: 'audio', enabled: true, supported: true,
    model_count: 2, active_model_count: 2, enabled_key_count: 1, status: 'ready', keyless: false },
  { id: 'local_voice', name: 'Local Voice', provider_type: 'audio', enabled: true, supported: true,
    model_count: 1, active_model_count: 1, enabled_key_count: 0, status: 'ready', keyless: true },
];
const key = { id: 'key-1', provider_id: 'acme', masked_key: '****ABCD', enabled: true,
  revision: 1, created_at: '2026-09-23T00:00:00Z' };

beforeEach(() => {
  aiApi.listProviders.mockReset().mockResolvedValue({ success: true, data: providers });
  aiApi.createProvider.mockReset();
  aiApi.listKeys.mockReset().mockImplementation(async id => ({ success: true, data: id === 'acme' ? [key] : [] }));
  aiApi.addKey.mockReset();
  aiApi.setKeyEnabled.mockReset();
  aiApi.deleteKey.mockReset();
  aiApi.refreshModels.mockReset();
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

it('adds a provider profile, reloads the catalog, and selects the new provider', async () => {
  const added = { ...providers[0], id: 'custom_llm', name: 'Custom LLM', provider_type: 'llm', supported: false };
  aiApi.createProvider.mockResolvedValue({ success: true, data: added });
  aiApi.listProviders.mockResolvedValueOnce({ success: true, data: providers })
    .mockResolvedValueOnce({ success: true, data: [...providers, added] });
  render(<KeyPool />);
  await screen.findByRole('button', { name: /Acme Voice/ });
  fireEvent.click(screen.getByRole('button', { name: 'Thêm nhà cung cấp AI' }));
  const dialog = screen.getByRole('dialog', { name: 'Thêm nhà cung cấp AI' });
  expect(within(dialog).getByRole('option', { name: 'Vision' }).value).toBe('vision');
  fireEvent.change(within(dialog).getByLabelText('ID'), { target: { value: 'custom_llm' } });
  fireEvent.change(within(dialog).getByLabelText('Tên'), { target: { value: 'Custom LLM' } });
  fireEvent.change(within(dialog).getByLabelText('Loại'), { target: { value: 'llm' } });
  fireEvent.change(within(dialog).getByLabelText('Base URL (không bắt buộc)'), { target: { value: 'https://example.com/v1' } });
  fireEvent.click(within(dialog).getByRole('button', { name: 'Lưu nhà cung cấp' }));
  await screen.findByRole('button', { name: /Custom LLM/ });
  expect(screen.getByRole('button', { name: /Custom LLM/ }).getAttribute('aria-pressed')).toBe('true');
  expect(screen.getByRole('heading', { name: '🔑 Key Pool — Custom LLM' })).toBeTruthy();
  expect(screen.getByText('Chưa có adapter chạy model cho nhà cung cấp này.')).toBeTruthy();
  expect(screen.queryByRole('dialog')).toBeNull();
  expect(aiApi.createProvider).toHaveBeenCalledWith({ id: 'custom_llm', name: 'Custom LLM', provider_type: 'llm', base_url: 'https://example.com/v1' });
});

it('groups backend providers and shows only selected provider masked keys', async () => {
  render(<KeyPool />);
  expect(await screen.findByRole('button', { name: /Acme Voice/ })).toBeTruthy();
  expect(screen.getByRole('button', { name: /Local Voice/ })).toBeTruthy();
  expect(screen.queryByText(/OpenAI/)).toBeNull();
  expect(await screen.findByText('****ABCD')).toBeTruthy();
  expect(screen.queryByText('key-1')).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: /Local Voice/ }));
  expect(await screen.findByText(/Không cần API key/)).toBeTruthy();
  expect(screen.queryByText('****ABCD')).toBeNull();
  expect(screen.queryByRole('button', { name: /Thêm Key/ })).toBeNull();
  expect(screen.queryByLabelText('API Key')).toBeNull();
});

it('adds a key, clears plaintext on incomplete discovery, and reports it remains disabled', async () => {
  aiApi.addKey.mockResolvedValue({ success: true, data: { key: { ...key, id: 'key-2', masked_key: '****WXYZ', enabled: false },
    discovery: { status: 'partial', access_scope: 'unknown', error_code: 'rate_limited', verified_for_generation: false } } });
  aiApi.listKeys.mockResolvedValueOnce({ success: true, data: [] }).mockResolvedValue({ success: true, data: [{ ...key, id: 'key-2', masked_key: '****WXYZ', enabled: false }] });
  render(<KeyPool />);
  await screen.findByRole('button', { name: /Acme Voice/ });
  const actions = screen.getByTestId('key-pool-actions');
  expect(within(actions).getAllByRole('button').map(button => button.textContent)).toEqual(['🔄 Cập nhật Models', '+ Thêm Key']);
  fireEvent.click(within(actions).getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-secret-private' } });
  fireEvent.click(screen.getByRole('button', { name: 'Lưu Key' }));
  expect(await screen.findByText(/vẫn tắt.*partial/i)).toBeTruthy();
  expect(screen.getByLabelText('API Key').value).toBe('');
  expect(screen.queryByText('synthetic-secret-private')).toBeNull();
  expect(await screen.findByText('****WXYZ')).toBeTruthy();
  expect(aiApi.refreshModels).not.toHaveBeenCalled();
});

it('clears plaintext and hides raw backend errors on failed add', async () => {
  aiApi.addKey.mockRejectedValue(new Error('synthetic-secret-private'));
  render(<KeyPool />);
  await screen.findByRole('button', { name: /Acme Voice/ });
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-secret-private' } });
  fireEvent.click(screen.getByRole('button', { name: 'Lưu Key' }));
  expect(await screen.findByRole('alert')).toBeTruthy();
  expect(screen.getByLabelText('API Key').value).toBe('');
  expect(document.body.textContent).not.toContain('synthetic-secret-private');
});

it('keeps a key disabled when enable discovery is incomplete and deletes without refresh', async () => {
  aiApi.listKeys.mockResolvedValue({ success: true, data: [{ ...key, enabled: false }] });
  aiApi.setKeyEnabled.mockResolvedValue({ success: true, data: { key: { ...key, enabled: false },
    discovery: { status: 'failed', access_scope: 'unknown', error_code: 'invalid_key', verified_for_generation: false } } });
  aiApi.deleteKey.mockResolvedValue({ success: true, data: { deleted: true } });
  vi.spyOn(window, 'confirm').mockReturnValue(true);
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: 'Bật Key' }));
  expect(await screen.findByText(/vẫn tắt.*failed/i)).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Xóa Key' }));
  expect(await screen.findByText(/models.*chỉ.*lần cập nhật.*complete/i)).toBeTruthy();
  expect(aiApi.refreshModels).not.toHaveBeenCalled();
});

it('shows per-provider refresh outcomes and never reports cleanup for partial or failed results', async () => {
  aiApi.refreshModels.mockResolvedValueOnce({ success: false, data: { id: 'run-1', status: 'partial', providers: {
    acme: { keys_scanned: 2, retired: 0, status: 'partial', reason: 'one_key_failed', results: [
      { key_id: 'key-1', status: 'complete', access_scope: 'credential', error_code: null, complete: true },
      { key_id: 'key-2', status: 'failed', access_scope: 'unknown', error_code: 'rate_limited', complete: false },
    ] },
    local_voice: { keys_scanned: 0, retired: 0, status: 'unsupported', reason: 'keyless', results: [] },
  } } }).mockResolvedValueOnce({ success: true, data: { id: 'run-2', status: 'complete', providers: {
    acme: { keys_scanned: 2, retired: 1, status: 'complete', reason: null, results: [
      { key_id: 'key-1', status: 'complete', access_scope: 'credential', error_code: null, complete: true },
      { key_id: 'key-2', status: 'complete', access_scope: 'credential', error_code: null, complete: true },
    ] },
  } } });
  render(<KeyPool />);
  await screen.findByRole('button', { name: /Acme Voice/ });
  fireEvent.click(screen.getByRole('button', { name: /Cập nhật Models/ }));
  expect(await screen.findByText(/Acme Voice.*partial/i)).toBeTruthy();
  expect(screen.getByText(/Local Voice.*unsupported/i)).toBeTruthy();
  expect(screen.getByText(/Acme Voice.*2 keys scanned/i)).toBeTruthy();
  expect(document.body.textContent).not.toMatch(/đã dọn|đã xóa model/i);
  fireEvent.click(screen.getByRole('button', { name: /Cập nhật Models/ }));
  expect(await screen.findByText(/Acme Voice.*complete.*1 models đã được dọn/i)).toBeTruthy();
});

it('reports empty and failed provider/key loads honestly', async () => {
  aiApi.listProviders.mockResolvedValueOnce({ success: true, data: [] });
  const first = render(<KeyPool />);
  expect(await screen.findByText(/Chưa có nhà cung cấp AI/)).toBeTruthy();
  first.unmount();
  aiApi.listProviders.mockRejectedValueOnce(new Error('synthetic-secret-private'));
  render(<KeyPool />);
  expect(await screen.findByRole('alert')).toBeTruthy();
  expect(document.body.textContent).not.toContain('synthetic-secret-private');
});

it('reports a key list failure without showing stale keys or backend text', async () => {
  aiApi.listKeys.mockRejectedValueOnce(new Error('synthetic-secret-private'));
  render(<KeyPool />);
  expect(await screen.findByText('Không thể tải Key Pool.')).toBeTruthy();
  expect(screen.queryByText('****ABCD')).toBeNull();
  expect(document.body.textContent).not.toContain('synthetic-secret-private');
});

it('uses a fixed safe message when explicit refresh fails', async () => {
  aiApi.refreshModels.mockRejectedValueOnce(new Error('synthetic-secret-private'));
  render(<KeyPool />);
  await screen.findByRole('button', { name: /Acme Voice/ });
  fireEvent.click(screen.getByRole('button', { name: /Cập nhật Models/ }));
  expect(await screen.findByRole('alert')).toBeTruthy();
  expect(document.body.textContent).not.toContain('synthetic-secret-private');
});

it('does not let an add for a previous provider replace the selected keys or clear its draft', async () => {
  let finishAdd;
  aiApi.listProviders.mockResolvedValue({ success: true, data: [providers[0], {
    ...providers[0], id: 'beta', name: 'Beta Voice', enabled_key_count: 1,
  }] });
  aiApi.listKeys.mockImplementation(async id => ({ success: true, data: id === 'beta'
    ? [{ ...key, id: 'beta-key', provider_id: 'beta', masked_key: '****BETA' }] : [key] }));
  aiApi.addKey.mockReturnValue(new Promise(resolve => { finishAdd = resolve; }));
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-A-secret' } });
  fireEvent.click(screen.getByRole('button', { name: 'Lưu Key' }));
  fireEvent.click(screen.getByRole('button', { name: /Beta Voice/ }));
  await screen.findByText('****BETA');
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-B-draft' } });
  await act(async () => finishAdd({ success: true, data: { key: { ...key, enabled: false },
    discovery: { status: 'partial', access_scope: 'unknown', error_code: 'rate_limited', verified_for_generation: false } } }));
  expect(screen.getByText('****BETA')).toBeTruthy();
  expect(screen.queryByText('****ABCD')).toBeNull();
  expect(screen.getByLabelText('API Key').value).toBe('synthetic-B-draft');
  expect(screen.queryByText(/Đã thêm Key/)).toBeNull();
});

it('keeps an add result when the selected provider tile is clicked again', async () => {
  let finishAdd;
  aiApi.addKey.mockReturnValue(new Promise(resolve => { finishAdd = resolve; }));
  aiApi.listKeys.mockResolvedValueOnce({ success: true, data: [key] }).mockResolvedValue({ success: true, data: [key, {
    ...key, id: 'key-2', masked_key: '****NEW2', enabled: false,
  }] });
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-A-secret' } });
  fireEvent.click(screen.getByRole('button', { name: 'Lưu Key' }));
  fireEvent.click(screen.getByRole('button', { name: /Acme Voice/ }));
  await act(async () => finishAdd({ success: true, data: { key: { ...key, id: 'key-2', enabled: false },
    discovery: { status: 'partial', access_scope: 'unknown', error_code: 'rate_limited', verified_for_generation: false } } }));
  expect(await screen.findByText('****NEW2')).toBeTruthy();
});

it.each(['toggle', 'delete'])('does not let a previous provider %s completion change the selected view', async action => {
  let finish;
  aiApi.listProviders.mockResolvedValue({ success: true, data: [providers[0], {
    ...providers[0], id: 'beta', name: 'Beta Voice', enabled_key_count: 1,
  }] });
  aiApi.listKeys.mockImplementation(async id => ({ success: true, data: id === 'beta'
    ? [{ ...key, id: 'beta-key', provider_id: 'beta', masked_key: '****BETA' }] : [key] }));
  const pending = new Promise(resolve => { finish = resolve; });
  if (action === 'toggle') aiApi.setKeyEnabled.mockReturnValue(pending);
  else {
    aiApi.deleteKey.mockReturnValue(pending);
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  }
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: action === 'toggle' ? 'Tắt Key' : 'Xóa Key' }));
  fireEvent.click(screen.getByRole('button', { name: /Beta Voice/ }));
  await screen.findByText('****BETA');
  await act(async () => finish(action === 'toggle'
    ? { success: true, data: { key: { ...key, enabled: false }, discovery: { status: 'disabled' } } }
    : { success: true, data: { deleted: true } }));
  expect(screen.getByText('****BETA')).toBeTruthy();
  expect(screen.queryByText('****ABCD')).toBeNull();
  expect(screen.queryByText(/Key đã tắt|Đã xóa Key/)).toBeNull();
});

it('does not let an old refresh completion replace a later provider view', async () => {
  let finishRefresh;
  aiApi.refreshModels.mockReturnValue(new Promise(resolve => { finishRefresh = resolve; }));
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: /Cập nhật Models/ }));
  fireEvent.click(screen.getByRole('button', { name: /Local Voice/ }));
  await screen.findByText(/Không cần API key/);
  await act(async () => finishRefresh({ success: true, data: { id: 'run-old', status: 'complete', providers: {
    acme: { keys_scanned: 1, retired: 0, status: 'complete', reason: null, results: [] },
  } } }));
  expect(screen.queryByText(/Cập nhật Models: complete/)).toBeNull();
});

it('reconciles a completed add after A→B→A without replacing the new draft or accepting an older list', async () => {
  let finishAdd;
  let finishOldList;
  let acmeLoads = 0;
  aiApi.listProviders.mockResolvedValue({ success: true, data: [providers[0], {
    ...providers[0], id: 'beta', name: 'Beta Voice', enabled_key_count: 1,
  }] });
  aiApi.listKeys.mockImplementation(id => {
    if (id === 'beta') return Promise.resolve({ success: true, data: [{
      ...key, id: 'beta-key', provider_id: 'beta', masked_key: '****BETA',
    }] });
    acmeLoads += 1;
    if (acmeLoads === 1) return Promise.resolve({ success: true, data: [key] });
    if (acmeLoads === 2) return new Promise(resolve => { finishOldList = resolve; });
    return Promise.resolve({ success: true, data: [key, {
      ...key, id: 'new-key', masked_key: '****NEW2', enabled: false,
    }] });
  });
  aiApi.addKey.mockReturnValue(new Promise(resolve => { finishAdd = resolve; }));
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-old-secret' } });
  fireEvent.click(screen.getByRole('button', { name: 'Lưu Key' }));
  fireEvent.click(screen.getByRole('button', { name: /Beta Voice/ }));
  await screen.findByText('****BETA');
  fireEvent.click(screen.getByRole('button', { name: /Acme Voice/ }));
  await screen.findByText('Đang tải Key Pool…');
  fireEvent.click(screen.getByRole('button', { name: /Thêm Key/ }));
  fireEvent.change(screen.getByLabelText('API Key'), { target: { value: 'synthetic-new-draft' } });
  await act(async () => finishAdd({ success: true, data: { key: {
    ...key, id: 'new-key', masked_key: '****NEW2', enabled: false,
  }, discovery: { status: 'partial', access_scope: 'unknown', error_code: 'rate_limited', verified_for_generation: false } } }));
  expect(await screen.findByText('****NEW2')).toBeTruthy();
  expect(screen.getByLabelText('API Key').value).toBe('synthetic-new-draft');
  expect(screen.queryByText(/Đã thêm Key/)).toBeNull();
  await act(async () => finishOldList({ success: true, data: [key] }));
  expect(screen.getByText('****NEW2')).toBeTruthy();
});

it('reconciles a completed toggle after A→B→A without showing its old notice', async () => {
  let finishToggle;
  let acmeEnabled = true;
  aiApi.listProviders.mockResolvedValue({ success: true, data: [providers[0], {
    ...providers[0], id: 'beta', name: 'Beta Voice', enabled_key_count: 1,
  }] });
  aiApi.listKeys.mockImplementation(async id => ({ success: true, data: id === 'beta'
    ? [{ ...key, id: 'beta-key', provider_id: 'beta', masked_key: '****BETA' }]
    : [{ ...key, enabled: acmeEnabled }] }));
  aiApi.setKeyEnabled.mockReturnValue(new Promise(resolve => { finishToggle = resolve; }));
  render(<KeyPool />);
  await screen.findByText('****ABCD');
  fireEvent.click(screen.getByRole('button', { name: 'Tắt Key' }));
  fireEvent.click(screen.getByRole('button', { name: /Beta Voice/ }));
  await screen.findByText('****BETA');
  fireEvent.click(screen.getByRole('button', { name: /Acme Voice/ }));
  await screen.findByText('****ABCD');
  acmeEnabled = false;
  await act(async () => finishToggle({ success: true, data: {
    key: { ...key, enabled: false }, discovery: { status: 'disabled' },
  } }));
  expect(await screen.findByRole('button', { name: 'Bật Key' })).toBeTruthy();
  expect(screen.queryByText('Key đã tắt.')).toBeNull();
});
