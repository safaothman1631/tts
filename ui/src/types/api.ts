import { z } from 'zod';

export const VoiceSchema = z.object({
  id: z.string(),
  name: z.string(),
  gender: z.string().default('neutral'),
  accent: z.string().default(''),
  language: z.string().default('en'),
  backend: z.string().default('pyttsx3'),
  model: z.string().default(''),
  description: z.string().optional(),
  preview_url: z.string().optional(),
  tags: z.array(z.string()).default([]),
  custom: z.boolean().default(false),
  created_at: z.string().optional(),
  supports_clone: z.boolean().optional(),
  supports_style_prompt: z.boolean().optional(),
});
export type Voice = z.infer<typeof VoiceSchema>;

export const StylePresetSchema = z.object({
  id: z.string(),
  label: z.string(),
  prompt: z.string(),
});
export type StylePreset = z.infer<typeof StylePresetSchema>;

export const CapabilitiesSchema = z.object({
  languages: z.array(z.string()).default([]),
  formats: z.array(z.string()).default(['wav']),
  tiers: z.array(z.string()).default([]),
  controls: z.array(z.string()).default([]),
  endpoints: z.array(z.string()).default([]),
  voice_clone: z.boolean().default(false),
  streaming: z.boolean().default(false),
  custom_voice_persistence: z.boolean().default(false),
  qwen_speakers: z.array(z.string()).default([]),
  emotions: z.array(z.string()).default([]),
  style_presets: z.array(StylePresetSchema).default([]),
  voice_characters_total: z.number().optional(),
});
export type Capabilities = z.infer<typeof CapabilitiesSchema>;

export const VoiceCharacterSchema = z.object({
  id: z.string(),
  name: z.string(),
  tagline: z.string().optional().default(''),
  gender: z.string(),
  language: z.string(),
  qwen_language: z.string(),
  region: z.string(),
  accent: z.string(),
  age_range: z.string().optional().default('adult'),
  backend: z.string(),
  model: z.string(),
  speaker_id: z.string(),
  style_prompt: z.string(),
  default_emotion: z.string(),
  pitch_offset: z.number().optional().default(0),
  speed_offset: z.number().optional().default(0),
  reference_audio: z.string().nullable().optional(),
  reference_text: z.string().nullable().optional(),
  source_type: z.string().optional().default('qwen_named'),
  category: z.string().optional().default('narrator'),
  subcategory: z.string().optional().default(''),
  persona_id: z.string(),
  persona_label: z.string(),
  description: z.string(),
  tags: z.array(z.string()).default([]),
  inspiration_note: z.string().nullable().optional(),
  license: z.string().optional().default('synthetic_only'),
  source_url: z.string().nullable().optional(),
  attribution_required: z.boolean().optional().default(false),
  attribution_string: z.string().nullable().optional(),
  speaker_embedding_sha: z.string().nullable().optional(),
});
export type VoiceCharacter = z.infer<typeof VoiceCharacterSchema>;

export const VoiceCategorySchema = z.object({
  id: z.string(),
  label: z.string(),
});
export type VoiceCategory = z.infer<typeof VoiceCategorySchema>;

export const VoiceCharactersPageSchema = z.object({
  total: z.number(),
  offset: z.number(),
  limit: z.number(),
  items: z.array(VoiceCharacterSchema),
});
export type VoiceCharactersPage = z.infer<typeof VoiceCharactersPageSchema>;

/** UI-side request — gets translated to the backend `SynthesizeRequest` shape inside endpoints.ts */
export const SynthRequestSchema = z.object({
  text: z.string().min(1).max(20000),
  voice_id: z.string().optional(),
  format: z.enum(['wav', 'mp3', 'flac', 'ogg']).default('wav'),
  speed: z.number().min(0.25).max(4).default(1),
  pitch: z.number().min(-12).max(12).default(0),
  volume: z.number().min(0).max(2).default(1),
  tier: z.enum(['draft', 'standard', 'studio']).default('standard'),
  ssml: z.boolean().default(false),
  seed: z.number().int().optional(),
  style_prompt: z.string().max(500).optional(),
  language: z.string().optional(),
  qwen_speaker: z.string().optional(),
  emotion: z.string().optional(),
  voice_character: z.string().optional(),
});
export type SynthRequest = z.infer<typeof SynthRequestSchema>;

export const SynthSegmentSchema = z.object({
  id: z.string(),
  text: z.string().min(1).max(20000),
  voice_id: z.string().optional(),
  tier: z.enum(['draft', 'standard', 'studio']).default('standard'),
  speed: z.number().min(0.25).max(4).default(1),
  pitch: z.number().min(-12).max(12).default(0),
  volume: z.number().min(0).max(2).default(1),
  style_prompt: z.string().max(500).optional(),
  pause_after_ms: z.number().int().min(0).max(5000).default(120),
  language: z.string().optional(),
  qwen_speaker: z.string().optional(),
  emotion: z.string().optional(),
  voice_character: z.string().optional(),
});
export type SynthSegment = z.infer<typeof SynthSegmentSchema>;

export const SynthSegmentsRequestSchema = z.object({
  segments: z.array(SynthSegmentSchema).min(1).max(64),
  format: z.enum(['wav']).default('wav'),
});
export type SynthSegmentsRequest = z.infer<typeof SynthSegmentsRequestSchema>;

export const SynthResponseSchema = z.object({
  id: z.string(),
  audio_url: z.string().optional(),
  duration_seconds: z.number().optional(),
  sample_rate: z.number().optional(),
  format: z.string(),
  bytes: z.number().optional(),
  cached: z.boolean().optional(),
  voice: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
});
export type SynthResponse = z.infer<typeof SynthResponseSchema>;

export const HealthSchema = z.object({
  status: z.string(),
  version: z.string().optional(),
  device: z.string().optional(),
  uptime_seconds: z.number().optional(),
  backends: z.array(z.string()).optional(),
});
export type Health = z.infer<typeof HealthSchema>;

export const NlpAnalysisSchema = z.object({
  tokens: z.array(
    z.object({
      text: z.string(),
      type: z.string(),
      phonemes_arpabet: z.array(z.string()).optional(),
      phonemes_ipa: z.string().optional(),
      stress: z.array(z.number()).optional(),
    }),
  ),
  prosody: z
    .object({
      pitch_curve: z.array(z.number()),
      energy_curve: z.array(z.number()),
      duration_ms: z.number(),
    })
    .optional(),
  ssml_ast: z.unknown().optional(),
});
export type NlpAnalysis = z.infer<typeof NlpAnalysisSchema>;

export interface HistoryItem {
  id: string;
  text: string;
  voiceId?: string;
  format: string;
  durationSeconds?: number;
  createdAt: number;
  audioBlob?: Blob;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: unknown;
}
