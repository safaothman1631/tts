import { apiClient } from './client';
import {
  getErrorStatus,
  isCooldownActive,
  isEndpointUnavailableStatus,
  markCooldown,
  parseBooleanEnv,
} from './fallback';
import { getCachedVoice, getCachedVoices, saveCachedVoice, saveCachedVoices } from '@/lib/offline-storage';
import {
  CapabilitiesSchema,
  HealthSchema,
  NlpAnalysisSchema,
  SynthRequestSchema,
  SynthResponseSchema,
  SynthSegmentsRequestSchema,
  VoiceCharactersPageSchema,
  VoiceCharacterSchema,
  VoiceSchema,
  type Capabilities,
  type Health,
  type NlpAnalysis,
  type SynthRequest,
  type SynthResponse,
  type SynthSegment,
  type SynthSegmentsRequest,
  type Voice,
  type VoiceCharacter,
  type VoiceCharactersPage,
} from '@/types/api';
import { z } from 'zod';

const c = () => apiClient();

/** Map UI tier to backend acoustic tier. draft = fastest piper, studio = highest quality qwen3. */
function mapTier(t: SynthRequest['tier']): string {
  switch (t) {
    case 'draft': return 'piper';
    case 'studio': return 'qwen3';
    default: return 'piper';
  }
}

/** Translate UI request → backend `SynthesizeRequest`. */
function toBackendBody(req: SynthRequest): Record<string, unknown> {
  return {
    text: req.text,
    voice: req.voice_id,
    tier: mapTier(req.tier),
    speed: req.speed,
    pitch_shift: req.pitch,
    volume: req.volume,
    format: 'wav',
    ssml: req.ssml,
    style_prompt: req.style_prompt?.trim() || undefined,
    language: req.language || undefined,
    qwen_speaker: req.qwen_speaker || undefined,
    emotion: req.emotion || undefined,
    voice_character: req.voice_character || undefined,
  };
}

function toBackendSegment(segment: SynthSegment): Record<string, unknown> {
  return {
    text: segment.text,
    voice: segment.voice_id,
    tier: mapTier(segment.tier),
    speed: segment.speed,
    pitch_shift: segment.pitch,
    volume: segment.volume,
    style_prompt: segment.style_prompt?.trim() || undefined,
    pause_after_ms: segment.pause_after_ms,
    language: segment.language || undefined,
    qwen_speaker: segment.qwen_speaker || undefined,
    emotion: segment.emotion || undefined,
    voice_character: segment.voice_character || undefined,
  };
}

/* ------------------------------------------------------------------ Health */

export async function getHealth(): Promise<Health> {
  try {
    const { data } = await c().get('/v1/health');
    return HealthSchema.parse(data);
  } catch {
    return { status: 'down' };
  }
}

export async function getCapabilities(): Promise<Capabilities> {
  try {
    const { data } = await c().get('/v1/capabilities');
    return CapabilitiesSchema.parse(data);
  } catch {
    return CapabilitiesSchema.parse({
      languages: ['en'],
      formats: ['wav'],
      tiers: ['piper', 'legacy'],
      controls: ['voice', 'speed', 'pitch_shift', 'volume', 'ssml'],
      endpoints: ['/v1/health', '/v1/voices', '/v1/synthesize', '/v1/synthesize.wav'],
      voice_clone: false,
      streaming: false,
      custom_voice_persistence: false,
      qwen_speakers: [],
      emotions: [],
      style_presets: [],
      voice_characters_total: 0,
    });
  }
}

/* ------------------------------------------------------------ Voice Characters */

export interface VoiceCharacterQuery {
  language?: string;
  gender?: string;
  persona?: string;
  category?: string;
  accent?: string;
  age_range?: string;
  q?: string;
  limit?: number;
  offset?: number;
}

