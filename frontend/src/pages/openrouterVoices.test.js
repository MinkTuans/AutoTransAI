import { expect, it, vi } from 'vitest';
import { loadOpenRouterVoices } from './openrouterVoices';

it('loads only voice IDs from the configured OpenRouter TTS model', async () => {
  const api = {
    listFunctions: vi.fn().mockResolvedValue({ success: true, data: [
      { function_id: 'tts', primary_provider_id: 'openrouter', model_id: 'catalog-tts', selectable: true },
    ] }),
    getModel: vi.fn().mockResolvedValue({ success: true, data: {
      id: 'catalog-tts', provider_id: 'openrouter', status: 'active',
      display_name: 'Speech Model', metadata: { supported_voices: ['voice-a', 'voice-b'] },
    } }),
  };

  expect(await loadOpenRouterVoices(api)).toEqual({ modelId: 'catalog-tts', modelName: 'Speech Model',
    voices: [{ id: 'voice-a', name: 'voice-a', language: '', gender: '' },
      { id: 'voice-b', name: 'voice-b', language: '', gender: '' }] });
  expect(api.getModel).toHaveBeenCalledWith('catalog-tts');
});

it('does not offer voices when the configured model has no verified voice IDs', async () => {
  const api = {
    listFunctions: vi.fn().mockResolvedValue({ success: true, data: [
      { function_id: 'tts', primary_provider_id: 'openrouter', model_id: 'catalog-tts', selectable: true },
    ] }),
    getModel: vi.fn().mockResolvedValue({ success: true, data: {
      id: 'catalog-tts', provider_id: 'openrouter', status: 'active', metadata: { supported_voices: null },
    } }),
  };
  expect(await loadOpenRouterVoices(api)).toBeNull();
});

it('rejects voices returned for a different model or provider', async () => {
  const api = {
    listFunctions: vi.fn().mockResolvedValue({ success: true, data: [
      { function_id: 'tts', primary_provider_id: 'openrouter', model_id: 'catalog-tts', selectable: true },
    ] }),
    getModel: vi.fn().mockResolvedValue({ success: true, data: {
      id: 'another-model', provider_id: 'openrouter', status: 'active',
      metadata: { supported_voices: ['unrelated-voice'] },
    } }),
  };
  expect(await loadOpenRouterVoices(api)).toBeNull();
});
