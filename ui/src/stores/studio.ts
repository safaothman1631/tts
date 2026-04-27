import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { SynthRequest, SynthSegment, SynthSegmentsRequest } from '@/types/api';
import { config } from '@/lib/config';

function segmentId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `segment-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function createSegment(overrides: Partial<SynthSegment> = {}): SynthSegment {
  return {
    id: segmentId(),
    text: '',
    tier: 'draft',
    speed: 1,
    pitch: 0,
    volume: 1,
    pause_after_ms: 120,
    ...overrides,
  };
}

interface StudioState {
  text: string;
  ssmlMode: boolean;
  segmentsMode: boolean;
  segments: SynthSegment[];
  voiceId?: string;
  format: SynthRequest['format'];
  tier: SynthRequest['tier'];
  speed: number;
  pitch: number;
  volume: number;
  stylePrompt: string;
  language?: string;
  qwenSpeaker?: string;
  emotion?: string;
  voiceCharacter?: string;
  isPlaying: boolean;
  isSynthesizing: boolean;
  currentAudioUrl?: string;
  currentAudioBlob?: Blob;
  currentDuration?: number;
  /** Streaming progress 0..1 (undefined when not streaming). */
  streamProgress?: number;
  /** A/B compare: alternative take that the user can flip to. */
  compareUrl?: string;
  compareBlob?: Blob;
  compareLabel?: string;
  setText(text: string): void;
  setSsmlMode(v: boolean): void;
  setSegmentsMode(v: boolean): void;
  addSegment(afterId?: string): void;
  removeSegment(id: string): void;
  updateSegment(id: string, patch: Partial<Omit<SynthSegment, 'id'>>): void;
  setVoice(id?: string): void;
  setFormat(f: SynthRequest['format']): void;
  setTier(t: SynthRequest['tier']): void;
  setSpeed(v: number): void;
  setPitch(v: number): void;
  setVolume(v: number): void;
  setStylePrompt(v: string): void;
  setLanguage(v?: string): void;
  setQwenSpeaker(v?: string): void;
  setEmotion(v?: string): void;
  setVoiceCharacter(v?: string): void;
  setPlaying(v: boolean): void;
  setSynthesizing(v: boolean): void;
  setAudio(url?: string, durationSeconds?: number, blob?: Blob): void;
  setStreamProgress(p?: number): void;
  setCompare(url?: string, label?: string, blob?: Blob): void;
  swapAB(): void;
  buildRequest(): SynthRequest;
  buildSegmentsRequest(): SynthSegmentsRequest;
  reset(): void;
}

const initial = {
  text: '',
  ssmlMode: false,
  segmentsMode: false,
  segments: [createSegment()],
  format: 'wav' as const,
  tier: 'draft' as const,
  speed: 1,
  pitch: 0,
  volume: 1,
  stylePrompt: '',
  language: undefined as string | undefined,
  qwenSpeaker: undefined as string | undefined,
  emotion: undefined as string | undefined,
  voiceCharacter: undefined as string | undefined,
  isPlaying: false,
  isSynthesizing: false,
};

export const useStudioStore = create<StudioState>()(
  persist(
    immer((set, get) => ({
      ...initial,
      setText: (text) => set((s) => void (s.text = text)),
      setSsmlMode: (v) => set((s) => void (s.ssmlMode = v)),
      setSegmentsMode: (v) =>
        set((s) => {
          s.segmentsMode = v;
          if (v && s.segments.every((segment) => !segment.text.trim())) {
            s.segments = [createSegment({ text: s.text, voice_id: s.voiceId, tier: s.tier, speed: s.speed, pitch: s.pitch, volume: s.volume })];
          }
        }),
      addSegment: (afterId) =>
        set((s) => {
          const next = createSegment({ voice_id: s.voiceId, tier: s.tier, speed: s.speed, pitch: s.pitch, volume: s.volume });
          const index = afterId ? s.segments.findIndex((segment) => segment.id === afterId) : -1;
          if (index >= 0) s.segments.splice(index + 1, 0, next);
          else s.segments.push(next);
        }),
      removeSegment: (id) =>
        set((s) => {
          if (s.segments.length <= 1) {
            s.segments[0] = createSegment({ voice_id: s.voiceId, tier: s.tier, speed: s.speed, pitch: s.pitch, volume: s.volume });
            return;
          }
          s.segments = s.segments.filter((segment) => segment.id !== id);
        }),
      updateSegment: (id, patch) =>
        set((s) => {
          const segment = s.segments.find((item) => item.id === id);
          if (!segment) return;
          Object.assign(segment, patch);
        }),
      setVoice: (id) => set((s) => void (s.voiceId = id)),
      setFormat: (f) => set((s) => void (s.format = f)),
      setTier: (t) => set((s) => void (s.tier = t)),
      setSpeed: (v) => set((s) => void (s.speed = v)),
      setPitch: (v) => set((s) => void (s.pitch = v)),
      setVolume: (v) => set((s) => void (s.volume = v)),
      setStylePrompt: (v) => set((s) => void (s.stylePrompt = v)),
      setLanguage: (v) => set((s) => void (s.language = v || undefined)),
      setQwenSpeaker: (v) => set((s) => void (s.qwenSpeaker = v || undefined)),
      setEmotion: (v) => set((s) => void (s.emotion = v || undefined)),
      setVoiceCharacter: (v) => set((s) => void (s.voiceCharacter = v || undefined)),
      setPlaying: (v) => set((s) => void (s.isPlaying = v)),
      setSynthesizing: (v) => set((s) => void (s.isSynthesizing = v)),
      setAudio: (url, durationSeconds, blob) =>
        set((s) => {
          s.currentAudioUrl = url;
          s.currentAudioBlob = blob;
          s.currentDuration = durationSeconds;
        }),
      setStreamProgress: (p) => set((s) => void (s.streamProgress = p)),
      setCompare: (url, label, blob) =>
        set((s) => {
          s.compareUrl = url;
          s.compareBlob = blob;
          s.compareLabel = label;
        }),
      swapAB: () =>
        set((s) => {
          const a = s.currentAudioUrl;
          const aBlob = s.currentAudioBlob;
          s.currentAudioUrl = s.compareUrl;
          s.currentAudioBlob = s.compareBlob;
          s.compareUrl = a;
          s.compareBlob = aBlob;
        }),
      buildRequest: () => {
        const s = get();
        return {
          text: s.text,
          voice_id: s.voiceId,
          format: s.format,
          tier: s.tier,
          speed: s.speed,
          pitch: s.pitch,
          volume: s.volume,
          ssml: s.ssmlMode,
          style_prompt: s.stylePrompt?.trim() || undefined,
          language: s.language,
          qwen_speaker: s.qwenSpeaker,
          emotion: s.emotion,
          voice_character: s.voiceCharacter,
        };
      },
      buildSegmentsRequest: () => {
        const state = get();
        const segments = state.segments
          .filter((segment) => segment.text.trim())
          .map((segment) => ({
            ...segment,
            text: segment.text.trim(),
            voice_id: segment.voice_id || state.voiceId,
          }));
        return {
          format: 'wav',
          segments: segments.length ? segments : [createSegment({ text: state.text.trim(), voice_id: state.voiceId, tier: state.tier, speed: state.speed, pitch: state.pitch, volume: state.volume })],
        };
      },
      reset: () => set(() => ({ ...initial })),
    })),
    {
      name: 'tts-studio:studio',
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        text: s.text,
        ssmlMode: s.ssmlMode,
        segmentsMode: s.segmentsMode,
        segments: s.segments,
        voiceId: s.voiceId,
        format: s.format,
        tier: s.tier,
        speed: s.speed,
        pitch: s.pitch,
        volume: s.volume,
        stylePrompt: s.stylePrompt,
        language: s.language,
        qwenSpeaker: s.qwenSpeaker,
        emotion: s.emotion,
        voiceCharacter: s.voiceCharacter,
      }),
      version: 4,
      migrate: (persisted, _fromVersion) => {
        // Re-base any older persisted state onto current defaults; keeps user
        // text/voice/format etc. but drops fields we no longer support and
        // fills in newly added optional fields with sane defaults.
        const safe = (persisted ?? {}) as Partial<StudioState>;
        return {
          ...initial,
          ...safe,
          stylePrompt: safe.stylePrompt ?? '',
          voiceCharacter: safe.voiceCharacter ?? undefined,
        } as Partial<StudioState>;
      },
    },
  ),
);

void config;