export async function listVoiceCharacters(
  query: VoiceCharacterQuery = {},
): Promise<VoiceCharactersPage> {
  const params: Record<string, string | number> = {};
  if (query.language) params.language = query.language;
  if (query.gender) params.gender = query.gender;
  if (query.persona) params.persona = query.persona;
  if (query.category) params.category = query.category;
  if (query.accent) params.accent = query.accent;
  if (query.age_range) params.age_range = query.age_range;
  if (query.q) params.q = query.q;
  params.limit = query.limit ?? 60;
  params.offset = query.offset ?? 0;
  const { data } = await c().get('/v1/voice-characters', { params });
  return VoiceCharactersPageSchema.parse(data);
}

export async function getVoiceCharacter(id: string): Promise<VoiceCharacter> {
  const { data } = await c().get(`/v1/voice-characters/${encodeURIComponent(id)}`);
  return VoiceCharacterSchema.parse(data);
}

export async function listPersonas(): Promise<{ id: string; label: string; default_emotion: string; tags: string[] }[]> {
  const { data } = await c().get('/v1/personas');
  return Array.isArray(data) ? data : [];
}

export async function listVoiceCategories(): Promise<{ id: string; label: string }[]> {
  try {
    const { data } = await c().get('/v1/voice-categories');
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

/* ------------------------------------------------------------------ Voices */

export async function listVoices(): Promise<Voice[]> {
  try {
    const { data } = await c().get('/v1/voices');
    const voices = z.array(VoiceSchema).parse(data?.voices ?? data ?? []);
    await saveCachedVoices(voices);
    return voices;
  } catch (e) {
    const cached = await getCachedVoices();
    if (cached.length) return cached;
    throw e;
  }
}

export async function getVoice(id: string): Promise<Voice> {
  try {
    const { data } = await c().get(`/v1/voices/${encodeURIComponent(id)}`);
    const voice = VoiceSchema.parse(data);
    await saveCachedVoice(voice);
    return voice;
  } catch (e) {
    const cached = await getCachedVoice(id);
    if (cached) return cached;
    throw e;
  }
}

export async function deleteVoice(id: string): Promise<void> {
  await c().delete(`/v1/voices/${encodeURIComponent(id)}`);
}

export interface CloneVoicePayload {
  name: string;
  description?: string;
  audioBlob: Blob;
  consent: boolean;
  language?: string;
  referenceText?: string;
  gender?: string;
}

const CLONE_UNAVAILABLE_KEY = 'tts.cloneEndpointUnavailableUntil';
const CLONE_UNAVAILABLE_TTL_MS = 60 * 60 * 1000; // 1 hour
const CLONE_ENDPOINT_ENABLED = parseBooleanEnv(import.meta.env.VITE_ENABLE_VOICE_CLONE_ENDPOINT, true);

/**
 * Voice cloning. The backend may not yet expose `/v1/voices/clone`; in that
 * case (or any error during upload) we transparently fall back to a local
 * descriptor so the wizard can still complete and show a recorded voice.
 * 
 * Returns { voice, isLocal } to help UI differentiate between uploaded vs fallback.
 */
export async function cloneVoice(payload: CloneVoicePayload): Promise<{ voice: Voice; isLocal: boolean }> {
  const localFallback = (): Voice =>
    VoiceSchema.parse({
      id: `local-${Date.now()}`,
      name: payload.name,
      gender: 'neutral',
      accent: 'custom',
      backend: 'local',
      model: 'recording',
      custom: true,
    });

  if (!CLONE_ENDPOINT_ENABLED) {
    const voice = localFallback();
    await saveCachedVoice(voice);
    return { voice, isLocal: true };
  }

  const fd = new FormData();
  const recording = await prepareCloneRecording(payload.audioBlob);
  fd.append('name', payload.name);
  if (payload.description) fd.append('description', payload.description);
  fd.append('consent', String(payload.consent));
  fd.append('audio', recording.blob, recording.filename);
  if (payload.language) fd.append('language', payload.language);
  if (payload.referenceText) fd.append('reference_text', payload.referenceText);
  if (payload.gender) fd.append('gender', payload.gender);

  if (isCooldownActive(CLONE_UNAVAILABLE_KEY)) {
    const voice = localFallback();
    await saveCachedVoice(voice);
    return { voice, isLocal: true };
  }

  try {
    const { data } = await c().post('/v1/voices/clone', fd);
    const voice = VoiceSchema.parse(data);
    await saveCachedVoice(voice);
    return { voice, isLocal: false };
  } catch (e) {
    // Backend clone endpoint unavailable or failed; use local fallback
    // This allows the wizard to complete and show recorded voice in voice list.
    const status = getErrorStatus(e);
    if (isEndpointUnavailableStatus(status)) {
      markCooldown(CLONE_UNAVAILABLE_KEY, CLONE_UNAVAILABLE_TTL_MS);
    }
    const voice = localFallback();
    await saveCachedVoice(voice);
    // Optionally log the upstream error for debugging
    console.debug('Clone endpoint unavailable, using local fallback:', (e as { message?: string })?.message);
    return { voice, isLocal: true };
  }
}

/* ------------------------------------------------------------------ Synth  */

export async function synthesize(req: SynthRequest): Promise<{ blob: Blob; meta: SynthResponse }> {
  const body = SynthRequestSchema.parse(req);
  const backend = toBackendBody(body);
  const res = await c().post('/v1/synthesize.wav', backend, {
    responseType: 'blob',
    headers: { Accept: 'audio/wav,application/octet-stream,application/json' },
  });
  const contentType = String(res.headers['content-type'] ?? '').toLowerCase();
  const raw = res.data as Blob;
  if (res.status === 204 || raw.size === 0) {
    return await synthesizeViaJsonFallback(backend);
  }
  if (contentType.includes('application/json')) {
    const text = await raw.text();
    throw { status: res.status, message: text || 'Synthesis did not return audio.' };
  }
  const blob = contentType.includes('audio/') ? raw : new Blob([raw], { type: 'audio/wav' });
  const wavOk = await isWavBlob(blob);
  if (!wavOk) {
    const preview = await safeBlobPreview(raw);
    throw {
      status: res.status,
      message: preview || 'Synthesis response is not a valid WAV audio payload.',
    };
  }
  const meta = SynthResponseSchema.parse({
    id: res.headers['x-request-id'] || crypto.randomUUID(),
    format: 'wav',
    bytes: blob.size,
    sample_rate: Number(res.headers['x-sample-rate']) || undefined,
    duration_seconds: Number(res.headers['x-duration-seconds']) || undefined,
  });
  return { blob, meta };
}

export async function synthesizeSegments(req: SynthSegmentsRequest): Promise<{ blob: Blob; meta: SynthResponse }> {
  const body = SynthSegmentsRequestSchema.parse(req);
  const backend = {
    format: 'wav',
    segments: body.segments.map(toBackendSegment),
  };
  const res = await c().post('/v1/synthesize/segments.wav', backend, {
    responseType: 'blob',
    headers: { Accept: 'audio/wav,application/octet-stream,application/json' },
  });
  const contentType = String(res.headers['content-type'] ?? '').toLowerCase();
  const raw = res.data as Blob;
  if (res.status === 204 || raw.size === 0) {
    return await synthesizeSegmentsViaJsonFallback(backend);
  }
  if (contentType.includes('application/json')) {
    const text = await raw.text();
    throw { status: res.status, message: text || 'Segment synthesis did not return audio.' };
  }
  const blob = contentType.includes('audio/') ? raw : new Blob([raw], { type: 'audio/wav' });
  const wavOk = await isWavBlob(blob);
  if (!wavOk) {
    const preview = await safeBlobPreview(raw);
    throw {
      status: res.status,
      message: preview || 'Segment synthesis response is not a valid WAV audio payload.',
    };
  }
  const meta = SynthResponseSchema.parse({
    id: res.headers['x-request-id'] || crypto.randomUUID(),
    format: 'wav',
    bytes: blob.size,
    sample_rate: Number(res.headers['x-sample-rate']) || undefined,
    duration_seconds: Number(res.headers['x-duration-seconds']) || undefined,
    metadata: { segments: Number(res.headers['x-segments']) || body.segments.length },
  });
  return { blob, meta };
}

async function synthesizeSegmentsViaJsonFallback(
  backend: Record<string, unknown>,
): Promise<{ blob: Blob; meta: SynthResponse }> {
  const { data } = await c().post('/v1/synthesize/segments', backend);
  const sampleRate = Number(data?.sample_rate) || undefined;
  const durationSeconds = Number(data?.duration_seconds) || undefined;
  const audioBase64 = String(data?.audio_base64 ?? '');
  if (!audioBase64) {
    throw { status: 204, message: 'Segment synthesis returned no audio payload.' };
  }

  const bytes = Uint8Array.from(atob(audioBase64), (ch) => ch.charCodeAt(0));
  const blob = new Blob([bytes], { type: 'audio/wav' });
  const wavOk = await isWavBlob(blob);
  if (!wavOk) {
    throw { status: 500, message: 'Fallback segment synthesis payload is not valid WAV audio.' };
  }

  const meta = SynthResponseSchema.parse({
    id: crypto.randomUUID(),
    format: 'wav',
    bytes: blob.size,
    sample_rate: sampleRate,
    duration_seconds: durationSeconds,
  });
  return { blob, meta };
}

async function synthesizeViaJsonFallback(backend: Record<string, unknown>): Promise<{ blob: Blob; meta: SynthResponse }> {
  const { data } = await c().post('/v1/synthesize', backend);
  const sampleRate = Number(data?.sample_rate) || undefined;
  const durationSeconds = Number(data?.duration_seconds) || undefined;
  const audioBase64 = String(data?.audio_base64 ?? '');
  if (!audioBase64) {
    throw { status: 204, message: 'Synthesis returned no audio payload.' };
  }

  const bytes = Uint8Array.from(atob(audioBase64), (ch) => ch.charCodeAt(0));
  const blob = new Blob([bytes], { type: 'audio/wav' });
  const wavOk = await isWavBlob(blob);
  if (!wavOk) {
    throw { status: 500, message: 'Fallback synthesis payload is not valid WAV audio.' };
  }

  const meta = SynthResponseSchema.parse({
    id: crypto.randomUUID(),
    format: 'wav',
    bytes: blob.size,
    sample_rate: sampleRate,
    duration_seconds: durationSeconds,
  });
  return { blob, meta };
}

/**
 * Download synthesis with the Fetch streams API so progress can update without
 * concatenating multiple standalone WAV files into one invalid blob.
 */
export async function streamSynthesize(
  req: SynthRequest,
  onChunk?: (chunk: Uint8Array, totalBytes: number) => void,
  signal?: AbortSignal,
): Promise<{ blob: Blob; bytes: number }> {
  const body = toBackendBody(SynthRequestSchema.parse(req));
  const url = `${c().defaults.baseURL ?? ''}/v1/stream`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'audio/wav' },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) throw { status: res.status, message: `Stream failed: ${res.status}` };
  const reader = res.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value) {
      chunks.push(value);
      total += value.byteLength;
      onChunk?.(value, total);
    }
  }
  const blob = new Blob(chunks as BlobPart[], { type: 'audio/wav' });
  const wavOk = await isWavBlob(blob);
  if (!wavOk) {
    const preview = await safeBlobPreview(blob);
    throw { status: res.status, message: preview || 'Stream response is not valid WAV audio.' };
  }
  return { blob, bytes: total };
}

