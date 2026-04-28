import { createStore, del, get, keys, set } from 'idb-keyval';
import type { Voice } from '@/types/api';

const store = createStore('tts-studio', 'offline');
const VOICES_SNAPSHOT_KEY = 'voices:snapshot';
const VOICE_PREFIX = 'voice:';

interface VoiceSnapshot {
  updatedAt: number;
  voices: Voice[];
}

export async function saveCachedVoices(voices: Voice[]): Promise<void> {
  const snapshot: VoiceSnapshot = { updatedAt: Date.now(), voices };
  await set(VOICES_SNAPSHOT_KEY, snapshot, store);
  await Promise.all(voices.map((voice) => set(`${VOICE_PREFIX}${voice.id}`, voice, store)));
}

export async function getCachedVoices(): Promise<Voice[]> {
  const snapshot = await get<VoiceSnapshot>(VOICES_SNAPSHOT_KEY, store);
  if (snapshot?.voices?.length) return snapshot.voices;

  const allKeys = await keys(store);
  const voiceKeys = allKeys.filter((key): key is string => typeof key === 'string' && key.startsWith(VOICE_PREFIX));
  const voices = await Promise.all(voiceKeys.map((key) => get<Voice>(key, store)));
  return voices.filter((voice): voice is Voice => Boolean(voice));
}

export async function saveCachedVoice(voice: Voice): Promise<void> {
  await set(`${VOICE_PREFIX}${voice.id}`, voice, store);
  const voices = await getCachedVoices();
  const next = [voice, ...voices.filter((v) => v.id !== voice.id)];
  await set(VOICES_SNAPSHOT_KEY, { updatedAt: Date.now(), voices: next }, store);
}

export async function getCachedVoice(id: string): Promise<Voice | undefined> {
  const direct = await get<Voice>(`${VOICE_PREFIX}${id}`, store);
  if (direct) return direct;
  return (await getCachedVoices()).find((voice) => voice.id === id);
}

export async function clearCachedVoices(): Promise<void> {
  const allKeys = await keys(store);
  await Promise.all(
    allKeys
      .filter((key): key is string => typeof key === 'string' && (key === VOICES_SNAPSHOT_KEY || key.startsWith(VOICE_PREFIX)))
      .map((key) => del(key, store)),
  );
}
