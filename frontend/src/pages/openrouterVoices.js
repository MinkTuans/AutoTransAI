export async function loadOpenRouterVoices(aiApi) {
  const functions = await aiApi.listFunctions();
  const tts = functions?.success && Array.isArray(functions.data)
    ? functions.data.find(row => row.function_id === 'tts') : null;
  if (!tts?.selectable || tts.primary_provider_id !== 'openrouter' || !tts.model_id) return null;

  const response = await aiApi.getModel(tts.model_id);
  const model = response?.success ? response.data : null;
  const candidates = model?.metadata?.supported_voices;
  if (model?.id !== tts.model_id || model.provider_id !== 'openrouter' || model.status !== 'active'
      || !Array.isArray(candidates)) return null;
  const ids = [...new Set(candidates.filter(id => typeof id === 'string' && id.length > 0 && id.length <= 100
    && id === id.trim() && !/[\u0000-\u001f\u007f]/.test(id)))];
  if (!ids.length) return null;
  return { modelId: model.id, modelName: model.display_name || model.remote_model_id || model.id,
    voices: ids.map(id => ({ id, name: id, language: '', gender: '' })) };
}