async function isWavBlob(blob: Blob): Promise<boolean> {
  if (!blob || blob.size < 12) return false;
  const bytes = new Uint8Array(await blob.slice(0, 12).arrayBuffer());
  const sig = String.fromCharCode(...bytes.slice(0, 4));
  const fmt = String.fromCharCode(...bytes.slice(8, 12));
  return sig === 'RIFF' && fmt === 'WAVE';
}

async function prepareCloneRecording(blob: Blob): Promise<{ blob: Blob; filename: string }> {
  if (await isWavBlob(blob)) return { blob: new Blob([blob], { type: 'audio/wav' }), filename: 'recording.wav' };

  const converted = await convertAudioBlobToWav(blob).catch(() => null);
  if (converted) return { blob: converted, filename: 'recording.wav' };

  const ext = blob.type.includes('webm') ? 'webm' : blob.type.includes('ogg') ? 'ogg' : blob.type.includes('mpeg') ? 'mp3' : 'bin';
  return { blob, filename: `recording.${ext}` };
}

async function convertAudioBlobToWav(blob: Blob): Promise<Blob> {
  const AudioContextCtor = window.AudioContext
    ?? (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioContextCtor) throw new Error('AudioContext is not available.');

  const context = new AudioContextCtor();
  try {
    const audioBuffer = await context.decodeAudioData(await blob.arrayBuffer());
    const channel = new Float32Array(audioBuffer.length);
    audioBuffer.copyFromChannel(channel, 0);
    return new Blob([encodeMonoWav(channel, audioBuffer.sampleRate)], { type: 'audio/wav' });
  } finally {
    await context.close().catch(() => undefined);
  }
}

function encodeMonoWav(samples: Float32Array, sampleRate: number): ArrayBuffer {
  const bytesPerSample = 2;
  const dataSize = samples.length * bytesPerSample;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  writeAscii(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataSize, true);
  writeAscii(view, 8, 'WAVE');
  writeAscii(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * bytesPerSample, true);
  view.setUint16(32, bytesPerSample, true);
  view.setUint16(34, 16, true);
  writeAscii(view, 36, 'data');
  view.setUint32(40, dataSize, true);

  let offset = 44;
  for (const sample of samples) {
    const clamped = Math.max(-1, Math.min(1, sample));
    view.setInt16(offset, clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff, true);
    offset += bytesPerSample;
  }
  return buffer;
}

function writeAscii(view: DataView, offset: number, value: string): void {
  for (let i = 0; i < value.length; i += 1) {
    view.setUint8(offset + i, value.charCodeAt(i));
  }
}

async function safeBlobPreview(blob: Blob): Promise<string> {
  try {
    return (await blob.text()).slice(0, 240);
  } catch {
    return '';
  }
}

/* ------------------------------------------------------------------ NLP    */

export async function analyzeText(text: string): Promise<NlpAnalysis> {
  try {
    const { data } = await c().post('/v1/analyze', { text });
    return NlpAnalysisSchema.parse(data);
  } catch (e) {
    const status = getErrorStatus(e);
    if (isEndpointUnavailableStatus(status)) {
      // Local fallback: simple tokenization so the Analyzer page is still useful.
      const tokens = text
        .split(/\s+/)
        .filter(Boolean)
        .map((w) => ({ text: w, type: /[.!?,;:]/.test(w) ? 'punct' : 'word' }));
      return NlpAnalysisSchema.parse({ tokens });
    }
    throw e;
  }
}

/* ------------------------------------------------------------------ SSML   */

export async function validateSsml(ssml: string): Promise<{ valid: boolean; errors: string[] }> {
  try {
    const { data } = await c().post('/v1/ssml/validate', { ssml });
    return { valid: !!data?.valid, errors: data?.errors ?? [] };
  } catch (e) {
    const status = getErrorStatus(e);
    if (isEndpointUnavailableStatus(status)) {
      // Minimal local check: tags should be balanced.
      const open = (ssml.match(/<[a-z][^/>]*?>/gi) ?? []).length;
      const close = (ssml.match(/<\/[a-z][^>]*?>/gi) ?? []).length;
      const selfClose = (ssml.match(/<[a-z][^>]*?\/>/gi) ?? []).length;
      const ok = open === close + selfClose;
      return { valid: ok, errors: ok ? [] : ['Unbalanced tags (local check)'] };
    }
    return { valid: false, errors: [(e as { message?: string }).message ?? 'Validation failed'] };
  }
}

